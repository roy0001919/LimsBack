import pandas as pd
import requests
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime
import os
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column,Integer,String

headers = {'Content-Type': 'application/json'}

myDBname = "postgres"
my_uesrname = "postgres"
my_pwd = "roy0001919"
my_host = "192.168.11.21"
my_port = "5432"
my_tbname_1 = "reserve_sample"
my_tbname_2 = "nonreserve_sample"
my_tbname_3 = "all_sample_data"
my_tbname_4 = "report_reserve_sample"
my_tbname_5 = "back_stage_custdata"
my_tbname_6 = "back_stage_report_reserve_sample_test"

con = psycopg2.connect(database=myDBname, user=my_uesrname,password=my_pwd, host=my_host, port=my_port)
engine = create_engine('postgresql://'+my_uesrname+':'+my_pwd+'@'+my_host+':'+my_port+'/'+myDBname, echo=False, encoding="utf-8")
# DBSession = sessionmaker(bind=engine)
# #创建session对象
# session = DBSession()
#
# Base = declarative_base()

# class Data(Base):
#     #表的名字：
#     __tablename__ = 'back_stage_report_reserve_sample_test'
#
#     #表的结构:
#     ContactID = Column(String(250),primary_key=True)
#     Name = Column(String(250))
#     Client_uuid = Column(String(250))
#     Contact_uuid = Column(String(250))
#     Sample_uuid = Column(String(250))
#     ClientName = Column(String(250))
#     Sample_id = Column(String(250))
#     PID = Column(String(250))


def login():
    loginurl = "http://3.139.254.61:8080/senaite/@@API/senaite/v1/login?__ac_name=admin&__ac_password=admin"
    reslogin = requests.get(loginurl)
    return reslogin


reslogin = login()


def create_nocontact_barcode(**barcode_dict):
    sql_cmd = 'select * from public."back_stage_custdata"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    df_export = pd.DataFrame()
    client_uuid_list = []
    sampleID_list = []
    sample_uuid_list = []
    clientName_list = []
    clientName = barcode_dict["clientName"]
    number = int(barcode_dict["number"])
    # 確認是新客還是舊客
    if clientName in df_id.ClientName.values.tolist():
        client_uuid = df_id.loc[df_id.ClientName == clientName, 'Client_uuid'].values[0]
        for i in range(0, number):
            url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid,
                                                                                    "fb874dfd7ef3481aa6b91f01a38e137c",
                                                                                    '72ee86eeed68455fbcbf05ce7d7e1d8a',
                                                                                    None,
                                                                                    None, True,
                                                                                    None)
            print(url)
            result = requests.post(url, cookies=reslogin.cookies, headers=headers)
            print(result.json())
            sampleID_list.append(result.json()["items"][0]["id"])
            sample_uuid_list.append(result.json()["items"][0]["uid"])
            client_uuid_list.append(result.json()["items"][0]["parent_uid"])
            clientName_list.append(clientName)
    else:
        url = 'http://192.168.11.21/api/client/{}/{}'.format(clientName, None)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        print(result.json())
        # clientName = result.json()["items"][0]["Name"]
        client_uuid = result.json()["items"][0]["uid"]
        for i in range(0, number):
            url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid,
                                                                                    "fb874dfd7ef3481aa6b91f01a38e137c",
                                                                                    '72ee86eeed68455fbcbf05ce7d7e1d8a',
                                                                                    None,
                                                                                    None, True,
                                                                                    None)
            print(url)
            result = requests.post(url, cookies=reslogin.cookies, headers=headers)
            sampleID_list.append(result.json()["items"][0]["id"])
            sample_uuid_list.append(result.json()["items"][0]["uid"])
            client_uuid_list.append(result.json()["items"][0]["parent_uid"])
            clientName_list.append(clientName)
    df_export["ClientName"] = clientName_list
    df_export["Client_uuid"] = client_uuid_list
    df_export["Sample_id"] = sampleID_list
    df_export["Sample_uuid"] = sample_uuid_list
    print(df_export)
    df_export.to_sql(name=my_tbname_5, con=engine, if_exists='append', index=False, chunksize=10000)
    result_dict = {
        "start": sampleID_list[0],
        "end": sampleID_list[-1]
    }
    return result_dict


def import_custdata():
    error_index_list = []
    try:
        sql_cmd = 'select * from public."back_stage_custdata"'
        df_id = pd.read_sql(sql=sql_cmd, con=engine)
        print(df_id)
        df = pd.read_excel("/root/cust_data_nonreserve.xlsx", converters={'出生日期': str, '身份证号': str, '电话': str, '英文名': str})
        df_import = df[["姓名", "身份证号", "年龄", "电话", "性别", "公司（以委托书名称填写）", "出生日期", "英文名", "备注"]]
        df_import.columns = ["Name", "ContactID", "Age", "Phone", "Sex", "ClientName", "birthday", "ENName", "remark"]
        print(df_import)
        df_checkID = df_import.ClientName.isin(df_id.ClientName)
        print(df_checkID)
        df_clientName = pd.DataFrame()
        df_contactID = pd.DataFrame()
        clientName_list = []
        client_uuid_list = []
        contactID_list = []
        contact_uuid_list = []
        old_clientName_list = []
        old_client_seq_list = []
        old_client_uuid_list = []
        for i in df_checkID.index:
            # not exsit and not duplicate
            if df_checkID.loc[i] == False and i in df_import.ClientName.drop_duplicates().index.tolist():
                import_dict = df_import.loc[i].to_dict()
                url = 'http://192.168.11.21/api/client/{}/{}'.format(import_dict["ClientName"], None)
                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                if str(result.status_code) == "200":
                    print(result.json())
                    clientName_list.append(import_dict["ClientName"])
                    client_uuid_list.append(result.json()["items"][0]["uid"])
                else:
                    error_index_list.append(int(i) + 2)
            elif df_checkID.loc[i] == True:
                if df_import.ContactID.isin(df_id.ContactID).loc[i] == False:
                    import_dict = df_import.loc[i].to_dict()
                    name = import_dict["Name"]
                    sex = import_dict["Sex"]
                    contactID = import_dict["ContactID"]
                    phone = import_dict["Phone"]
                    age = import_dict["Age"]
                    birthday = str(import_dict["birthday"]).replace('/', '-')
                    clientName = import_dict["ClientName"]
                    client_uuid = df_id.Client_uuid[df_id.ClientName == clientName].tolist()[0]
                    other = str(import_dict["ENName"]) + ':' + str(import_dict["remark"])
                    # email = import_dict["Email"]
                    url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid,
                                                                                                      contactID,
                                                                                                      name, sex, age,
                                                                                                      birthday,
                                                                                                      clientName, phone,
                                                                                                      other, clientName)

                    print(url)
                    result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                    if str(result.status_code) == "200":
                        print(result.json())
                        clientName_list.append(import_dict["ClientName"])
                        client_uuid_list.append(result.json()["items"][0]["uid"])
                    else:
                        error_index_list.append(int(i) + 2)
                    contactID_list.append(result.json()["items"][0]["Salutation"])
                    contact_uuid_list.append(result.json()["items"][0]["uid"])
                    old_clientName_list.append(import_dict["ClientName"])
                    old_client_seq_list.append(result.json()["items"][0]["parent_id"])
                    old_client_uuid_list.append(result.json()["items"][0]["parent_uid"])
        df_clientName["ClientName"] = clientName_list
        df_clientName["Client_uuid"] = client_uuid_list
        df_contactID["ContactID"] = contactID_list
        df_contactID["Contact_uuid"] = contact_uuid_list
        df_contactID["ClientName"] = old_clientName_list
        df_contactID["Client_uuid"] = old_client_uuid_list
        df_contactID_export = pd.merge(df_import, df_contactID)
        print(df_clientName)
        print(df_contactID_export)

        # Create new clients'contacts
        print("new contact")
        df_export = pd.merge(df_import, df_clientName)
        print(df_export)
        birthday = None
        df_contactID = pd.DataFrame()
        for i in df_export.index:
            data = df_export.loc[i].to_dict()
            print(data)
            for key, value in data.items():
                if ''.join(key) == "Name":
                    name = value
                elif ''.join(key) == "ContactID":
                    contactID = value
                elif ''.join(key) == "Age":
                    age = value
                elif ''.join(key) == "Phone":
                    phone = value
                elif ''.join(key) == "birthday":
                    birthday = str(value).replace('/', '-')
                elif ''.join(key) == "Client_uuid":
                    client_uuid = value
                    print(client_uuid)
                elif ''.join(key) == "Email":
                    email = value
                elif ''.join(key) == "Sex":
                    sex = value
                elif ''.join(key) == "ClientName":
                    clientName = value
            other = str(data["ENName"]) + ':' + str(data["remark"])

            url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contactID,
                                                                                              name, sex, age, birthday,
                                                                                              clientName, phone, other,
                                                                                                 clientName)
            print(url)
            result = requests.post(url, cookies=reslogin.cookies, headers=headers)
            if str(result.status_code) == "200":
                print(result.json())
                clientName_list.append(import_dict["ClientName"])
                client_uuid_list.append(result.json()["items"][0]["uid"])
            else:
                error_index_list.append(int(i) + 2)
            contactID_list.append(result.json()["items"][0]["Salutation"])
            contact_uuid_list.append(result.json()["items"][0]["uid"])
        df_contactID['ContactID'] = contactID_list
        df_contactID['Contact_uuid'] = contact_uuid_list
        df_export = pd.merge(df_export, df_contactID)
        df_export = df_export.append(df_contactID_export)
        df_export = df_export.reset_index(drop=True)
        print(df_contactID)
        print(df_export)
        df_export = df_export[["Name", "ClientName", "ContactID", "Client_uuid", "Contact_uuid"]]
        df_export.to_sql(name=my_tbname_5, con=engine, if_exists='append', index=False, chunksize=10000)
        if not error_index_list:
            errorMsg = ""
        else:
            errorMsg = ",第{}行資料有誤".format(error_index_list)
        msg = "已匯入:{}筆資料".format(df_export.shape[0]) + errorMsg
        return msg
    except Exception as e:
        if "You are trying to merge on object and float64 columns. If you wish to proceed you should use pd.concat" == str(e):
            return "匯入不成功:此份檔案之人員資料皆已匯入過"
        else:
            print(e)
            return "匯入不成功:輸入格式不正確,請參考範例檔案之欄位及格式"


def update_contact_polling_info():
    error_index_list = []
    try:
        sql_cmd = 'select * from public."back_stage_custdata"'
        df_id = pd.read_sql(sql=sql_cmd, con=engine)
        df_id = df_id[["Name", "ClientName", "ContactID", "Client_uuid", "Contact_uuid"]]
        print(df_id)
        df_import = pd.read_excel("/root/contactPolling.xlsx", converters={'身份证号': str})
        df_import.columns = ["ContactID", "PID", "DateSampled", "SampleReceiveDate", "Type"]
        print(df_import)
        df_export = pd.merge(df_id, df_import, on='ContactID')
        print(df_export)
        first_PID_index_list = df_export.PID.drop_duplicates().index.to_list()
        df_export_unique = df_export.loc[first_PID_index_list]
        df_export.sort_values(by='PID', inplace=True)
        print(df_export)
        print(df_export_unique)
        df_sampleID = pd.DataFrame()
        contact_uuid_list = []
        sample_uuid_list = []
        sampleID_list = []
        for i in df_export_unique.index:
            client_uuid = df_export_unique.loc[i, "Client_uuid"]
            PID = df_export_unique.loc[i, "PID"]
            contact_uuid = df_export_unique.loc[i, "Contact_uuid"]
            type = df_export_unique.loc[i, "Type"]
            EnvironmentalConditions = str(df_export_unique.loc[i, "DateSampled"]) + ',' + str(df_export_unique.loc[i, "SampleReceiveDate"])
            print(client_uuid)
            print(contact_uuid)
            contact_uuid_polling_list = df_export.loc[
                df_export.PID == df_export.loc[i].PID, ['Contact_uuid']].values.ravel().tolist()
            url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid,
                                                                                    "b54dcd097d1844578dd333219f4b0ff6",
                                                                                    "72ee86eeed68455fbcbf05ce7d7e1d8a",
                                                                                    None,
                                                                                    None, type,
                                                                                    PID, contact_uuid_polling_list,
                                                                                    EnvironmentalConditions)
            print(url)
            result = requests.post(url, cookies=reslogin.cookies, headers=headers)
            sample_uuid = result.json()["items"][0]["uid"]
            contact_uuid_list.append(contact_uuid)
            for j in range(0, len(contact_uuid_polling_list)):
                sample_uuid_list.append(sample_uuid)
                sampleID_list.append(result.json()["items"][0]["id"])
        df_sampleID["Contact_uuid"] = df_export.Contact_uuid.values.tolist()
        df_sampleID["Sample_uuid"] = sample_uuid_list
        df_sampleID["Sample_id"] = sampleID_list
        df_export = pd.merge(df_export, df_sampleID, on='Contact_uuid')
        print(df_export)
        # df_export = df_export[["Name", "ClientName", "ContactID", "Client_uuid", "Contact_uuid", "Sample_uuid", "Sample_id", "PID"]]
        df_export.to_sql(name=my_tbname_6, con=engine, if_exists='append', index=False, chunksize=10000)
        if not error_index_list:
            errorMsg = ""
        else:
            errorMsg = ",第{}行資料有誤".format(error_index_list)
        msg = "已匯入:{}筆資料".format(df_export.shape[0]) + errorMsg
        return msg
    except Exception as e:
        if "You are trying to merge on object and float64 columns. If you wish to proceed you should use pd.concat" == str(e):
            return "匯入不成功:請查明是否已進行客戶資料匯入"
        elif "duplicate key" in str(e):
            return "此份檔案已有匯入過的資料"
        else:
            print(e)
            return "匯入不成功:輸入格式不正確,請參考範例檔案之欄位及格式"


def update_barcode_contact_info():
    # error_index_list = []
    try:
        sql_cmd = 'select * from public."back_stage_custdata"'
        df_id = pd.read_sql(sql=sql_cmd, con=engine)
        df_id = df_id[["Client_uuid", "Sample_uuid", "ClientName", "Sample_id"]]
        print(df_id)
        df = pd.read_excel("/root/update_barcode_contact_info.xlsx", converters={'出生日期': str, '身份证号': str, '电话': str})
        df_import = df[["Sample_id", "PID", "ClientFrom", "采样时间", "接收时间", "样本类型", "姓名", "身份证号", "年龄", "电话", "性别", "公司（以委托书名称填写）", "出生日期", "英文名", "备注"]]
        df_import.columns = ["Sample_id", "PID", "ClientName", "DateSampled", "SampleReceiveDate", "Type", "Name", "ContactID", "Age", "Phone", "Sex", "ClientTo", "birthday", "ENName", "remark"]
        print(df_import)
        df_export = pd.merge(df_id, df_import)
        error_index_list = [i+2 for i in df_import[~df_import.Sample_id.isin(df_export.Sample_id)].index.tolist()]
        print(df_export)
        df_contact = pd.DataFrame()
        contactID_list = []
        contact_uuid_list = []
        # 依照客戶資料創建contact
        for i in df_export.index:
            clientFrom = df_export.loc[i, "ClientName"]
            contactID = df_export.loc[i, "ContactID"]
            client_uuid = df_export.loc[i, "Client_uuid"]
            name = df_export.loc[i, "Name"]
            sex = df_export.loc[i, "Sex"]
            age = df_export.loc[i, "Age"]
            birthday = str(df_export.loc[i, "birthday"]).replace('/', '-')
            phone = df_export.loc[i, "Phone"]
            other = str(df_export.loc[i, "ENName"]) + ':' + str(df_export.loc[i, "remark"])
            ClientTo = df_export.loc[i, "ClientTo"]
            url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contactID,
                                                                                               name, sex, age, birthday,
                                                                                               clientFrom, phone, other,
                                                                                                 ClientTo)
            print(url)
            result = requests.post(url, cookies=reslogin.cookies, headers=headers)
            if str(result.status_code) == "200":
                print(result.json())
                contactID_list.append(contactID)
                contact_uuid_list.append(result.json()["items"][0]["uid"])
            else:
                error_index_list.append(int(i) + 2)
        df_contact["ContactID"] = contactID_list
        df_contact["Contact_uuid"] = contact_uuid_list
        print(df_contact)
        df_export = pd.merge(df_export, df_contact)
        print(df_export)
        # 更新barcode資訊
        for i in df_export.index:
            sample_uuid = df_export.loc[i, "Sample_uuid"]
            contact_uuid = df_export.loc[i, "Contact_uuid"]
            type = df_export.loc[i, "Type"]
            PID = df_export.loc[i, "PID"]
            contact_uuid_polling_list = df_export.loc[
                df_export.Sample_id == df_export.loc[i].Sample_id, ['Contact_uuid']].values.ravel().tolist()
            # sample_type_uuid = df_export.loc[i, "SampleType"]
            EnvironmentalConditions = str(df_export.loc[i, "DateSampled"]) + ',' + str(df_export.loc[i, "SampleReceiveDate"])
            print(contact_uuid_polling_list)
            url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}/{}'.format(sample_uuid, client_uuid,
                                                                        contact_uuid, contact_uuid_polling_list,
                                                                              EnvironmentalConditions, None, type, PID)
            print(url)
            result = requests.put(url, cookies=reslogin.cookies, headers=headers)
            if str(result.status_code) == "200":
                print(result.json())
            else:
                error_index_list.append(int(i) + 2)
        # df_export = df_export[["Name", "ClientName", "ContactID", "Client_uuid", "Contact_uuid", "Sample_uuid", "Sample_id"]]
        df_export.to_sql(name=my_tbname_6, con=engine, if_exists='append', index=False, chunksize=10000)
        if not error_index_list:
            errorMsg = ""
        else:
            errorMsg = ",第{}行資料有誤".format(error_index_list)
        msg = "已匯入:{}筆資料".format(df_export.shape[0]) + errorMsg
        return msg
    except Exception as e:
        print(e)
        if "duplicate key" in str(e):
            return "此份檔案已有匯入過的資料"
        elif "You are trying to merge on object and float64 columns. If you wish to proceed you should use pd.concat" == str(e):
            return "匯入不成功:請查明LIMS系統中是否存在這些sample_id"
        else:
            return "匯入不成功:輸入格式不正確,請參考範例檔案之欄位及格式"


def update_sample_result():
    error_index_list = []
    try:
        if os.path.isfile("/root/Extraction_table_{}.xlsx".format(datetime.now().strftime("%Y%m%d"))):
            df = pd.read_excel("/root/Extraction_table_{}.xlsx".format(datetime.now().strftime("%Y%m%d")), sheet_name="新提取表")
        else:
            df = pd.read_excel("/root/Extraction_table_20211111.xlsx", sheet_name="新提取表")
        sql_cmd = 'select * from public."back_stage_report_reserve_sample_test"'
        df_id = pd.read_sql(sql=sql_cmd, con=engine)
        df_id = df_id[["Client_uuid", "Sample_uuid", "ClientName", "Sample_id", "PID"]]
        print(df_id)
        all_barcode_list = []
        for i in df.loc[:, 1:12].values.tolist():
            for element in i:
                all_barcode_list.append(element)
        all_machine_list = []
        machine_list = df.檢測儀器.dropna().tolist()
        for machine in machine_list:
            for i in range(0, 96):
                all_machine_list.append(machine)
        all_result_list = []
        result_list = df.結果.dropna().tolist()
        for result in result_list:
            for i in range(0, 96):
                all_result_list.append(result)
        df_sorted = pd.DataFrame()
        df_sorted["PID"] = all_barcode_list
        df_sorted["Machine"] = all_machine_list
        df_sorted["result"] = all_result_list
        df_sorted = df_sorted[~df_sorted.PID.isin(["水", "空白", "pc", "nc", "质控"]) & df_sorted.PID.notnull()].drop_duplicates()
        print(df_sorted)
        df_export = pd.merge(df_id, df_sorted, on='PID')
        print(df_export)
        for i in df_export.index:
            client_uuid = df_export.loc[i, "Client_uuid"]
            sample_uuid = df_export.loc[i, "Sample_uuid"]
            clientReference = df_export.loc[i, "Machine"] + ',' + df_export.loc[i, "result"]
            url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}'.format(client_uuid, sample_uuid, None, clientReference)
            print(url)
            result = requests.put(url, cookies=reslogin.cookies, headers=headers)
            print(result.json())
        if not error_index_list:
            errorMsg = ""
        else:
            errorMsg = ",第{}行資料有誤".format(error_index_list)
        msg = "已匯入:{}筆資料".format(df_export.shape[0]) + errorMsg
        return msg
    except Exception as e:
        print(e)
        if "duplicate key" in str(e):
            return "此份檔案已有匯入過的資料"
        else:
            return "匯入不成功:輸入格式不正確,請參考範例檔案之欄位及格式"


def single_batch_list():
    if os.path.isfile("/root/Extraction_table_{}.xlsx".format(datetime.now().strftime("%Y%m%d"))):
        df = pd.read_excel("/root/Extraction_table_{}.xlsx".format(datetime.now().strftime("%Y%m%d")), sheet_name="新提取表")
    else:
        df = pd.read_excel("/root/Extraction_table_20211111.xlsx", sheet_name="新提取表")
    batch_list = list(df["上机命名"].dropna())
    batch_dict = {
        "batch": batch_list
    }
    return batch_dict


def single_report(**batchID_dict):
    batchID_list = batchID_dict["batch"]
    if os.path.isfile("/root/Extraction_table_{}.xlsx".format(datetime.now().strftime("%Y%m%d"))):
        df = pd.read_excel("/root/Extraction_table_{}.xlsx".format(datetime.now().strftime("%Y%m%d")), sheet_name="新提取表")
    else:
        df = pd.read_excel("/root/Extraction_table_20211111.xlsx", sheet_name="新提取表")
    # PID
    PID_list = []
    for i in df.loc[:, 1:12].T.values.tolist():
        for element in i:
            if element == "水":
                element = "Shui"
            elif element == "质控":
                element = "ZK"
            elif element == "空白":
                element = "KB"
            elif element == "pc" or element == "阳性":
                element = "PC"
            elif element == "nc" or element == "阴性":
                element = "NC"
            PID_list.append(element)
    # BatchID
    single_batch = list(df["上机命名"].fillna(method='ffill'))
    batch_list = []
    for i in range(0, 12):
        for i in range(0, int(len(PID_list) / 12)):
            batch_list.append(single_batch[i])
    # Well
    list_well = []
    list_element = [list(df["Unnamed: 1"].loc[0:7].values + str(i)) for i in range(1, 13)]
    for i in range(0, 12):
        for time in range(0, int(len(PID_list)/96)):
            for j in range(0, 8):
                list_well.append(list_element[i][j])
    df_sorted = pd.DataFrame()
    df_sorted["BatchID"] = batch_list
    df_sorted["Well"] = list_well
    df_sorted["PID"] = PID_list
    print(df_sorted)
    try:
        for batchID in batchID_list:
            df_export = df_sorted[df_sorted["BatchID"] == batchID]
            df_export = df_export[["Well", "PID"]]
            print(df_export)
            df_export.to_csv("/root/{}.csv".format(batchID), index=False)
        return batchID_dict
    except Exception as e:
        print(e)
        return "查無此batchID"


def muti_report(**batchID_dict):
    batchID_list = batchID_dict["batch"]
    print(batchID_list)
    if os.path.isfile("/root/Extraction_table_{}.xlsx".format(datetime.now().strftime("%Y%m%d"))):
        df = pd.read_excel("/root/Extraction_table_{}.xlsx".format(datetime.now().strftime("%Y%m%d")), sheet_name="新提取表")
    else:
        df = pd.read_excel("/root/Extraction_table_20211111.xlsx", sheet_name="新提取表")
    # PID
    PID_list = []
    for i in df.loc[:, 1:12].T.values.tolist():
        for element in i:
            if element == "水":
                element = "Shui"
            elif element == "质控":
                element = "ZK"
            elif element == "空白":
                element = "KB"
            elif element == "pc" or element == "阳性":
                element = "PC"
            elif element == "nc" or element == "阴性":
                element = "NC"
            PID_list.append(element)
    # BatchID
    single_batch = list(df["上机命名"].fillna(method='ffill'))
    batch_list = []
    for i in range(0, 12):
        for i in range(0, int(len(PID_list) / 12)):
            batch_list.append(single_batch[i])
    # Well
    list_well = []
    list_element = [list(df["Unnamed: 1"].loc[0:7].values + str(i)) for i in range(1, 13)]
    for i in range(0, 12):
        for time in range(0, int(len(PID_list)/96)):
            for j in range(0, 8):
                list_well.append(list_element[i][j])
    df_sorted = pd.DataFrame()
    df_sorted["BatchID"] = batch_list
    df_sorted["Well"] = list_well
    df_sorted["PID"] = PID_list
    print(df_sorted)
    try:
        for batchID in batchID_list:
            df_export = df_sorted[df_sorted["BatchID"] == batchID]
            df_firstThree = df_export[0:3]
            df_A = df_export[df_export['Well'].str.contains('A')]
            df_recursive_A = df_A.append(df_A).append(df_A).sort_index()[3:]
            df_B = df_export[df_export['Well'].str.contains('B')]
            df_recursive_B = df_B.append(df_B).append(df_B).sort_index()
            df_C = df_export[df_export['Well'].str.contains('C')]
            df_recursive_C = df_C.append(df_C).append(df_C).sort_index()
            df_D = df_export[df_export['Well'].str.contains('D')]
            df_recursive_D = df_D.append(df_D).append(df_D).sort_index()
            df_E = df_export[df_export['Well'].str.contains('E')]
            df_recursive_E = df_E.append(df_E).append(df_E).sort_index()
            df_F = df_export[df_export['Well'].str.contains('F')]
            df_recursive_F = df_F.append(df_F).append(df_F).sort_index()
            df_G = df_export[df_export['Well'].str.contains('G')]
            df_recursive_G = df_G.append(df_G).append(df_G).sort_index()
            df_H = df_export[df_export['Well'].str.contains('H')]
            df_recursive_H = df_H.append(df_H).append(df_H).sort_index()
            df_export = df_firstThree.append(df_recursive_A).append(df_recursive_B).append(df_recursive_C).append(
                df_recursive_D).append(df_recursive_E).append(df_recursive_F).append(df_recursive_G).append(
                df_recursive_H)
            df_export = df_export[["Well", "PID"]]
            print(df_export)
            df_export.to_csv("/root/{}_muti.csv".format(batchID), index=False)
        return batchID_dict
    except Exception as e:
        print(e)
        return "查無此batchID"


def secondtype_report_post(**result_dict):
    error_index_list = []
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    print(result_dict)
    contact_uuid_list = []
    sample_uuid_list = []
    for key, value in result_dict.items():
        value = eval(value)
        contact_uuid_list.append(value[0])
        sample_uuid_list.append(value[1])
    print(contact_uuid_list)
    print(sample_uuid_list)
    # sql_cmd = 'select * from public."report_reserve_sample"'
    # df_id = pd.read_sql(sql=sql_cmd, con=engine)
    # contact_id_list = df_id["Contact_uuid"].values.tolist()
    # sample_id_list = df_id["Sample_uuid"].values.tolist()

    # second type report
    df_secondtype = pd.DataFrame(
        columns=["【序号】", "【身份证号】", "【姓名】", "【英文姓名】", "【性别】", "【年龄】", "【样本条码】", "【采样时间】"
            , "【接收时间】", "【手机号】", "【送检单位】", "【护照号】", "【样本类型】", "【报告时间】", "【出生日期】", "【采样单位】"
            , "【检测仪器】", "【检测结果】", "【参考区间】", "【remark】"])
    for i, contact_id in enumerate(contact_uuid_list):
        print(i, contact_id)
        contact_data = load_sql(contact_id)
        print(contact_data)
        print(contact_data["title"].split()[0])
        bitrhday = None if contact_data["JobTitle"].split(':')[0] == 'nan' else contact_data["JobTitle"].split(':')[0]
        enName = None if contact_data["JobTitle"].split(':')[1] == 'nan' else contact_data["JobTitle"].split(':')[1]
        passport_num = None if contact_data["JobTitle"].split(':')[2] == '十混一' else contact_data["JobTitle"].split(':')[2]
        df_secondtype.loc[i] = [i+1, contact_data["Salutation"], contact_data["Firstname"], enName, contact_data["Middlename"], contact_data["Surname"], None, None
            , None, contact_data["MobilePhone"], contact_data["Middleinitial"], passport_num, None, now, bitrhday, "丽宝生医"
            , None, None, None, None]
    # load sample data
    for i, sample_id in enumerate(sample_uuid_list):
        print(i, sample_id)
        sample_data = load_sql(sample_id)
        print(sample_data)
        df_secondtype.loc[i, "【样本条码】"] = sample_data["ClientSampleID"]
        df_secondtype.loc[i, "【样本类型】"] = sample_data["ClientOrderNumber"]
        df_secondtype.loc[i, "【采样时间】"] = sample_data["EnvironmentalConditions"].split(',')[0].split(' ')[0].replace('-', '/')
        df_secondtype.loc[i, "【接收时间】"] = sample_data["EnvironmentalConditions"].split(',')[1].split(' ')[0].replace('-', '/')
        df_secondtype.loc[i, "【检测仪器】"] = sample_data["ClientReference"].split(',')[0]
        try:
            df_secondtype.loc[i, "【检测结果】"] = sample_data["ClientReference"].split(',')[1]
        except:
            error_index_list.append(i)
    df_secondtype.drop(error_index_list, axis=0, inplace=True)
    print(df_secondtype)
    df_secondtype.to_excel("/root/report2.xlsx", index=False)
    return_list = [i + 1 for i in error_index_list]
    if not error_index_list:
        msg = "已匯出報表模板,無任何異常資料"
    else:
        msg = "已勾選之第{}筆資料無法匯出,請確認是否已匯入實驗結果資訊".format(return_list)
    return msg


def reserve_sample():
    # Create clients
    df = pd.read_excel("/root/covid_21-09-16_reserve.xlsx", converters={'送件單位id': str, 'UUID': str, '手機': str})
    df_client = df[["送件單位", "送件單位id"]]
    df_client.columns = ["Name", "ClientID"]
    df_client = df_client.drop_duplicates()
    print(df_client)
    df_clientID = pd.DataFrame()
    clientID_list = []
    client_seq_list = []
    client_uuid_list = []
    sampleID_list = []
    for i in df_client.index:
        data = df_client.loc[i].to_dict()
        for key, value in data.items():
            if ''.join(key) == "Name":
                name = value
            elif ''.join(key) == "ClientID":
                client = value
        url = 'http://192.168.11.21/api/client/{}/{}'.format(name, client)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        # print(result.json())
        clientID = result.json()["items"][0]["id"]
        client_uuid = result.json()["items"][0]["uid"]
        clientID_list.append(client)
        client_seq_list.append(clientID)
        client_uuid_list.append(client_uuid)
    df_clientID["ClientID"] = clientID_list
    df_clientID["Client_seq"] = client_seq_list
    df_clientID["Client_uuid"] = client_uuid_list

    # Create contacts
    df_contact = df[["中文名", "UUID", "手機", "Email", "性別", "送件單位id"]]
    df_contact.columns = ["Name", "ContactID", "Phone", "Email", "Sex", "ClientID"]
    df_contact.Sex = df_contact.Sex.squeeze().str.split(' /', expand=True)[0]
    print(df_contact)
    print(df_clientID)
    df_export = pd.merge(df_contact, df_clientID)
    print(df_export)
    df_contactID = pd.DataFrame()
    contactID_list=[]
    contact_uuid_list = []
    for i in df_export.index:
        data = df_export.loc[i].to_dict()
        for key, value in data.items():
            if ''.join(key) == "Name":
                name = value
            elif ''.join(key) == "ContactID":
                contactID = value
            elif ''.join(key) == "Phone":
                phone = value
            elif ''.join(key) == "Email":
                email = value
            elif ''.join(key) == "Sex":
                sex = value
            elif ''.join(key) == "ClientID":
                clientID = value
                df_filter = df_clientID.ClientID == clientID
                client_seq = df_clientID[df_filter.squeeze()]["Client_seq"].values[0]
                url = 'http://192.168.11.21/api/contact/{}/{}/{}/{}/{}/{}'.format(client_seq, name, sex, contactID, phone, email)
                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Username"]
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
    df_contactID['ContactID'] = contactID_list
    df_contactID['Contact_uuid'] = contact_uuid_list
    df_export = pd.merge(df_export, df_contactID, on='ContactID')
    print(df_export)

    # Create samples
    df_sampleID = pd.DataFrame()
    contact_uuid_list = []
    sample_uuid_list = []
    for i in df_export.index:
        client_uuid = df_export.loc[i, "Client_uuid"]
        contact_uuid = df_export.loc[i, "Contact_uuid"]
        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contact_uuid,
                                                                             '72ee86eeed68455fbcbf05ce7d7e1d8a', None,
                                                                             None, None,
                                                                             None)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        sample_uuid = result.json()["items"][0]["uid"]
        sample_id = result.json()["items"][0]["id"]
        # print(result.json())
        contact_uuid_list.append(contact_uuid)
        sample_uuid_list.append(sample_uuid)
        sampleID_list.append(sample_id)
    df_sampleID["Contact_uuid"] = contact_uuid_list
    df_sampleID["Sample_uuid"] = sample_uuid_list
    df_sampleID["Sample_id"] = sampleID_list
    df_export = pd.merge(df_export, df_sampleID, on='Contact_uuid')
    print(df_export)
    df_export.to_sql(name=my_tbname_1, con=engine, if_exists='append', index=False, chunksize=10000)


def reserve_sample_report():
    # Create clients
    df = pd.read_excel("/root/cust_data_reserve.xlsx")
    df["出生日期"] = df["出生日期"].str.replace('/', '-')
    df_client = df[["公司（以委托书名称填写）"]]
    df_client = df_client.drop_duplicates()
    df_client.reset_index(drop=True, inplace=True)
    df_client.reset_index(drop=False, inplace=True)
    df_client.columns = ["ClientID", "Name"]
    df_client.ClientID += 1
    print(df_client)
    df_clientID = pd.DataFrame()
    clientID_list = []
    client_seq_list = []
    client_uuid_list = []
    client_name_list = []
    sampleID_list = []
    for i in df_client.index:
        data = df_client.loc[i].to_dict()
        for key, value in data.items():
            if ''.join(key) == "Name":
                name = value
            elif ''.join(key) == "ClientID":
                clientID = str(value)
        url = 'http://192.168.11.21/api/client/{}/{}'.format(name, clientID)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        print(result.json())
        clientID = result.json()["items"][0]["ClientID"]
        client_seq = result.json()["items"][0]["id"]
        client_uuid = result.json()["items"][0]["uid"]
        client_name = result.json()["items"][0]["Name"]
        clientID_list.append(clientID)
        client_seq_list.append(client_seq)
        client_uuid_list.append(client_uuid)
        client_name_list.append(client_name)
    df_clientID["ClientID"] = clientID_list
    df_clientID["ClientName"] = client_name_list
    df_clientID["Client_seq"] = client_seq_list
    df_clientID["Client_uuid"] = client_uuid_list
    print(df_clientID)
    #
    # Create contacts
    df_contact = df[["姓名", "身份证号", "年龄", "电话", "性别", "公司（以委托书名称填写）", "出生日期"]]
    df_contact.columns = ["Name", "ContactID", "Age","Phone", "Sex", "ClientName", "birthday"]
    df_contact.Sex = df_contact.Sex.squeeze().str.split(' /', expand=True)[0]
    print(df_contact)
    print(df_clientID)
    df_export = pd.merge(df_contact, df_clientID)
    print(df_export)
    df_contactID = pd.DataFrame()
    contactID_list=[]
    contact_uuid_list = []
    for i in df_export.index:
        data = df_export.loc[i].to_dict()
        for key, value in data.items():
            if ''.join(key) == "Name":
                name = value
            elif ''.join(key) == "Client_uuid":
                client_uuid = value
            elif ''.join(key) == "ContactID":
                contactID = value
            elif ''.join(key) == "Age":
                age = value
            elif ''.join(key) == "Phone":
                phone = value
            elif ''.join(key) == "Email":
                email = value
            elif ''.join(key) == "Sex":
                sex = value
            elif ''.join(key) == "ClientID":
                clientID = value
            elif ''.join(key) == "ClientName":
                clientName = value
            elif ''.join(key) == "birthday":
                birthday = value
                # df_filter = df_clientID.ClientID == clientID
                # client_seq = df_clientID[df_filter.squeeze()]["Client_seq"].values[0]
                url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contactID, name, sex, age, birthday, clientName, phone)
                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                print(result.json())
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Salutation"]
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
    df_contactID['ContactID'] = contactID_list
    df_contactID['Contact_uuid'] = contact_uuid_list
    print(df_export)
    print(df_contactID)
    df_export = pd.merge(df_export, df_contactID, on='ContactID')
    print(df_export)
    #
    # Create samples
    df_sampleID = pd.DataFrame()
    contact_uuid_list = []
    sample_uuid_list = []
    for i in df_export.index:
        client_uuid = df_export.loc[i, "Client_uuid"]
        contact_uuid = df_export.loc[i, "Contact_uuid"]
        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contact_uuid,
                                                                             '72ee86eeed68455fbcbf05ce7d7e1d8a', None,
                                                                             None, None,
                                                                             None)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        sample_uuid = result.json()["items"][0]["uid"]
        sample_id = result.json()["items"][0]["id"]
        print(result.json())
        contact_uuid_list.append(contact_uuid)
        sample_uuid_list.append(sample_uuid)
        sampleID_list.append(sample_id)
    df_sampleID["Contact_uuid"] = contact_uuid_list
    df_sampleID["Sample_uuid"] = sample_uuid_list
    df_sampleID["Sample_id"] = sampleID_list
    df_export = pd.merge(df_export, df_sampleID, on='Contact_uuid')
    print(df_export)
    # df_contact_uuid = df_export[["Name", "ContactID", "Phone", "ClientName", "ClientID", "Client_seq", "Client_uuid", "Contact_uuid", "Sample_uuid", "Sex", "Sample_id"]]
    df_export = df_export[["Name", "ClientName", "ContactID", "Client_uuid", "Contact_uuid", "Sample_uuid", "Sample_id"]]
    df_export.to_sql(name=my_tbname_4, con=engine, if_exists='append', index=False, chunksize=10000)


def report_sample_chao():
    # Create clients
    df = pd.read_excel("/root/20211020厦航洪文活动中心采样（687人）.xlsx", converters={"身份证匹配手机号": str, "姓名匹配手机号": str})
    print(df.head(10))
    df_data = df[["条码", "输入身份证", "姓名", "性别", "身份证匹配手机号", "身份证匹配公司", "姓名匹配手机号"]]
    print(df_data)
    # df["出生日期"] = df["出生日期"].str.replace('/', '-')
    # df_client = df[["公司（以委托书名称填写）"]]
    # df_client = df_client.drop_duplicates()
    # df_client.reset_index(drop=True, inplace=True)
    # df_client.reset_index(drop=False, inplace=True)
    # df_client.columns = ["ClientID", "Name"]
    # df_client.ClientID += 1
    # print(df_client)
    # df_clientID = pd.DataFrame()
    # clientID_list = []
    # client_seq_list = []
    # client_uuid_list = []
    # client_name_list = []
    # sampleID_list = []
    # for i in df_client.index:
    #     data = df_client.loc[i].to_dict()
    #     for key, value in data.items():
    #         if ''.join(key) == "Name":
    #             name = value
    #         elif ''.join(key) == "ClientID":
    #             clientID = str(value)
    #     url = 'http://192.168.11.21/api/client/{}/{}'.format(name, clientID)
    #     print(url)
    #     result = requests.post(url, cookies=reslogin.cookies, headers=headers)
    #     print(result.json())
    #     clientID = result.json()["items"][0]["ClientID"]
    #     client_seq = result.json()["items"][0]["id"]
    #     client_uuid = result.json()["items"][0]["uid"]
    #     client_name = result.json()["items"][0]["Name"]
    #     clientID_list.append(clientID)
    #     client_seq_list.append(client_seq)
    #     client_uuid_list.append(client_uuid)
    #     client_name_list.append(client_name)
    # df_clientID["ClientID"] = clientID_list
    # df_clientID["ClientName"] = client_name_list
    # df_clientID["Client_seq"] = client_seq_list
    # df_clientID["Client_uuid"] = client_uuid_list
    # print(df_clientID)
    # #
    # # Create contacts
    # df_contact = df[["姓名", "身份证号", "年龄", "电话", "性别", "公司（以委托书名称填写）", "出生日期"]]
    # df_contact.columns = ["Name", "ContactID", "Age", "Phone", "Sex", "ClientName", "birthday"]
    # df_contact.Sex = df_contact.Sex.squeeze().str.split(' /', expand=True)[0]
    # print(df_contact)
    # print(df_clientID)
    # df_export = pd.merge(df_contact, df_clientID)
    # print(df_export)
    # df_contactID = pd.DataFrame()
    # contactID_list = []
    # contact_uuid_list = []
    # for i in df_export.index:
    #     data = df_export.loc[i].to_dict()
    #     for key, value in data.items():
    #         if ''.join(key) == "Name":
    #             name = value
    #         elif ''.join(key) == "Client_uuid":
    #             client_uuid = value
    #         elif ''.join(key) == "ContactID":
    #             contactID = value
    #         elif ''.join(key) == "Age":
    #             age = value
    #         elif ''.join(key) == "Phone":
    #             phone = value
    #         elif ''.join(key) == "Email":
    #             email = value
    #         elif ''.join(key) == "Sex":
    #             sex = value
    #         elif ''.join(key) == "ClientID":
    #             clientID = value
    #         elif ''.join(key) == "ClientName":
    #             clientName = value
    #         elif ''.join(key) == "birthday":
    #             birthday = value
    #             # df_filter = df_clientID.ClientID == clientID
    #             # client_seq = df_clientID[df_filter.squeeze()]["Client_seq"].values[0]
    #             url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contactID,
    #                                                                                            name, sex, age, birthday,
    #                                                                                            clientName, phone)
    #             print(url)
    #             result = requests.post(url, cookies=reslogin.cookies, headers=headers)
    #             print(result.json())
    #             contact_uuid = result.json()["items"][0]["uid"]
    #             contact_id = result.json()["items"][0]["Salutation"]
    #             contactID_list.append(contact_id)
    #             contact_uuid_list.append(contact_uuid)
    # df_contactID['ContactID'] = contactID_list
    # df_contactID['Contact_uuid'] = contact_uuid_list
    # print(df_export)
    # print(df_contactID)
    # df_export = pd.merge(df_export, df_contactID, on='ContactID')
    # print(df_export)
    # #
    # # Create samples
    # df_sampleID = pd.DataFrame()
    # contact_uuid_list = []
    # sample_uuid_list = []
    # for i in df_export.index:
    #     client_uuid = df_export.loc[i, "Client_uuid"]
    #     contact_uuid = df_export.loc[i, "Contact_uuid"]
    #     url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contact_uuid,
    #                                                                          '72ee86eeed68455fbcbf05ce7d7e1d8a', None,
    #                                                                          None, None,
    #                                                                          None)
    #     print(url)
    #     result = requests.post(url, cookies=reslogin.cookies, headers=headers)
    #     sample_uuid = result.json()["items"][0]["uid"]
    #     sample_id = result.json()["items"][0]["id"]
    #     print(result.json())
    #     contact_uuid_list.append(contact_uuid)
    #     sample_uuid_list.append(sample_uuid)
    #     sampleID_list.append(sample_id)
    # df_sampleID["Contact_uuid"] = contact_uuid_list
    # df_sampleID["Sample_uuid"] = sample_uuid_list
    # df_sampleID["Sample_id"] = sampleID_list
    # df_export = pd.merge(df_export, df_sampleID, on='Contact_uuid')
    # print(df_export)
    # # df_contact_uuid = df_export[["Name", "ContactID", "Phone", "ClientName", "ClientID", "Client_seq", "Client_uuid", "Contact_uuid", "Sample_uuid", "Sex", "Sample_id"]]
    # df_export = df_export[["Name", "ClientName", "ContactID", "Client_uuid", "Contact_uuid", "Sample_uuid"]]
    # df_export.to_sql(name=my_tbname_4, con=engine, if_exists='append', index=False, chunksize=10000)


def nonreserve_sample():
    # Create new clients & exsit client but new contacts
    sql_cmd = 'select * from public."nonreserve_sample"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    print(df_id)
    df = pd.read_excel("/root/covid_21-09-16_nonreserve.xlsx", converters={'送件單位id': str, 'UUID': str, '手機': str})
    df_import = df[["送件單位", "送件單位id", "UUID", "中文名", "手機", "Email", "性別"]]
    df_import.columns = ["Client_Name", "ClientID", "ContactID", "Name", "Phone", "Email", "Sex"]
    df_import.Sex = df_import.Sex.str.split(' /', expand=True)[0]
    df_checkID = df_import.ClientID.isin(df_id.ClientID)
    print(df_import)
    df_clientID = pd.DataFrame()
    df_contactID = pd.DataFrame()
    clientID_list = []
    client_seq_list = []
    client_uuid_list = []
    contactID_list = []
    contact_uuid_list = []
    old_clientID_list = []
    old_client_seq_list = []
    old_client_uuid_list = []
    print(df_checkID)
    for i in df_checkID.index:
        if df_checkID.loc[i] == False and i in df_import.ClientID.drop_duplicates().index.tolist():
            import_dict = df_import.loc[i].to_dict()
            url = 'http://192.168.11.21/api/client/{}/{}'.format(import_dict["Client_Name"], import_dict["ClientID"])
            print(url)
            result = requests.post(url, cookies=reslogin.cookies, headers=headers)
            print(result.json())
            clientID = result.json()["items"][0]["id"]
            client_uuid = result.json()["items"][0]["uid"]
            clientID_list.append(import_dict["ClientID"])
            client_seq_list.append(clientID)
            client_uuid_list.append(client_uuid)
        elif df_checkID.loc[i] == True:
            if df_import.ContactID.isin(df_id.ContactID).loc[i] == False:
                # print(df_import.loc[i].to_dict())
                # print(df_id.loc[i].to_dict())
                import_dict = df_import.loc[i].to_dict()
                print(import_dict)
                # import_dict = df_id.loc[i].to_dict()
                name = import_dict["Name"]
                sex = import_dict["Sex"]
                contactID = import_dict["ContactID"]
                phone = import_dict["Phone"]
                email = import_dict["Email"]
                client_uuid = df_id.Client_uuid[df_id.ClientID == import_dict["ClientID"]].tolist()[0]
                url = 'http://192.168.11.21/api/contact/{}/{}/{}/{}/{}/{}'.format(client_uuid, name, sex, contactID,
                                                                                   phone, email)
                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                print(result.json())
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Username"]
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
                old_clientID_list.append(import_dict["ClientID"])
                old_client_seq_list.append(result.json()["items"][0]["parent_id"])
                old_client_uuid_list.append(result.json()["items"][0]["parent_uid"])
    df_clientID["ClientID"] = clientID_list
    df_clientID["Client_seq"] = client_seq_list
    df_clientID["Client_uuid"] = client_uuid_list
    df_contactID["ContactID"] = contactID_list
    df_contactID["Contact_uuid"] = contact_uuid_list
    df_contactID["ClientID"] = old_clientID_list
    df_contactID["Client_seq"] = old_client_seq_list
    df_contactID["Client_uuid"] = old_client_uuid_list
    df_contactID_export = pd.merge(df_import, df_contactID)
    print(df_import)
    print(df_contactID)
    print(df_contactID_export)

    # Create new contacts
    print("new contact")
    df_contact = df[["中文名", "UUID", "手機", "Email", "性別", "送件單位id"]]
    df_contact.columns = ["Name", "ContactID", "Phone", "Email", "Sex", "ClientID"]
    df_contact.Sex = df_contact.Sex.str.split(' /', expand=True)[0]
    print(df_contact)
    df_export = pd.merge(df_contact, df_clientID, on='ClientID')
    print(df_export)
    df_contactID = pd.DataFrame()
    for i in df_export.index:
        data = df_export.loc[i].to_dict()
        for key, value in data.items():
            if ''.join(key) == "Name":
                name = value
            elif ''.join(key) == "ContactID":
                contactID = value
            elif ''.join(key) == "Phone":
                phone = value
            elif ''.join(key) == "Email":
                email = value
            elif ''.join(key) == "Sex":
                sex = value
            elif ''.join(key) == "ClientID":
                clientID = value
                df_filter = df_clientID.ClientID == clientID
                print(df_filter)
                Client_uuid = df_clientID[df_filter]["Client_uuid"].values[0]
                url = 'http://192.168.11.21/api/contact/{}/{}/{}/{}/{}/{}'.format(Client_uuid, name, sex, contactID,
                                                                                   phone, email)
                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Username"]
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
    df_contactID['ContactID'] = contactID_list
    df_contactID['Contact_uuid'] = contact_uuid_list
    df_contactID_export = df_contactID_export.drop(columns=["Client_Name"])
    # df_contactID_export.Sex = df_contactID_export.Sex.str.split(' /', expand=True)[0]
    df_export = pd.merge(df_export, df_contactID)
    df_export = df_export.append(df_contactID_export)
    df_export = df_export.reset_index(drop=True)
    print(df_contactID)
    print(df_export)

    # Create samples
    print("Create samples")
    df_sampleID = pd.DataFrame()
    contact_uuid_list = []
    sample_uuid_list = []
    sampleID_list = []
    for i in df_export.index:
        client_uuid = df_export.loc[i, "Client_uuid"]
        contact_uuid = df_export.loc[i, "Contact_uuid"]
        print(client_uuid)
        print(contact_uuid)
        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contact_uuid,
                                                                             '72ee86eeed68455fbcbf05ce7d7e1d8a', None,
                                                                             None, None,
                                                                             None)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        sample_uuid = result.json()["items"][0]["uid"]
        contact_uuid_list.append(contact_uuid)
        sample_uuid_list.append(sample_uuid)
        sampleID_list.append(result.json()["items"][0]["id"])
    df_sampleID["Contact_uuid"] = contact_uuid_list
    df_sampleID["Sample_uuid"] = sample_uuid_list
    df_sampleID["Sample_id"] = sampleID_list
    df_export = pd.merge(df_export, df_sampleID, on='Contact_uuid')
    print(df_export)
    df_export.to_sql(name=my_tbname_2, con=engine, if_exists='append', index=False, chunksize=10000)


def nonreserve_sample_report():
    # Create new clients & old client but new contacts
    sql_cmd = 'select * from public."back_stage_custdata"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    print(df_id)
    df = pd.read_excel("/root/cust_data_nonreserve.xlsx", converters={'出生日期': str, '身份证号': str, '电话': str})
    df_import = df[["姓名", "身份证号", "年龄", "电话", "性别", "公司（以委托书名称填写）", "出生日期"]]
    df_import.columns = ["Name", "ContactID", "Age", "Phone", "Sex", "ClientName", "birthday"]
    print(df_import)
    df_checkID = df_import.ClientName.isin(df_id.ClientName)
    print(df_checkID)
    df_clientName = pd.DataFrame()
    df_contactID = pd.DataFrame()
    clientName_list = []
    client_seq_list = []
    client_uuid_list = []
    contactID_list = []
    contact_uuid_list = []
    old_clientName_list = []
    old_client_seq_list = []
    old_client_uuid_list = []
    for i in df_checkID.index:
        # not exsit and not duplicate
        if df_checkID.loc[i] == False and i in df_import.ClientName.drop_duplicates().index.tolist():
            import_dict = df_import.loc[i].to_dict()
            url = 'http://192.168.11.21/api/client/{}/{}'.format(import_dict["ClientName"], None)
            print(url)
            result = requests.post(url, cookies=reslogin.cookies, headers=headers)
            print(result.json())
            # clientName = result.json()["items"][0]["Name"]
            client_uuid = result.json()["items"][0]["uid"]
            clientName_list.append(import_dict["ClientName"])
            # clientName_list.append(clientName)
            client_uuid_list.append(client_uuid)
        elif df_checkID.loc[i] == True:
            if df_import.ContactID.isin(df_id.ContactID).loc[i] == False:
                import_dict = df_import.loc[i].to_dict()
                name = import_dict["Name"]
                sex = import_dict["Sex"]
                contactID = import_dict["ContactID"]
                phone = import_dict["Phone"]
                age = import_dict["Age"]
                birthday = import_dict["birthday"]
                clientName = import_dict["ClientName"]
                client_uuid = df_id.Client_uuid[df_id.ClientName == clientName].tolist()[0]
                # email = import_dict["Email"]
                url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contactID,
                                                                                               name, sex, age, birthday,
                                                                                               clientName, phone)

                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                print(result.json())
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Salutation"]
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
                old_clientName_list.append(import_dict["ClientName"])
                old_client_seq_list.append(result.json()["items"][0]["parent_id"])
                old_client_uuid_list.append(result.json()["items"][0]["parent_uid"])
    df_clientName["ClientName"] = clientName_list
    # df_clientName["Client_seq"] = client_seq_list
    df_clientName["Client_uuid"] = client_uuid_list
    df_contactID["ContactID"] = contactID_list
    df_contactID["Contact_uuid"] = contact_uuid_list
    df_contactID["ClientName"] = old_clientName_list
    # df_contactID["Client_seq"] = old_client_seq_list
    df_contactID["Client_uuid"] = old_client_uuid_list
    df_contactID_export = pd.merge(df_import, df_contactID)
    print(df_clientName)
    print(df_contactID_export)

    # Create new clients'contacts
    print("new contact")
    # df_contact = df[["中文名", "UUID", "手機", "Email", "性別", "送件單位id"]]
    # df_contact.columns = ["Name", "ContactID", "Phone", "Email", "Sex", "ClientID"]
    # df_contact.Sex = df_contact.Sex.str.split(' /', expand=True)[0]
    df_export = pd.merge(df_import, df_clientName)
    print(df_export)
    birthday = None
    df_contactID = pd.DataFrame()
    for i in df_export.index:
        data = df_export.loc[i].to_dict()
        for key, value in data.items():
            if ''.join(key) == "Name":
                name = value
            elif ''.join(key) == "ContactID":
                contactID = value
            elif ''.join(key) == "Age":
                age = value
            elif ''.join(key) == "Phone":
                phone = value
            elif ''.join(key) == "birthday":
                birthday = value
            elif ''.join(key) == "Client_uuid":
                client_uuid = value
            elif ''.join(key) == "Email":
                email = value
            elif ''.join(key) == "Sex":
                sex = value
            elif ''.join(key) == "ClientName":
                clientName = value
                # df_filter = df_clientName.ClientName == clientName
                # print(df_filter)
                # client_seq = df_clientName[df_filter]["Client_seq"].values[0]
                url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contactID,
                                                                                               name, sex, age, birthday,
                                                                                               clientName, phone)
                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Salutation"]
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
    df_contactID['ContactID'] = contactID_list
    df_contactID['Contact_uuid'] = contact_uuid_list
    # df_contactID_export = df_contactID_export.drop(columns=["Client_Name"])
    # df_contactID_export.Sex = df_contactID_export.Sex.str.split(' /', expand=True)[0]
    df_export = pd.merge(df_export, df_contactID)
    df_export = df_export.append(df_contactID_export)
    df_export = df_export.reset_index(drop=True)
    print(df_contactID)
    print(df_export)

    # Create samples
    print("Create samples")
    df_sampleID = pd.DataFrame()
    contact_uuid_list = []
    sample_uuid_list = []
    sampleID_list = []
    for i in df_export.index:
        client_uuid = df_export.loc[i, "Client_uuid"]
        contact_uuid = df_export.loc[i, "Contact_uuid"]
        print(client_uuid)
        print(contact_uuid)
        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contact_uuid,
                                                                             '72ee86eeed68455fbcbf05ce7d7e1d8a', None,
                                                                             None, None,
                                                                             None)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        sample_uuid = result.json()["items"][0]["uid"]
        contact_uuid_list.append(contact_uuid)
        sample_uuid_list.append(sample_uuid)
        sampleID_list.append(result.json()["items"][0]["id"])
    df_sampleID["Contact_uuid"] = contact_uuid_list
    df_sampleID["Sample_uuid"] = sample_uuid_list
    df_sampleID["Sample_id"] = sampleID_list
    df_export = pd.merge(df_export, df_sampleID, on='Contact_uuid')
    print(df_export)
    df_export = df_export[["Name", "ClientName", "ContactID", "Client_uuid", "Contact_uuid", "Sample_uuid", "Sample_id"]]
    df_export.to_sql(name=my_tbname_6, con=engine, if_exists='append', index=False, chunksize=10000)


def cust_data_polling():
    # Create new clients & old client but new contacts
    sql_cmd = 'select * from public."back_stage_report_reserve_sample_test"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    print(df_id)
    df = pd.read_excel("/root/cust_data_polling.xlsx", converters={'出生日期': str, '身份证号': str, '电话': str})
    df_import = df[["姓名", "身份证号", "年龄", "电话", "性别", "公司（以委托书名称填写）", "出生日期", "PID"]]
    df_import.columns = ["Name", "ContactID", "Age", "Phone", "Sex", "ClientName", "birthday", "PID"]
    print(df_import)
    df_checkID = df_import.ClientName.isin(df_id.ClientName)
    print(df_checkID)
    df_clientName = pd.DataFrame()
    df_contactID = pd.DataFrame()
    clientName_list = []
    client_seq_list = []
    client_uuid_list = []
    contactID_list = []
    contact_uuid_list = []
    old_clientName_list = []
    old_client_seq_list = []
    old_client_uuid_list = []
    for i in df_checkID.index:
        # not exsit and not duplicate
        if df_checkID.loc[i] == False and i in df_import.ClientName.drop_duplicates().index.tolist():
            import_dict = df_import.loc[i].to_dict()
            url = 'http://192.168.11.21/api/client/{}/{}'.format(import_dict["ClientName"], None)
            print(url)
            result = requests.post(url, cookies=reslogin.cookies, headers=headers)
            print(result.json())
            # clientName = result.json()["items"][0]["Name"]
            client_uuid = result.json()["items"][0]["uid"]
            clientName_list.append(import_dict["ClientName"])
            # clientName_list.append(clientName)
            client_uuid_list.append(client_uuid)
        elif df_checkID.loc[i] == True:
            if df_import.ContactID.isin(df_id.ContactID).loc[i] == False:
                import_dict = df_import.loc[i].to_dict()
                name = import_dict["Name"]
                sex = import_dict["Sex"]
                contactID = import_dict["ContactID"]
                phone = import_dict["Phone"]
                age = import_dict["Age"]
                birthday = import_dict["birthday"]
                clientName = import_dict["ClientName"]
                client_uuid = df_id.Client_uuid[df_id.ClientName == clientName].tolist()[0]
                # email = import_dict["Email"]
                url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contactID,
                                                                                               name, sex, age, birthday,
                                                                                               clientName, phone)

                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                print(result.json())
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Salutation"]
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
                old_clientName_list.append(import_dict["ClientName"])
                old_client_seq_list.append(result.json()["items"][0]["parent_id"])
                old_client_uuid_list.append(result.json()["items"][0]["parent_uid"])
    df_clientName["ClientName"] = clientName_list
    # df_clientName["Client_seq"] = client_seq_list
    df_clientName["Client_uuid"] = client_uuid_list
    df_contactID["ContactID"] = contactID_list
    df_contactID["Contact_uuid"] = contact_uuid_list
    df_contactID["ClientName"] = old_clientName_list
    # df_contactID["Client_seq"] = old_client_seq_list
    df_contactID["Client_uuid"] = old_client_uuid_list
    df_contactID_export = pd.merge(df_import, df_contactID)
    print(df_clientName)
    print(df_contactID_export)

    # Create new clients'contacts
    print("new contact")
    # df_contact = df[["中文名", "UUID", "手機", "Email", "性別", "送件單位id"]]
    # df_contact.columns = ["Name", "ContactID", "Phone", "Email", "Sex", "ClientID"]
    # df_contact.Sex = df_contact.Sex.str.split(' /', expand=True)[0]
    df_export = pd.merge(df_import, df_clientName)
    print(df_export)
    birthday = None
    df_contactID = pd.DataFrame()
    for i in df_export.index:
        data = df_export.loc[i].to_dict()
        for key, value in data.items():
            if ''.join(key) == "Name":
                name = value
            elif ''.join(key) == "ContactID":
                contactID = value
            elif ''.join(key) == "Age":
                age = value
            elif ''.join(key) == "Phone":
                phone = value
            elif ''.join(key) == "birthday":
                birthday = value
            elif ''.join(key) == "Client_uuid":
                client_uuid = value
            elif ''.join(key) == "Email":
                email = value
            elif ''.join(key) == "Sex":
                sex = value
            elif ''.join(key) == "ClientName":
                clientName = value
                # df_filter = df_clientName.ClientName == clientName
                # print(df_filter)
                # client_seq = df_clientName[df_filter]["Client_seq"].values[0]
                url = 'http://192.168.11.21/api/contactReport/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contactID,
                                                                                               name, sex, age, birthday,
                                                                                               clientName, phone)
                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Salutation"]
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
    df_contactID['ContactID'] = contactID_list
    df_contactID['Contact_uuid'] = contact_uuid_list
    # df_contactID_export = df_contactID_export.drop(columns=["Client_Name"])
    # df_contactID_export.Sex = df_contactID_export.Sex.str.split(' /', expand=True)[0]
    df_export = pd.merge(df_export, df_contactID)
    df_export = df_export.append(df_contactID_export)
    df_export = df_export.reset_index(drop=True)
    print(df_contactID)
    print(df_export)

    # Create samples
    print("Create samples")
    first_PID_index_list = df_export.PID.drop_duplicates().index.to_list()
    df_export_unique = df_export.loc[first_PID_index_list]
    df_export.sort_values(by='PID', inplace=True)
    print(df_export)
    print(df_export_unique)
    df_sampleID = pd.DataFrame()
    contact_uuid_list = []
    sample_uuid_list = []
    sampleID_list = []
    for i in df_export_unique.index:
        client_uuid = df_export_unique.loc[i, "Client_uuid"]
        contact_uuid = df_export_unique.loc[i, "Contact_uuid"]
        print(client_uuid)
        print(contact_uuid)
        contact_uuid_polling_list = df_export.loc[df_export.PID == df_export.loc[i].PID, ['Contact_uuid']].values.ravel().tolist()
        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, "b54dcd097d1844578dd333219f4b0ff6",
                                                                             '72ee86eeed68455fbcbf05ce7d7e1d8a', None,
                                                                             None, True,
                                                                             None, contact_uuid_polling_list)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        sample_uuid = result.json()["items"][0]["uid"]
        contact_uuid_list.append(contact_uuid)
        # sample_uuid_list.append(sample_uuid)
        # sampleID_list.append(result.json()["items"][0]["id"])
        for j in range(0, len(contact_uuid_polling_list)):
            sample_uuid_list.append(sample_uuid)
            sampleID_list.append(result.json()["items"][0]["id"])
    df_sampleID["Contact_uuid"] = df_export.Contact_uuid.values.tolist()
    df_sampleID["Sample_uuid"] = sample_uuid_list
    df_sampleID["Sample_id"] = sampleID_list
    df_export = pd.merge(df_export, df_sampleID, on='Contact_uuid')
    print(df_export)
    df_export = df_export[["Name", "ClientName", "ContactID", "Client_uuid", "Contact_uuid", "Sample_uuid", "Sample_id", "PID"]]
    df_export.to_sql(name=my_tbname_6, con=engine, if_exists='append', index=False, chunksize=10000)
    return "已匯入:{}筆資料".format(df_export.shape[0])


def batch_well():
    df_result = pd.read_excel("/root/Batch_Well.xlsx", converters={'BatchID': str, 'ContactID': str})
    sql_cmd_re = 'select * from public."report_reserve_sample"'
    df_re = pd.read_sql(sql=sql_cmd_re, con=engine)
    sql_cmd_nonre = 'select * from public."back_stage_report_reserve_sample_test"'
    df_nonre = pd.read_sql(sql=sql_cmd_nonre, con=engine)
    # df_nonre = df_nonre[
    #     ["Name", "ContactID", "Phone", "Email", "ClientID", "Client_seq", "Client_uuid", "Contact_uuid", "Sample_uuid",
    #      "Sex", "Sample_id"]]
    df_update = df_re.append(df_nonre)
    df_update.reset_index(drop=True, inplace=True)
    df_contact_to_sample = pd.merge(df_result, df_update)
    df_result = df_contact_to_sample[["BatchID", "Sample_id", "ContactID", "Well"]]
    df_result.sort_values(by=['BatchID', 'Well'], inplace=True)
    print(df_result)
    df_split = df_result['Well'].str.split('', expand=True).drop([0, 3], axis=1)
    df_split = pd.concat([df_split, df_result.Sample_id], axis=1)
    print(df_split)
    df_split[1].drop_duplicates().values.tolist()
    df_split[2].drop_duplicates().values.tolist()
    df_graph = pd.DataFrame(columns=df_split[1].drop_duplicates().values.tolist(),
                            index=df_split[2].drop_duplicates().values.tolist())
    df_graph.sort_index(inplace=True)
    df_graph = df_graph.T
    for i in df_split.index:
        record = df_split.loc[i].values.tolist()
        df_graph.loc[record[0], record[1]] = record[2]
    print(df_graph)
    df_graph.to_excel("batch_graph.xlsx")


def batch_well_Xiamen():
    df_result = pd.read_excel("/root/Batch_Well.xlsx", converters={'BatchID': str, 'ContactID': str})
    sql_cmd_re = 'select * from public."back_stage_report_reserve_sample_test"'
    df_re = pd.read_sql(sql=sql_cmd_re, con=engine)
    df_contact_to_sample = pd.merge(df_result, df_re)
    df_result = df_contact_to_sample[["BatchID", "Sample_id", "ContactID", "Well"]]
    df_result.sort_values(by=['BatchID', 'Well'], inplace=True)
    print(df_result)
    df_split = df_result['Well'].str.split('', expand=True).drop([0, 3], axis=1)
    df_split = pd.concat([df_split, df_result], axis=1)
    print(df_split)
    batchID_list = df_split.BatchID.drop_duplicates().tolist()
    writer = pd.ExcelWriter('batch_graph.xlsx', engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Result')
    writer.sheets['Result'] = worksheet
    column = 0
    for i in batchID_list:
        df_graph = batch_graph(df_split[df_split.BatchID == i])
        worksheet.write_string(column, 0, str(i))
        df_graph.to_excel(writer, sheet_name='Result', startrow=column)
        column = column + df_graph.shape[0] + 2
    writer.save()


def batch_well_Xiamen_Polling():
    df_result = pd.read_excel("/root/Batch_Well_polling.xlsx", converters={'BatchID': str, 'ContactID': str})
    sql_cmd_re = 'select * from public."back_stage_report_reserve_sample_test"'
    df_re = pd.read_sql(sql=sql_cmd_re, con=engine)
    df_contact_to_sample = pd.merge(df_result, df_re)
    print(df_contact_to_sample)
    df_result = df_contact_to_sample[["BatchID", "Sample_id", "ContactID", "Well", "PID"]]
    df_result.sort_values(by=['BatchID', 'Well'], inplace=True)
    print(df_result)
    df_pre_polling = df_result[["BatchID", "Well", "PID"]]
    # 混採以第一個人的barcode表示
    df_polling = df_result.loc[df_pre_polling.drop_duplicates().index.to_list()]
    # 將混採人員換上混採的barcode
    df_polling_chgSampleid = df_result[df_result.isin(df_polling)].Sample_id.fillna(method='ffill')
    # 找出非混採的樣本
    unique_sampleid_list = df_polling_chgSampleid.value_counts()[df_polling_chgSampleid.value_counts().values == 1].index.to_list()
    df_result.Sample_id = df_polling_chgSampleid
    df_result["is_polling"] = ~df_polling_chgSampleid.isin(unique_sampleid_list)
    print(df_result)
    df_split = df_polling['Well'].str.split('', expand=True).drop([0, 3], axis=1)
    df_split = pd.concat([df_split, df_polling], axis=1)
    print(df_split)
    batchID_list = df_split.BatchID.drop_duplicates().tolist()
    writer = pd.ExcelWriter('batch_graph.xlsx', engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Result')
    writer.sheets['Result'] = worksheet
    column = 0
    for i in batchID_list:
        df_graph = batch_graph(df_split[df_split.BatchID == i])
        worksheet.write_string(column, 0, str(i))
        df_graph.to_excel(writer, sheet_name='Result', startrow=column)
        column = column + df_graph.shape[0] + 2
    writer.save()


def batch_well_Xiamen_Polling2():
    df_result = pd.read_excel("/root/Batch_Well2.xlsx", converters={'BatchID': str, 'PID': str})
    # sql_cmd_re = 'select * from public."back_stage_report_reserve_sample_test"'
    # df_re = pd.read_sql(sql=sql_cmd_re, con=engine)
    # df_contact_to_sample = pd.merge(df_result, df_re)
    # df_result = df_contact_to_sample[["BatchID", "Sample_id", "ContactID", "Well"]]
    df_result.sort_values(by=['BatchID', 'Well'], inplace=True)
    print(df_result)
    df_split = df_result['Well'].str.split('', expand=True).drop([0, 3], axis=1)
    df_split = pd.concat([df_split, df_result], axis=1)
    print(df_split)
    batchID_list = df_split.BatchID.drop_duplicates().tolist()
    writer = pd.ExcelWriter('batch_graph.xlsx', engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Result')
    writer.sheets['Result'] = worksheet
    column = 0
    for i in batchID_list:
        df_graph = batch_graph(df_split[df_split.BatchID == i])
        worksheet.write_string(column, 0, str(i))
        df_graph.to_excel(writer, sheet_name='Result', startrow=column)
        column = column + df_graph.shape[0] + 2
    writer.save()


def batch_graph(df_split):
    df_graph = pd.DataFrame(columns=df_split[1].drop_duplicates().values.tolist(),
                            index=df_split[2].drop_duplicates().values.tolist())
    df_graph.sort_index(inplace=True)
    df_graph = df_graph.T
    for i in df_split.index:
        record = df_split.loc[i].values.tolist()
        df_graph.loc[record[0], record[1]] = record[3]
    print(df_graph)
    return df_graph


def sample_update():
    # Create batches
    df_batchWell = pd.read_excel("/root/Batch_Well.xlsx", converters={'BatchID': str, 'ContactID': str})
    sql_cmd_re = 'select * from public."reserve_sample"'
    df_re = pd.read_sql(sql=sql_cmd_re, con=engine)
    sql_cmd_nonre = 'select * from public."nonreserve_sample"'
    df_nonre = pd.read_sql(sql=sql_cmd_nonre, con=engine)
    df_nonre = df_nonre[
        ["Name", "ContactID", "Phone", "Email", "ClientID", "Client_seq", "Client_uuid", "Contact_uuid", "Sample_uuid",
         "Sex", "Sample_id"]]
    df_update = df_re.append(df_nonre)
    df_update.reset_index(drop=True, inplace=True)
    print(df_update)
    print(df_batchWell)
    df_merge = pd.merge(df_batchWell, df_update)
    print(df_merge)
    df_import = df_merge[["BatchID", "收件日期", "Client_uuid"]]
    batchID_list = []
    batch_uuid_list = []
    df_batchID = pd.DataFrame()
    for i in df_import.BatchID.drop_duplicates().index:
        print(df_import.iloc[i]["BatchID"], df_import.iloc[i]["收件日期"])
        url = 'http://192.168.11.21/api/batch/{}/{}/{}/{}/{}/{}'.format(df_import.iloc[i]["Client_uuid"], df_import.iloc[i]["BatchID"], None,
                                                                  None, df_import.iloc[i]["收件日期"], None)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        print(result.json())
        batchID_list.append(df_import.iloc[i]["BatchID"])
        batch_uuid_list.append(result.json()["items"][0]["uid"])
    df_batchID["BatchID"] = batchID_list
    df_batchID["Batch_uuid"] = batch_uuid_list
    print(df_batchID)
    df_merge = pd.merge(df_merge, df_batchID)
    print(df_merge)
    df_export = df_merge[["Name", "Client_seq", "ClientID", "Client_uuid", "ContactID", "Contact_uuid", "Sample_id", "Sample_uuid", "BatchID", "Batch_uuid", "Well", "收件日期"]]
    df_export.rename({"收件日期": "Receive_date"}, axis=1, inplace=True)
    df_export.to_sql(name=my_tbname_3, con=engine, if_exists='append', index=False, chunksize=10000)

    # Update samples
    for i in df_merge.index:
        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}'.format(df_merge.iloc[i]["Client_uuid"],df_merge.iloc[i]["Sample_uuid"], df_merge.iloc[i]["收件日期"], None, df_merge.iloc[i]["Batch_uuid"])
        print(url)
        result = requests.put(url, cookies=reslogin.cookies, headers=headers)
        print(result.json())


def sample_update_new():
    # Create batches
    df_batchWell = pd.read_excel("/root/Batch_Well.xlsx", converters={'BatchID': str, 'ContactID': str})
    sql_cmd_nonre = 'select * from public."back_stage_report_reserve_sample_test"'
    df_nonre = pd.read_sql(sql=sql_cmd_nonre, con=engine)
    df_merge = pd.merge(df_batchWell, df_nonre)
    print(df_merge)
    df_import = df_merge[["BatchID", "收件日期", "Client_uuid"]]
    batchID_list = []
    batch_uuid_list = []
    df_batchID = pd.DataFrame()
    for i in df_import.BatchID.drop_duplicates().index:
        print(df_import.iloc[i]["BatchID"], df_import.iloc[i]["收件日期"])
        url = 'http://192.168.11.21/api/batch/{}/{}/{}/{}/{}/{}'.format(df_import.iloc[i]["Client_uuid"], df_import.iloc[i]["BatchID"], None,
                                                                  None, df_import.iloc[i]["收件日期"], None)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        print(result.json())
        batchID_list.append(df_import.iloc[i]["BatchID"])
        batch_uuid_list.append(result.json()["items"][0]["uid"])
    df_batchID["BatchID"] = batchID_list
    df_batchID["Batch_uuid"] = batch_uuid_list
    print(df_batchID)
    df_merge = pd.merge(df_merge, df_batchID)
    print(df_merge)
    # df_export = df_merge[["Name", "Client_seq", "ClientID", "Client_uuid", "ContactID", "Contact_uuid", "Sample_id", "Sample_uuid", "BatchID", "Batch_uuid", "Well", "收件日期"]]
    df_merge.rename({"收件日期": "Receive_date"}, axis=1, inplace=True)
    print(df_merge)
    df_merge.to_sql(name=my_tbname_3, con=engine, if_exists='append', index=False, chunksize=10000)

    # Update samples
    for i in df_merge.index:
        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}'.format(df_merge.iloc[i]["Client_uuid"],df_merge.iloc[i]["Sample_uuid"], df_merge.iloc[i]["Receive_date"], None, df_merge.iloc[i]["Batch_uuid"])
        print(url)
        result = requests.put(url, cookies=reslogin.cookies, headers=headers)
        print(result.json())
# def batch_graph():
#     df_result = if_covid()
#     df_result.sort_values(by='Well', inplace=True)
#     df_split = df_result['Well'].str.split('', expand=True).drop([0, 3], axis=1)
#     df_split = pd.concat([df_split, df_result.if_covid], axis=1)
#     # print(df_split)
#     df_split[1].drop_duplicates().values.tolist()
#     df_split[2].drop_duplicates().values.tolist()
#     df_graph = pd.DataFrame(columns=df_split[1].drop_duplicates().values.tolist(),
#                             index=df_split[2].drop_duplicates().values.tolist())
#     df_graph.sort_index(inplace=True)
#     df_graph = df_graph.T
#     for i in df_split.index:
#         record = df_split.loc[i].values.tolist()
#         df_graph.loc[record[0], record[1]] = record[2]
#     df_graph_styler = df_graph.style.applymap(color_dataframe)
#     df_graph_styler.to_excel("output.xlsx")


def if_covid():
    df = pd.read_excel("/root/20210719-4A-2_data.xls", skiprows=7)
    # df2 = pd.read_excel("/root/covid_21-09-17.xlsx")

    # 判定是何種機台
    if 'CTFAIL' and 'THOLDFAIL' and 'EXPFAIL' in df.columns:
        print("sds7500")
        machine = 1
    else:
        print("MA-6000")
        machine = 2

    # 判定是何種試劑
    if machine == 1:
        target_list = df["Target Name"].drop_duplicates().values.tolist()
        if "N" and "ORF1ab" and "RNase P" in target_list:
            Reagent_type = 1
            print("伯杰")
        elif "IR-RNase P" and "N gene" and "ORF1ab gene" in target_list:
            Reagent_type = 2
            print("明德")
        else:
            Reagent_type = 3
            print("判別失敗")

        # covid-19判別陰陽性演算法
        if Reagent_type == 1:
            df.columns = [['Well', 'Sample Name', 'Target Name', 'Task',
                           'Reporter', 'Quencher', 'CT', 'CTMean', 'CTSD', 'Quantity',
                           'Quantity Mean', 'Quantity SD', 'Automatic CTThreshold',
                           'CTThreshold', 'Automatic Baseline', 'Baseline Start', 'Baseline End',
                           'Comments', 'AMPNC', 'HIGHSD', 'EXPFAIL', 'THOLDFAIL', 'CTFAIL']]
            ct_list = []
            for i in df["CT"].index:
                i = i + 1
                if i % 3 == 0:
                    print(i)
                    print(df["CT"].iloc[i - 3:i].values.tolist())
                    ct_list.append(df["CT"].iloc[i - 3:i].values.tolist())
            # print(ct_list)
            result_list = []
            for i in range(0, len(ct_list)):
                N = ct_list[i][0][0]
                ORF = ct_list[i][1][0]
                RN = ct_list[i][2][0]
                # print(IR, N, P)

            # 伯杰試劑
                try:
                    if RN < 45:
                        a = 1
                    else:
                        a = 0
                except:
                    a = 0
                    #         print(a)
                    #         print(IR, N, P)
                try:
                    if N <= 40 and ORF <= 40:
                        b = 1
                    elif N > 40 and ORF > 40:
                        b = 0
                    else:
                        b = "重檢"
                except:
                    b = "Undetermined"
                print(a, b)
                if a == 1 and b == 1:
                    result = "陽性"
                elif a == 1 and b == 0:
                    result = "陰性"
                elif a == 0 or b == "重檢":
                    result = "重檢"
                else:
                    result = "error"
                print(result)
                result_list.append(result)
            print(result_list)
            df_result = pd.DataFrame()
            df_result["Well"] = df.Well.drop_duplicates()
            df_result["if_covid"] = result_list
            print(df_result)
        elif Reagent_type == 2:
            df = df.drop([0,28,29])
            df.columns = [['Sample Name', 'Well', 'Sample Name.1', 'Target Name', 'Task',
                           'Reporter', 'Quencher', 'CT', 'CTMean', 'CTSD', 'Quantity',
                           'Quantity Mean', 'Quantity SD', 'Automatic CTThreshold',
                           'CTThreshold', 'Automatic Baseline', 'Baseline Start', 'Baseline End',
                           'Comments', 'HIGHSD', 'EXPFAIL']]
            df.reset_index(drop=True, inplace=True)
            ct_list = []
            for i in df["CT"].index:
                i = i + 1
                if i % 3 == 0:
                    print(i)
                    print(df["CT"].iloc[i - 3:i].values.tolist())
                    ct_list.append(df["CT"].iloc[i - 3:i].values.tolist())
            # print(ct_list)
            result_list = []
            for i in range(0, len(ct_list)):
                IR = ct_list[i][0][0]
                N = ct_list[i][1][0]
                P = ct_list[i][2][0]
                # print(IR, N, P)

            # 明德試劑
                try:
                    if IR < 35:
                        a = 1
                    else:
                        a = 0
                except:
                    a = 0
                    #         print(a)
                    #         print(IR, N, P)
                try:
                    if N < 38 and P < 38:
                        b = 1
                    elif N >= 40 and P >= 40:
                        b = 0
                    else:
                        b = "重檢"
                except:
                    b = "Undetermined"
                print(a, b)
                if a == 1 and b == 1:
                    result = "陽性"
                elif a == 1 and b == 0:
                    result = "陰性"
                elif a == 0 or b == "重檢":
                    result = "重檢"
                else:
                    result = "error"
                print(result)
                result_list.append(result)
            print(result_list)
            df_result = pd.DataFrame()
            df_result["Well"] = df.Well.drop_duplicates()
            df_result["if_covid"] = result_list
            print(df_result)
    else:
        pass
    return df_result


def if_covid_sds7500():
    df = pd.read_excel("/root/sds7500 boji.xls", skiprows=7)
    target_list = df["Target Name"].drop_duplicates().values.tolist()

    # 判別試劑
    if "N" and "ORF1ab" and "RNase P" in target_list:
        Reagent_type = 1
        print("伯杰")
    elif "IR-RNase P" and "N gene" and "ORF1ab gene" in target_list:
        Reagent_type = 2
        print("明德")
    else:
        Reagent_type = 3
        print("判別失敗")

    # covid-19判別陰陽性演算法
    if Reagent_type == 1:
        df.columns = [['Well', 'Sample Name', 'Target Name', 'Task',
                       'Reporter', 'Quencher', 'CT', 'CTMean', 'CTSD', 'Quantity',
                       'Quantity Mean', 'Quantity SD', 'Automatic CTThreshold',
                       'CTThreshold', 'Automatic Baseline', 'Baseline Start', 'Baseline End',
                       'Comments', 'AMPNC', 'HIGHSD', 'EXPFAIL', 'THOLDFAIL']]
        ct_list = []
        for i in df["CT"].index:
            i = i + 1
            if i % 3 == 0:
                # print(i)
                # print(df["CT"].iloc[i - 3:i].values.tolist())
                ct_list.append(df["CT"].iloc[i - 3:i].values.tolist())
        # print(ct_list)
        result_list = []
        for i in range(0, len(ct_list)):
            N = ct_list[i][0][0]
            ORF = ct_list[i][1][0]
            RN = ct_list[i][2][0]
            # print(IR, N, P)

        # 伯杰試劑
            try:
                if RN < 45:
                    a = 1
                else:
                    a = 0
            except:
                a = 0
                #         print(a)
                #         print(IR, N, P)
            try:
                if N <= 40 and ORF <= 40:
                    b = 1
                elif N > 40 and ORF > 40:
                    b = 0
                else:
                    b = "重檢"
            except:
                b = 0
            # print(a, b)
            if a == 1 and b == 1:
                result = "陽性"
            elif a == 1 and b == 0:
                result = "陰性"
            elif a == 0 or b == "重檢":
                result = "重檢"
            else:
                result = "error"
            # print(result)
            result_list.append(result)
        # print(result_list)
        df_result = pd.DataFrame()
        df_result["Well"] = df.Well.drop_duplicates()
        df_result["if_covid"] = result_list
        print(df_result)
        df_result.to_excel("if_covid_7500.xlsx", index=False)
    elif Reagent_type == 2:
        df.columns = [['Well', 'Sample Name', 'Target Name', 'Task',
                       'Reporter', 'Quencher', 'CT', 'CTMean', 'CTSD', 'Quantity',
                       'Quantity Mean', 'Quantity SD', 'Automatic CTThreshold',
                       'CTThreshold', 'Automatic Baseline', 'Baseline Start', 'Baseline End',
                       'Comments', 'AMPNC', 'HIGHSD', 'EXPFAIL', 'THOLDFAIL']]
        ct_list = []
        for i in df["CT"].index:
            i = i + 1
            if i % 3 == 0:
                # print(i)
                # print(df["CT"].iloc[i - 3:i].values.tolist())
                ct_list.append(df["CT"].iloc[i - 3:i].values.tolist())
        # print(ct_list)
        result_list = []
        for i in range(0, len(ct_list)):
            IR = ct_list[i][0][0]
            N = ct_list[i][1][0]
            P = ct_list[i][2][0]
            # print(IR, N, P)

        # 明德試劑
            try:
                if IR < 35:
                    a = 1
                else:
                    a = 0
            except:
                a = 0
                #         print(a)
                #         print(IR, N, P)
            try:
                if N < 38 and P < 38:
                    b = 1
                elif N >= 40 and P >= 40:
                    b = 0
                else:
                    b = "重檢"
            except:
                b = 0
            # print(a, b)
            if a == 1 and b == 1:
                result = "陽性"
            elif a == 1 and b == 0:
                result = "陰性"
            elif a == 0 or b == "重檢":
                result = "重檢"
            else:
                result = "error"
            # print(result)
            result_list.append(result)
        # print(result_list)
        df_result = pd.DataFrame()
        df_result["Well"] = df.Well.drop_duplicates()
        df_result["if_covid"] = result_list
        print(df_result)
        df_result.to_excel("if_covid_7500.xlsx", index=False)
        return df_result


def if_covid_MA6000():
    df = pd.read_excel("/root/20210924-15B-BJ-MA6000.xls", skiprows=21)
    df_data = pd.read_excel("/root/20210924-15B-BJ-MA6000.xls", sheet_name="Data&Graph", skiprows=1)
    TargetItem = df["Item"].drop_duplicates()[0]

    # 判別試劑
    if TargetItem == 'BJ':
        Reagent_type = 1
        print("伯杰")
    elif TargetItem == 'MDSW':
        Reagent_type = 2
        print("明德")
    else:
        Reagent_type = 3
        print("判別失敗")


    # covid-19判別陰陽性演算法
    if Reagent_type == 1:
        ct_list = []
        print(df_data)
        print(df_data.Ct)
    #     for i in df["CT"].index:
    #         i = i + 1
    #         if i % 3 == 0:
    #             print(i)
    #             print(df["CT"].iloc[i - 3:i].values.tolist())
    #             ct_list.append(df["CT"].iloc[i - 3:i].values.tolist())
    #     # print(ct_list)
    #     result_list = []
    #     for i in range(0, len(ct_list)):
    #         N = ct_list[i][0][0]
    #         ORF = ct_list[i][1][0]
    #         RN = ct_list[i][2][0]
    #         # print(IR, N, P)
    #
    #         # 伯杰試劑
    #         try:
    #             if RN < 45:
    #                 a = 1
    #             else:
    #                 a = 0
    #         except:
    #             a = 0
    #             #         print(a)
    #             #         print(IR, N, P)
    #         try:
    #             if N <= 40 and ORF <= 40:
    #                 b = 1
    #             elif N > 40 and ORF > 40:
    #                 b = 0
    #             else:
    #                 b = "重檢"
    #         except:
    #             b = "Undetermined"
    #         print(a, b)
    #         if a == 1 and b == 1:
    #             result = "陽性"
    #         elif a == 1 and b == 0:
    #             result = "陰性"
    #         elif a == 0 or b == "重檢":
    #             result = "重檢"
    #         else:
    #             result = "error"
    #         print(result)
    #         result_list.append(result)
    #     print(result_list)
    #     df_result = pd.DataFrame()
    #     df_result["Well"] = df.Well.drop_duplicates()
    #     df_result["if_covid"] = result_list
    #     print(df_result)
    # elif Reagent_type == 2:
    #     df.columns = [['Well', 'Sample Name', 'Target Name', 'Task',
    #                    'Reporter', 'Quencher', 'CT', 'CTMean', 'CTSD', 'Quantity',
    #                    'Quantity Mean', 'Quantity SD', 'Automatic CTThreshold',
    #                    'CTThreshold', 'Automatic Baseline', 'Baseline Start', 'Baseline End',
    #                    'Comments', 'AMPNC', 'HIGHSD', 'EXPFAIL', 'THOLDFAIL']]
    #     ct_list = []
    #     for i in df["CT"].index:
    #         i = i + 1
    #         if i % 3 == 0:
    #             print(i)
    #             print(df["CT"].iloc[i - 3:i].values.tolist())
    #             ct_list.append(df["CT"].iloc[i - 3:i].values.tolist())
    #     # print(ct_list)
    #     result_list = []
    #     for i in range(0, len(ct_list)):
    #         IR = ct_list[i][0][0]
    #         N = ct_list[i][1][0]
    #         P = ct_list[i][2][0]
    #         # print(IR, N, P)
    #
    #         # 明德試劑
    #         try:
    #             if IR < 35:
    #                 a = 1
    #             else:
    #                 a = 0
    #         except:
    #             a = 0
    #             #         print(a)
    #             #         print(IR, N, P)
    #         try:
    #             if N < 38 and P < 38:
    #                 b = 1
    #             elif N >= 40 and P >= 40:
    #                 b = 0
    #             else:
    #                 b = "重檢"
    #         except:
    #             b = "Undetermined"
    #         print(a, b)
    #         if a == 1 and b == 1:
    #             result = "陽性"
    #         elif a == 1 and b == 0:
    #             result = "陰性"
    #         elif a == 0 or b == "重檢":
    #             result = "重檢"
    #         else:
    #             result = "error"
    #         print(result)
    #         result_list.append(result)
    #     print(result_list)
    #     df_result = pd.DataFrame()
    #     df_result["Well"] = df.Well.drop_duplicates()
    #     df_result["if_covid"] = result_list
    #     print(df_result)
    #     return df_result


def color_dataframe(val):
    if val == "陽性":
        color = 'red'
    elif val == "重檢":
        color = 'green'
    else:
        color = 'black'
    return 'background-color: %s' % color


def create_client():
    df = pd.read_excel("/root/covid_21-09-16_reserve.xlsx",converters={'送件單位id':str})
    df_client = df[["送件單位", "送件單位id"]]
    df_client.columns = [["Name", "ClientID"]]
    df_client = df_client.drop_duplicates()
    print(df_client)
    for i in df_client.index:
        data = df_client.loc[i].to_dict()
        for key,value in data.items():
            if ''.join(key)=="Name":
                name = value
            elif ''.join(key)=="ClientID":
                client = value
        url = 'http://192.168.11.21/api/client/{}/{}'.format(name,client)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        print(result)


def create_contact(df, df_clientID):
    df_contact = df[["中文名", "UUID", "手機", "Email", "性別", "送件單位id"]]
    df_contact.columns = ["Name", "ContactID", "Phone", "Email", "Sex", "ClientID"]
    df_contact.Sex = df_contact.Sex.str.split(' /', expand=True)[0]
    print(df_contact)
    df_export = pd.merge(df_contact, df_clientID, on='ClientID')
    print(df_export)
    df_contactID = pd.DataFrame()
    contactID_list = []
    contact_uuid_list = []
    for i in df_export.index:
        data = df_export.loc[i].to_dict()
        for key, value in data.items():
            if ''.join(key) == "Name":
                name = value
            elif ''.join(key) == "ContactID":
                contactID = value
            elif ''.join(key) == "Phone":
                phone = value
            elif ''.join(key) == "Email":
                email = value
            elif ''.join(key) == "Sex":
                sex = value
            elif ''.join(key) == "ClientID":
                clientID = value
                df_filter = df_clientID.ClientID == clientID
                print(df_filter)
                client_seq = df_clientID[df_filter]["Client_seq"].values[0]
                print(client_seq)
                url = 'http://192.168.11.21/api/contact/{}/{}/{}/{}/{}/{}'.format(client_seq, name, sex, contactID,
                                                                                   phone, email)
                print(url)
                result = requests.post(url, cookies=reslogin.cookies, headers=headers)
                print(result.json())
                contact_uuid = result.json()["items"][0]["uid"]
                contact_id = result.json()["items"][0]["Username"]
                print("contact_id", contact_id)
                print("contact_uuid", contact_uuid)
                contactID_list.append(contact_id)
                contact_uuid_list.append(contact_uuid)
    df_contactID['ContactID'] = contactID_list
    df_contactID['Contact_uuid'] = contact_uuid_list
    print(df_contactID)
    df_export = pd.merge(df_export, df_contactID, on='ContactID')
    print(df_export)


def create_sample(df_export):
    df_sampleID = pd.DataFrame()
    contact_uuid_list = []
    sample_uuid_list = []
    for i in df_export.index:
        client_uuid = df_export.loc[i, "Client_uuid"]
        contact_uuid = df_export.loc[i, "Contact_uuid"]
        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format(client_uuid, contact_uuid,
                                                                             '72ee86eeed68455fbcbf05ce7d7e1d8a', None,
                                                                             None, None,
                                                                             None)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        print(result.json())
        sample_uuid = result.json()["items"][0]["uid"]
        contact_uuid_list.append(contact_uuid)
        sample_uuid_list.append(sample_uuid)
        print(sample_uuid)
    df_sampleID["Contact_uuid"] = contact_uuid_list
    df_sampleID["Sample_uuid"] = sample_uuid_list
    print(df_sampleID)
    df_export = pd.merge(df_export, df_sampleID, on='Contact_uuid')
    print(df_export)


def import_machine():
    df = pd.read_excel("/root/covid_21-09-17.xlsx", skiprows=7)
    df.columns = [['Sample Name', 'Well', 'Sample Name.1', 'Target Name', 'Task',
                   'Reporter', 'Quencher', 'CT', 'CTMean', 'CTSD', 'Quantity',
                   'Quantity Mean', 'Quantity SD', 'Automatic CTThreshold',
                   'CTThreshold', 'Automatic Baseline', 'Baseline Start', 'Baseline End',
                   'Comments', 'HIGHSD', 'EXPFAIL']]
    df2 = pd.read_excel("/root/covid_21-09-17.xlsx")
    contact = df2.iloc[0, 2]
    sampler = df2.iloc[3, 2]
    contactList = [contact for i in range(0, df.shape[0])]
    samplertList = [sampler for i in range(0, df.shape[0])]
    df["contact"] = contactList
    df["sampler"] = samplertList
    dateSample = df2.iloc[2, 2].split()[0:2]
    dateSample = ' '.join(dateSample)
    dateSampleList = [dateSample for i in range(0, df.shape[0])]
    df["dateSample"] = dateSampleList
    Target_list = df['Target Name'].values.tolist()
    Target_id = []
    for i in Target_list:
        if i[0] == "IR-RNase P":
            i[0] = "fce5bfec4ea8477b96f1b1fc89f98eae"
        if i[0] == "N gene":
            i[0] = "43018dc8d11e488a965eb41d3975ebca"
        if i[0] == "ORF1ab gene":
            i[0] = "324cf9ee575f47b5af1504c4b1b5f980"
        Target_id.append(i[0])
    df["Target id"] = Target_id
    contact_list = df["contact"].values.tolist()
    contact_id = []
    for i in contact_list:
        if i[0] == "TAQMAN":
            i[0] = "e79738012a1142c182b0b39374947cfd"
        contact_id.append(i[0])
    df["contact id"] = contact_id
    df_sample = df[["dateSample", "CT", "contact id", "Target id", "Sample Name", "sampler"]]
    print(df_sample)

    for i in df_sample.index:
        data = df_sample.loc[i].to_dict()
        for key,value in data.items():
            if ''.join(key) == "dateSample":
                dateSample = value
            elif ''.join(key) == "CT":
                CT = value
            elif ''.join(key) == "contact id":
                contact_id = value
            elif ''.join(key) == "Target id":
                target_id = value
            elif ''.join(key) == "Sample Name":
                clientordernumber = value
            elif ''.join(key) == "sampler":
                clientsampleID = value

        url = 'http://192.168.11.21/api/sample/{}/{}/{}/{}/{}/{}/{}'.format('4e22a544d58642dabbc8b55b2b087a12', contact_id, target_id, dateSample, CT, clientordernumber, clientsampleID)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers)
        print(result)


def firsttype_report():
    sql_cmd = 'select * from public."all_sample_data"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    contact_id_list = df_id["Contact_uuid"].values.tolist()
    sample_id_list = df_id["Sample_uuid"].values.tolist()

    # first type report
    df_firsttype = pd.DataFrame(columns=["seq", "userid", "username", "engname", "gender", "age", "sampleid", "sampletime"
        , "receivetime", "Mobile", "sendername", "passportid", "sampletype", "reporttime", "reportype", "inspector"
        , "birth", "inspectcompany", "equipment", "result", "resultinterval", "remark", "yy", "mm", "dd", "hh", "min"
        , "gendereng", "sampletypeeng", "inspectcompanyeng", "sendernameeng"])

    # load contact data
    for i, contact_id in enumerate(contact_id_list):
        print(i, contact_id)
        contact_data = load_sql(contact_id)
        print(contact_data["title"].split()[0])
        df_firsttype.loc[i] = [i+1, None, contact_data["title"].split()[0], None, contact_data["title"].split()[1], None, None, None
            , None, contact_data["MobilePhone"], None, None, None, None, None, None
            , None, None, None, None, None, None, None, None, None, None, None
            , None, None, None, None]

    # load sample data
    for i, sample_id in enumerate(sample_id_list):
        print(i, sample_id)
        sample_data = load_sql(sample_id)
        print(sample_data["title"])

    print(df_firsttype)
    df_firsttype.to_excel("report1.xlsx", index=False)


def secondtype_report():
    sql_cmd = 'select * from public."report_test"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    contact_id_list = df_id["Contact_uuid"].values.tolist()
    # sample_id_list = df_id["Sample_uuid"].values.tolist()

    # second type report
    df_secondtype = pd.DataFrame(
        columns=["【序号】", "【身份证号】", "【姓名】", "【英文姓名】", "【性别】", "【年龄】", "【样本条码】", "【采样时间】"
            , "【接收时间】", "【手机号】", "【送检单位】", "【护照号】", "【样本类型】", "【报告时间】", "【出生日期】", "【采样单位】"
            , "【检测仪器】", "【检测结果】", "【参考区间】", "【remark】"])

    for i, contact_id in enumerate(contact_id_list):
        print(i, contact_id)
        contact_data = load_sql(contact_id)
        # print(contact_data["title"].split()[0])
        df_secondtype.loc[i] = [i+1, contact_data["Salutation"], contact_data["Firstname"], None, contact_data["Surname"].split()[0], contact_data["Surname"].split()[1], None, None
            , None, contact_data["MobilePhone"], contact_data["Department"], contact_data["Username"], None, None, contact_data["JobTitle"], None
            , None, None, None, None]

    # load sample data
    # for i, sample_id in enumerate(sample_id_list):
    #     print(i, sample_id)
    #     sample_data = load_sql(sample_id)
    #     print(sample_data["title"])

    print(df_secondtype)
    df_secondtype.to_excel("report2.xlsx", index=False)


def firsttype_report2():
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    sql_cmd = 'select * from public."back_stage_report_reserve_sample_test"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    contact_id_list = df_id["Contact_uuid"].values.tolist()
    sample_id_list = df_id["Sample_uuid"].values.tolist()

    # first type report
    df_firsttype = pd.DataFrame(columns=["seq", "userid", "username", "engname", "gender", "age", "sampleid", "sampletime"
        , "receivetime", "Mobile", "sendername", "passportid", "sampletype", "reporttime", "reportype", "inspector"
        , "birth", "inspectcompany", "equipment", "result", "resultinterval", "remark", "yy", "mm", "dd", "hh", "min"
        , "gendereng", "sampletypeeng", "inspectcompanyeng", "sendernameeng"])

    # load contact data
    for i, contact_id in enumerate(contact_id_list):
        print(i, contact_id)
        contact_data = load_sql(contact_id)
        print(contact_data["title"].split()[0])
        df_firsttype.loc[i] = [i+1, contact_data["Salutation"], contact_data["Firstname"], None, contact_data["Middlename"], contact_data["Surname"], None, None
            , None, contact_data["MobilePhone"], contact_data["Department"], contact_data["Username"], None, now, None, None
            , contact_data["JobTitle"], "丽宝生医", None, None, None, None, None, None, None, None, None
            , contact_data["Middlename"], None, "丽宝生医", contact_data["Department"]]

    # load sample data
    for i, sample_id in enumerate(sample_id_list):
        print(i, sample_id)
        sample_data = load_sql(sample_id)
        df_firsttype.loc[i, "sampleid"] = sample_data["title"]
        print(sample_data["title"])

    print(df_firsttype)
    df_firsttype.to_excel("report1.xlsx", index=False)


def secondtype_report2():
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    sql_cmd = 'select * from public."report_reserve_sample"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    contact_id_list = df_id["Contact_uuid"].values.tolist()
    sample_id_list = df_id["Sample_uuid"].values.tolist()

    # second type report
    df_secondtype = pd.DataFrame(
        columns=["【序号】", "【身份证号】", "【姓名】", "【英文姓名】", "【性别】", "【年龄】", "【样本条码】", "【采样时间】"
            , "【接收时间】", "【手机号】", "【送检单位】", "【护照号】", "【样本类型】", "【报告时间】", "【出生日期】", "【采样单位】"
            , "【检测仪器】", "【检测结果】", "【参考区间】", "【remark】"])

    for i, contact_id in enumerate(contact_id_list):
        print(i, contact_id)
        contact_data = load_sql(contact_id)
        print(contact_data)
        print(contact_data["title"].split()[0])
        df_secondtype.loc[i] = [i+1, contact_data["Salutation"], contact_data["Firstname"], None, contact_data["Middlename"], contact_data["Surname"], None, None
            , None, contact_data["MobilePhone"], contact_data["Department"], contact_data["Username"], None, now, contact_data["JobTitle"], "丽宝生医"
            , None, None, None, None]

    # load sample data
    for i, sample_id in enumerate(sample_id_list):
        print(i, sample_id)
        sample_data = load_sql(sample_id)
        df_secondtype.loc[i, "【样本条码】"] = sample_data["title"]
        print(sample_data["title"])

    print(df_secondtype)
    df_secondtype.to_excel("report2.xlsx", index=False)


def firsttype_report_post(**result_dict):
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    contact_uuid_list = []
    sample_uuid_list = []
    for key, value in result_dict.items():
        value = eval(value)
        contact_uuid_list.append(value[0])
        sample_uuid_list.append(value[1])
    print(contact_uuid_list)
    print(sample_uuid_list)

    # first type report
    df_firsttype = pd.DataFrame(columns=["seq", "userid", "username", "engname", "gender", "age", "sampleid", "sampletime"
        , "receivetime", "Mobile", "sendername", "passportid", "sampletype", "reporttime", "reportype", "inspector"
        , "birth", "inspectcompany", "equipment", "result", "resultinterval", "remark", "yy", "mm", "dd", "hh", "min"
        , "gendereng", "sampletypeeng", "inspectcompanyeng", "sendernameeng"])

    # load contact data
    for i, contact_id in enumerate(contact_uuid_list):
        print(i, contact_id)
        contact_data = load_sql(contact_id)
        print(contact_data["title"].split()[0])
        df_firsttype.loc[i] = [i+1, contact_data["Salutation"], contact_data["Firstname"], None, contact_data["Middlename"], contact_data["Surname"], None, None
            , None, contact_data["MobilePhone"], contact_data["Department"], contact_data["Username"], None, now, None, None
            , contact_data["JobTitle"], "丽宝生医", None, None, None, None, None, None, None, None, None
            , contact_data["Middlename"], None, "丽宝生医", contact_data["Department"]]

    # load sample data
    for i, sample_id in enumerate(sample_uuid_list):
        print(i, sample_id)
        sample_data = load_sql(sample_id)
        df_firsttype.loc[i, "sampleid"] = sample_data["title"]
        print(sample_data["title"])

    print(df_firsttype)
    df_firsttype.to_excel("report1.xlsx", index=False)


from googletrans import Translator


def trans_test():
    # Initial
    translator = Translator()
    # translate_text = translator.translate('apple', lang_src='en', dest='zh-CN')
    # translate_text = translator.translate('apple', lang_src='en', dest='zh-TW')
    translate_text = translator.translate('apple', lang_src='en', dest='ja')
    print(translate_text.text)


def secondtype_report_lan_test():
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    sql_cmd = 'select * from public."report_reserve_sample"'
    df_id = pd.read_sql(sql=sql_cmd, con=engine)
    contact_id_list = df_id["Contact_uuid"].values.tolist()
    sample_id_list = df_id["Sample_uuid"].values.tolist()

    # second type report
    df_secondtype = pd.DataFrame(
        columns=["【序号】", "【身份证号】", "【姓名】", "【英文姓名】", "【性别】", "【年龄】", "【样本条码】", "【采样时间】"
            , "【接收时间】", "【手机号】", "【送检单位】", "【护照号】", "【样本类型】", "【报告时间】", "【出生日期】", "【采样单位】"
            , "【检测仪器】", "【检测结果】", "【参考区间】", "【remark】"])

    for i, contact_id in enumerate(contact_id_list):
        print(i, contact_id)
        contact_data = load_sql(contact_id)
        print(contact_data)
        print(contact_data["title"].split()[0])
        df_secondtype.loc[i] = [i+1, contact_data["Salutation"], contact_data["Firstname"], None, contact_data["Middlename"], contact_data["Surname"], None, None
            , None, contact_data["MobilePhone"], contact_data["Department"], contact_data["Username"], None, now, contact_data["JobTitle"], "丽宝生医"
            , None, None, None, None]

    # load sample data
    for i, sample_id in enumerate(sample_id_list):
        print(i, sample_id)
        sample_data = load_sql(sample_id)
        df_secondtype.loc[i, "【样本条码】"] = sample_data["title"]
        print(sample_data["title"])

    print(df_secondtype)
    # df_secondtype.to_excel("report2.xlsx", index=False)


def load_sql(uid):
    url = 'http://192.168.11.21/api/{}'.format(uid)
    result = requests.get(url, cookies=reslogin.cookies, headers=headers)
    print(result.json())
    return result.json()


# create_nocontact_barcode("个人", 5)
# import_custdata()
# single_report("20211111-3C")
# single_batch_list()
# muti_report(**{'batch': ['20211111-2B']})
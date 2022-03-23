import json

from flask import Blueprint
from .load_excel import reserve_sample, nonreserve_sample, batch_well_Xiamen, sample_update, secondtype_report_post, \
    reserve_sample_report, nonreserve_sample_report, sample_update_new, if_covid_sds7500, cust_data_polling, \
    create_nocontact_barcode, import_custdata, update_contact_polling_info, update_barcode_contact_info, \
    update_sample_result, single_batch_list, single_report, muti_report
from flask import request

app_chatbot = Blueprint("webhook", __name__)


@app_chatbot.route("/", methods=['get'])
def first_type_report():
    return 'test'


@app_chatbot.route("/reserveSample", methods=['get'])
def reserveSample():
    reserve_sample()
    return 'reserveSample'


@app_chatbot.route("/nonreserveSample", methods=['get'])
def nonreserveSample():
    nonreserve_sample()
    return 'nonreserveSample'


@app_chatbot.route("/batch_well_Xiamen", methods=['get'])
def batchWellXiamen():
    batch_well_Xiamen()
    return 'batchWellXiamen'


@app_chatbot.route("/sampleUpdate", methods=['get'])
def sampleUpdate():
    sample_update()
    return 'sampleUpdate'


@app_chatbot.route("/secondtype_report_post", methods=['post'])
def secondtypeReportPost():
    result = request.get_json(silent=True, force=True)
    print(result)
    # contact_uuid_list = []
    # sample_uuid_list = []
    # for key, value in result.items():
    #     value = eval(value)
    #     contact_uuid_list.append(value[0])
    #     sample_uuid_list.append(value[1])
    # print(contact_uuid_list)
    # print(sample_uuid_list)
    msg = secondtype_report_post(**result)
    return msg


@app_chatbot.route("/reserve_sample_report", methods=['get'])
def reserveSampleReport():
    reserve_sample_report()
    return 'reserveSampleReport'


@app_chatbot.route("/nonreserve_sample_report", methods=['get'])
def nonreserveSampleReport():
    nonreserve_sample_report()
    return 'nonreserveSampleReport'


@app_chatbot.route("/sample_update_new", methods=['get'])
def sampleUpdateNew():
    sample_update_new()
    return 'sampleUpdateNew'


@app_chatbot.route("/if_covid_sds7500", methods=['get'])
def ifCovidSds7500():
    if_covid_sds7500()
    return 'ifCovidSds7500'


@app_chatbot.route("/cust_data_polling", methods=['get'])
def custDataPolling():
    data_num = cust_data_polling()
    return data_num


@app_chatbot.route("/createNocontactBarcode", methods=['post'])
def createNocontactBarcode():
    result = request.get_json(silent=True, force=True)
    print(result)
    barcode_dict = create_nocontact_barcode(**result)
    print(barcode_dict)
    return barcode_dict


@app_chatbot.route("/importCustdata", methods=['get'])
def importCustdata():
    data_num = import_custdata()
    return data_num


@app_chatbot.route("/updateContactPollingInfo", methods=['get'])
def updateContactPollingInfo():
    data_num = update_contact_polling_info()
    return data_num


@app_chatbot.route("/updateBarcodeContactInfo", methods=['get'])
def updateBarcodeContactInfo():
    data_num = update_barcode_contact_info()
    return data_num


@app_chatbot.route("/updateSampleResult", methods=['get'])
def updateSampleResult():
    data_num = update_sample_result()
    return data_num


@app_chatbot.route("/singleBatchList", methods=['get'])
def singleBatchList():
    result = single_batch_list()
    return result


@app_chatbot.route("/singleReport", methods=['post'])
def singleReport():
    result = request.get_json(silent=True, force=True)
    print(result)
    msg = single_report(**result)
    return msg


@app_chatbot.route("/mutiReport", methods=['post'])
def mutiReport():
    result = request.get_json(silent=True, force=True)
    print(result)
    msg = muti_report(**result)
    return msg
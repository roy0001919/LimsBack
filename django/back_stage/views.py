from django.shortcuts import render,HttpResponse
from .models import report_reserve_sample_test
import requests
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse


@login_required
def generateBarcode(request):
    # print("generateBarcode")
    if request.method == 'GET':
        return render(request, 'myweb/generateBarcode.html',{

        })
    elif request.method == 'POST':
        cilentName = request.POST["clientName"]
        number = request.POST["number"]
        data_dict = {
            "clientName": cilentName,
            "number": number
        }
        url = "http://192.168.11.21/createNocontactBarcode"
        result = requests.post(url, json=data_dict)
        print(result.json())
        return render(request, 'myweb/generateBarcode.html', {
            "data": result.json()
        })


@login_required
def nonreserveSample(request):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST, request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
        return render(request, 'myweb/nonreserveSample_uploaded.html', {
            'forms': forms, "error_msg": error_msg
        })
    else:
        forms = FileUploadForm()
        return render(request, 'myweb/nonreserveSample.html', {
            'forms': forms, "error_msg": error_msg
        })


@login_required
def nonreserveFunc(request):
    url = "http://192.168.11.21/importCustdata"
    result = requests.get(url)
    print(result.text)
    return render(request, 'myweb/submit.html', {
        "data_num": result.text
    })


@login_required
def contactPolling(request):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST, request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
        return render(request, 'myweb/contactPolling_uploaded.html', {
            'forms': forms, "error_msg": error_msg
        })
    else:
        forms = FileUploadForm()
        return render(request, 'myweb/contactPolling.html', {
            'forms': forms, "error_msg": error_msg
        })


@login_required
def contactPollingFunc(request):
    url = "http://192.168.11.21/updateContactPollingInfo"
    result = requests.get(url)
    print(result.text)
    return render(request, 'myweb/submit.html', {
        "data_num": result.text
    })


@login_required
def update_barcode_contact_info(request):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST, request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
        return render(request, 'myweb/update_barcode_contact_info_uploaded.html', {
            'forms': forms, "error_msg": error_msg
        })
    else:
        forms = FileUploadForm()
        return render(request, 'myweb/update_barcode_contact_info.html', {
            'forms': forms, "error_msg": error_msg
        })


@login_required
def update_barcode_contact_infoFunc(request):
    url = "http://192.168.11.21/updateBarcodeContactInfo"
    result = requests.get(url)
    print(result.text)
    return render(request, 'myweb/submit.html', {
        "data_num": result.text
    })


@login_required
def update_sample_result(request):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST, request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
        return render(request, 'myweb/update_sample_result_uploaded.html', {
            'forms': forms, "error_msg": error_msg
        })
    else:
        forms = FileUploadForm()
        return render(request, 'myweb/update_sample_result.html', {
            'forms': forms, "error_msg": error_msg
        })


@login_required
def update_sample_resultFunc(request):
    url = "http://192.168.11.21/updateSampleResult"
    result = requests.get(url)
    print(result.text)
    return render(request, 'myweb/submit.html', {
        "data_num": result.text
    })


@login_required
def single_report(request):
    if request.method == 'GET':
        url = "http://192.168.11.21/singleBatchList"
        result = requests.get(url)
        return render(request, 'myweb/singleReport.html', {
            "data": result.json()
        })
    elif request.method == 'POST':
        batch_list = list(request.POST.lists())[0][1]
        print(batch_list)
        url = "http://192.168.11.21/singleReport"
        batch_dict = {}
        batch_dict["batch"] = batch_list
        print(batch_dict)
        result = requests.post(url, json=batch_dict)
        print(result.json())
        batch_ID = batch_list[0]
        file = open('/root/{}.csv'.format(batch_ID), 'rb')
        print(batch_ID)
        response = FileResponse(file)
        response["Content-Type"] = "application/octet-stream"  # 設定頭資訊，告訴瀏覽器這是個檔案
        response["Content-Disposition"] = "attachment; filename={}.csv".format(batch_ID)
        return response


@login_required
def muti_report(request):
    if request.method == 'GET':
        url = "http://192.168.11.21/singleBatchList"
        result = requests.get(url)
        return render(request, 'myweb/mutiReport.html', {
            "data": result.json()
        })
    elif request.method == 'POST':
        batch_list = list(request.POST.lists())[0][1]
        print(batch_list)
        url = "http://192.168.11.21/mutiReport"
        batch_dict = {}
        batch_dict["batch"] = batch_list
        print(batch_dict)
        result = requests.post(url, json=batch_dict)
        print(result.json())
        batch_ID = batch_list[0]
        file = open('C:/Users/roy.lo/PycharmProjects/Lims_Work/main/{}_muti.csv'.format(batch_ID), 'rb')
        print(batch_ID)
        response = FileResponse(file)
        response["Content-Type"] = "application/octet-stream"  # 設定頭資訊，告訴瀏覽器這是個檔案
        response["Content-Disposition"] = "attachment; filename={}.csv".format(batch_ID)
        return response


@login_required
def first_type_report(request):
    if request.method == 'GET':
        data = report_reserve_sample_test.objects.all()
        return render(request, 'myweb/report.html',{
            "data": data
        })
    elif request.method == 'POST':
        data = request.POST
        data_dict = {}
        print(data)
        for key, value in data.items():
            data_dict.update({key: value})
        data_dict.pop('csrfmiddlewaretoken')
        print(data_dict)
        url = "http://192.168.11.21/secondtype_report_post"
        result = requests.post(url, json=data_dict)
        print(result.text)
        file = open('/root/report2.xlsx', 'rb')
        response = FileResponse(file)
        response["Content-Type"] = "application/octet-stream"  # 設定頭資訊，告訴瀏覽器這是個檔案
        response["Content-Disposition"] = "attachment; filename=report2.xlsx"
        if result.text == "已匯出報表模板,無任何異常資料":
            return response
        else:
            import pyautogui
            pyautogui.alert(result.text)
            return response


@login_required
def filter(request):
    query_terms = request.POST["q"]
    print(query_terms)
    data = report_reserve_sample_test.objects.filter(ClientName=query_terms).all()
    if not data:
        data = report_reserve_sample_test.objects.filter(Name=query_terms).all()
        if not data:
            data = report_reserve_sample_test.objects.filter(Sample_id=query_terms).all()
            if not data:
                data = report_reserve_sample_test.objects.filter(ContactID=query_terms).all()
                if not data:
                    data = report_reserve_sample_test.objects.filter(DateSampled=query_terms).all()
                    if not data:
                        data = report_reserve_sample_test.objects.filter(SampleReceiveDate=query_terms).all()
                        if not data:
                            data = report_reserve_sample_test.objects.filter(Type=query_terms).all()
                            if not data:
                                data = report_reserve_sample_test.objects.filter(PID=query_terms).all()

    return render(request, 'myweb/filter.html', {
        "data": data
    })


def handle_uploaded_file(f):
    save_path = os.path.join('/root/', f.name)
    with open(save_path, 'wb+') as fp:
        for chunk in f.chunks():
            fp.write(chunk)


@csrf_exempt
def file_upload(request, *args, **kwargs):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST,request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
    else:
        forms = FileUploadForm()
    return render(request, 'myweb/base.html', {'forms': forms, "error_msg": error_msg})


@login_required
def reserveSample(request, *args, **kwargs):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST, request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
        return render(request, 'myweb/reserveSample_uploaded.html', {
            'forms': forms, "error_msg": error_msg
        })
    else:
        forms = FileUploadForm()
        return render(request, 'myweb/reserveSample.html', {
            'forms': forms, "error_msg": error_msg
        })


@login_required
def batchGraph(request):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST, request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
        return render(request, 'myweb/batchGraph_uploaded.html', {
            'forms': forms, "error_msg": error_msg
        })
    else:
        forms = FileUploadForm()
        return render(request, 'myweb/batchGraph.html', {
            'forms': forms, "error_msg": error_msg
        })


@login_required
def sampleImport(request):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST, request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
        return render(request, 'myweb/sampleImport_uploaded.html', {
            'forms': forms, "error_msg": error_msg
        })
    else:
        forms = FileUploadForm()
        return render(request, 'myweb/sampleImport.html', {
            'forms': forms, "error_msg": error_msg
        })


@login_required
def sampleImportFunc(request):
    print(request.POST["ma"])
    # url = "http://192.168.11.21/reserve_sample_report"
    # result = requests.get(url)
    # print(result.text)
    # return render(request, 'myweb/submit.html', {
    #
    # })

@login_required
def ifCovid(request):
    error_msg = ""
    if request.method == 'POST':
        forms = FileUploadForm(request.POST, request.FILES)
        if forms.is_valid():
            handle_uploaded_file(request.FILES['file'])
        error_msg = "異常"
        return render(request, 'myweb/ifCovid_uploaded.html', {
            'forms': forms, "error_msg": error_msg
        })
    else:
        forms = FileUploadForm()
        return render(request, 'myweb/ifCovid.html', {
            'forms': forms, "error_msg": error_msg
        })


@login_required
def reserveFunc(request):
    pass
    # url = "http://192.168.11.21/nonreserveSample"
    # result = requests.get(url)
    # print(result.text)
    # return render(request, 'myweb/submit.html', {
    #
    # })



@login_required
def batchGraphFunc(request):
    url = "http://192.168.11.21/batch_well_Xiamen"
    result = requests.get(url)
    print(result.text)
    url2 = "http://192.168.11.21/sample_update_new"
    result = requests.get(url2)
    print(result.text)
    file = open('/root/batch_graph.xlsx', 'rb')
    response = FileResponse(file)
    response["Content-Type"] = "application/octet-stream"  # 設定頭資訊，告訴瀏覽器這是個檔案
    response["Content-Disposition"] = "attachment; filename=batchGraph.xlsx"
    return response
    # return render(request, 'myweb/batchGraph_download.html', {
    #
    # })


@login_required
def queryReport(request):
    batch_ID = request.POST["q"]
    url = "http://192.168.11.21/singleReport"
    batch_dict = {}
    batch_dict["batch"] = batch_ID
    print(batch_dict)
    result = requests.post(url, json=batch_dict)
    print(result.json())
    file = open('/root/{}.csv'.format(batch_ID), 'rb')
    print(batch_ID)
    response = FileResponse(file)
    response["Content-Type"] = "application/octet-stream"  # 設定頭資訊，告訴瀏覽器這是個檔案
    response["Content-Disposition"] = "attachment; filename={}.csv".format(batch_ID)
    return response


@login_required
def ifCovidFunc(request):
    print(request.POST["ma"])
    if request.POST["ma"] == 'MA6000':
        pass
    elif request.POST["ma"] == 'sds7500':
        url = "http://192.168.11.21/if_covid_sds7500"
        result = requests.get(url)
        print(result.text)
        return render(request, 'myweb/ifCovid_download.html', {

        })


@login_required
def batchGraphDownload(request):
    file = open('/root/batch_graph.xlsx', 'rb')
    response = FileResponse(file)
    response["Content-Type"] = "application/octet-stream"  # 設定頭資訊，告訴瀏覽器這是個檔案
    response["Content-Disposition"] = "attachment; filename=batchGraph.xlsx"
    return response
    # return render(request, 'myweb/submit.html', {
    #
    # })


@login_required
def ifCovidDownload(request):
    file = open('/root/if_covid_7500.xlsx', 'rb')
    response = FileResponse(file)
    response["Content-Type"] = "application/octet-stream"  # 設定頭資訊，告訴瀏覽器這是個檔案
    response["Content-Disposition"] = "attachment; filename=if_covid_7500.xlsx"
    return response
    # return render(request, 'myweb/submit.html', {
    #
    # })


@login_required
def reportDownload(request):
    file = open('/root/report2.xlsx', 'rb')
    response = FileResponse(file)
    response["Content-Type"] = "application/octet-stream"  # 設定頭資訊，告訴瀏覽器這是個檔案
    response["Content-Disposition"] = "attachment; filename=report2.xlsx"
    return response


def get_file(request):
    with open('/root/20210924-15B-BJ-MA6000.xls') as f:
        c = f.read()
        return HttpResponse(c)
import requests
import json
from . import reslogin

headers = {'Content-Type': 'application/json'}


class IDfilter:

    def read(self,uid):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/{}".format(uid)
        result = requests.get(url, cookies=reslogin.cookies, headers=headers)
        return result.json()


class Clients:

    def create(self,data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/create"
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return result.json()

    def read(self):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/client"
        result = requests.get(url, cookies=reslogin.cookies,headers=headers)
        return result.json()

    def update(self,data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/update"
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return str(result)

    def delete(self, data):
        print(data)


class Contacts:
    def create(self, client_uuid, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/create/{}".format(client_uuid)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return result.json()

    def createReport(self, uid, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/create/{}".format(uid)
        print(url)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return result.json()

    def read(self):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/contact"
        result = requests.get(url, cookies=reslogin.cookies,headers=headers)
        return result.json()

    def update(self,data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/update"
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return str(result)

    def delete(self, data):
        print(data)


class Samples:

    def create(self, client_uuid, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/AnalysisRequest/create/{}".format(client_uuid)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return result.json()

    def read(self):
        print("read samples")
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/analysisrequest"
        result = requests.get(url, cookies=reslogin.cookies, headers=headers)
        return result.json()

    def update(self, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/update"
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return result.json()

    def delete(self, data):
        print(data)


class Batches:

    def create(self, client_uuid, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/batch/create/{}".format(client_uuid)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return result.json()

    def read(self):
        print("read batches")
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/batch"
        result = requests.get(url, cookies=reslogin.cookies, headers=headers)
        return result.json()

    def update(self, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/update"
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        return result.json()

    def delete(self, data):
        print(data)


class Worksheets:

    def create(worksheetID, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/worksheet/create/{}".format(worksheetID)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        print(result)

    def read():
        print("read worksheets")
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/worksheet"
        result = requests.get(url, cookies=reslogin.cookies,headers=headers)
        print(result.text)

    def update(self, data):
        pass
        
        # url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/update"
        # result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        # print(result)

    def delete(self, data):
        print(data)


class ReferenceSamples:

    def create(ReferencesampleID, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/referencesample/create/{}".format(ReferencesampleID)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        print(result)

    def read():
        print("read referencesamples")
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/referencesample"
        result = requests.get(url, cookies=reslogin.cookies,headers=headers)
        print(result.text)

    def update(data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/update"
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        print(result)

    def delete(self, data):
        print(data)


class Methods:

    def create(methodID, data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/method/create/{}".format(methodID)
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        print(result)

    def read():
        print("read methods")
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/method"
        result = requests.get(url, cookies=reslogin.cookies,headers=headers)
        print(result.text)

    def update(data):
        url = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/update"
        result = requests.post(url, cookies=reslogin.cookies, headers=headers, data=data)
        print(result)

    def delete(self, data):
        print(data)

def read():
    Clients.read()
    Samples.read()
    Batches.read()
    Samples.read()
    Worksheets.read()
    ReferenceSamples.read()
    Methods.read()

def ClientsCreate():
    dict = {
        "portal_type": "Client",
        "title": "python",
        "ClientID": "TEST-01",
        "parent_path": "/senaite/clients"
    }
    mypostdata = json.dumps(dict)
    Clients.create(mypostdata)

def SamplesCreate():
    dict = {
        "Contact": "27adda6407474fcbb2c485b80cdef076",
        "SampleType": "7276590f81ba41b0b9227be68cb8349e",
        "DateSampled": "2021-09-11",
        "Template": ""
    }
    mypostdata = json.dumps(dict)
    Samples.create('aca94a9288634ed3bc1da7be555a0039', mypostdata)

def BatchCreate():
    dict = {
        "title":"python",
        "description":"generate by python"
    }
    mypostdata = json.dumps(dict)
    Batches.create('aca94a9288634ed3bc1da7be555a0039',mypostdata)

def WorksheetCreate():
    dict = {

    }
    mypostdata = json.dumps(dict)
    Worksheets.create('a979a9e13ab3409c9c495490ea2a2e1d',mypostdata)

def ReferenceSampleCreate():
    dict = {

    }
    mypostdata = json.dumps(dict)
    ReferenceSamples.create('a979a9e13ab3409c9c495490ea2a2e1d', mypostdata)

def MethodCreate():
    dict = {

    }
    mypostdata = json.dumps(dict)
    Methods.create('a979a9e13ab3409c9c495490ea2a2e1d', mypostdata)

def ClientUpdate():
    dict = {
        "uid":"aca94a9288634ed3bc1da7be555a0039",
        "Phone":"1234"
    }
    mypostdata = json.dumps(dict)
    Clients.update(mypostdata)

def SampleUpdate():
    dict = {
        "uid": "cf613f0a0c1e4509aa9669371547ad65",
        "Priority": 0
    }
    mypostdata = json.dumps(dict)
    Samples.update(mypostdata)

def BatchUpdate():
    dict = {
        "uid": "4e31f0bde4e94b989ea6694f30e7ab3f",
        "title": "change by python"
    }
    mypostdata = json.dumps(dict)
    Batches.update(mypostdata)

def ReferencesamplesUpdate():
    dict = {
        "uid":"d40b37279b4e41b49ba629c732699bb6",
        "title":"python"
    }
    mypostdata = json.dumps(dict)
    ReferenceSamples.update(mypostdata)

def MethodUpdate():
    dict = {
        "uid":"bb3c3361e9394ad48ec3583d2c9f3cf2",
        "description":"python"
    }
    mypostdata = json.dumps(dict)
    Methods.update(mypostdata)


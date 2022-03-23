from flask_restful import Resource
from ..logics.logic_crud import Samples
import json


class SampleRead(Resource):

    def get(self):
        result = Samples().read()
        print(result)
        return result


class SampleCreate(Resource):

    def post(self, client, contact, sampletype, datesampled, clientreference, clientordernumber,clientsampleID):

        dict = {
            "Contact": contact,
            "SampleType": sampletype,
            "DateSampled": datesampled,
            "ClientReference": clientreference,
            "ClientOrderNumber": clientordernumber,
            "ClientSampleID": clientsampleID
        }
        mypostdata = json.dumps(dict)
        result = Samples().create(client, mypostdata)
        print(result)
        return result


class SamplePollingCreate(Resource):

    def post(self, client, contact, sampletype, datesampled, clientreference, clientordernumber, clientsampleID, CCContact, EnvironmentalConditions):
        CCContact = eval(CCContact)
        print(CCContact)
        print(EnvironmentalConditions)
        print(sampletype)
        dict = {
            "Contact": contact,
            "SampleType": sampletype,
            "DateSampled": datesampled,
            "ClientReference": clientreference,
            "ClientOrderNumber": clientordernumber,
            "ClientSampleID": clientsampleID,
            "CCContact": CCContact,
            "EnvironmentalConditions": EnvironmentalConditions
        }
        mypostdata = json.dumps(dict)
        result = Samples().create(client, mypostdata)
        print(result)
        return result


class SampleUpdate(Resource):

    def put(self, client_uuid, uid, batch, clientreference):
        print(clientreference)
        print(batch)
        dict = {
            "Client": client_uuid,
            "uid": uid,
            "ClientReference": clientreference,
            "batch": batch
        }
        mypostdata = json.dumps(dict)
        result = Samples().update(mypostdata)
        print(result)
        return result


class SampleContactUpdate(Resource):

    def put(self, sample_uuid, client_uuid, contact_uuid, CCContact, EnvironmentalConditions, batch, clientordernumber, PID):
        print(PID)
        CCContact = eval(CCContact)
        print(CCContact)
        print(EnvironmentalConditions)
        print(batch)
        dict = {
            "uid": sample_uuid,
            "Client": client_uuid,
            "Contact": contact_uuid,
            "CCContact": CCContact,
            "EnvironmentalConditions": EnvironmentalConditions,
            "batch": batch,
            "ClientOrderNumber": clientordernumber,
            "ClientSampleID": PID,
        }
        mypostdata = json.dumps(dict)
        result = Samples().update(mypostdata)
        print(result)
        return result

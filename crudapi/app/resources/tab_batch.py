from flask_restful import Resource
from ..logics.logic_crud import Batches
import json


class BatchRead(Resource):

    def get(self):
        result = Batches().read()
        print(result)
        return result


class BatchCreate(Resource):

    def post(self, client_uuid, batchID, title, description, batch_date, remark):
        dict = {
            "ClientBatchID": batchID,
            "title": title,
            "description": description,
            "BatchDate": batch_date,
            "Remarks": remark
        }
        mypostdata = json.dumps(dict)
        result = Batches().create(client_uuid, mypostdata)
        print(result)
        return result


class BatchUpdate(Resource):

    def put(self, batch_uuid, title, description, batch_date, remark):
        dict = {
            "uid": batch_uuid,
            "title": title,
            "description": description,
            "BatchDate": batch_date,
            "Remarks": remark
        }
        mypostdata = json.dumps(dict)
        result = Batches().update(mypostdata)
        print(result)
        return result
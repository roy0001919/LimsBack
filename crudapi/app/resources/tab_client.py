from flask_restful import Resource
from ..logics.logic_crud import Clients
import json


class ClientRead(Resource):

    def get(self):
        result = Clients().read()
        print(result)
        return result


class ClientCreate(Resource):

    def post(self, name, clientID):
        dict = {
            "portal_type": "Client",
            "title": name,
            "ClientID": clientID,
            "parent_path": "/senaite/clients",
        }
        mypostdata = json.dumps(dict)
        result = Clients().create(mypostdata)
        print(result)
        return result


class ClientUpdate(Resource):

    def put(self, uid, phone):
        dict = {
            "uid": uid,
            "Phone": phone
        }
        mypostdata = json.dumps(dict)
        result = Clients().update(mypostdata)
        print(result)
        return result
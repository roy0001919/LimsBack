from flask_restful import Resource
from ..logics.logic_crud import Contacts
import json


class ContactRead(Resource):

    def get(self):
        result = Contacts().read()
        print(result)
        return result


class ContactCreate(Resource):

    def post(self, client_uuid, name, sex, contactID, phone, email):
        dict = {
            "portal_type": "Contact",
            "Firstname": name,
            "Surname": sex,
            "Username": contactID,
            "MobilePhone": phone,
            "EmailAddress": email
        }
        mypostdata = json.dumps(dict)
        result = Contacts().create(client_uuid, mypostdata)
        print(result)
        return result


class ContactCreateReport(Resource):

    def post(self, uid, contactID, name, inspector, sex_age, birthday, company, phone, other, Middleinitial):
        info = birthday + ':' + other
        print(info)
        dict = {
            "portal_type": "Contact",
            "Salutation": contactID,
            "Firstname": name,
            "Middlename": inspector,
            "Surname": sex_age,
            "JobTitle": info,
            "Department": company,
            "Username": "護照號碼",
            "MobilePhone": phone,
            "Middleinitial": Middleinitial
        }
        mypostdata = json.dumps(dict)
        result = Contacts().createReport(uid, mypostdata)
        print(result)
        return result


class ContactUpdate(Resource):

    def put(self, uid, username):
        dict = {
            "uid": uid,
            "Username": username
        }
        mypostdata = json.dumps(dict)
        result = Contacts().update(mypostdata)
        print(result)
        return result
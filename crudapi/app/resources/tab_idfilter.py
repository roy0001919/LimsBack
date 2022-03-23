from flask_restful import Resource
from ..logics.logic_crud import IDfilter


class IDRead(Resource):

    def get(self,uid):
        result = IDfilter().read(uid)
        print(result)
        return result



from .resources import api_bp
from flask_restful import Api

api = Api(api_bp)

from .resources.tab_idfilter import IDRead
api.add_resource(IDRead, '/<string:uid>')

from .resources.tab_client import ClientRead, ClientCreate, ClientUpdate
api.add_resource(ClientCreate, '/client/<string:name>/<string:clientID>')
api.add_resource(ClientRead, '/client')
api.add_resource(ClientUpdate, '/client/<string:uid>/<string:phone>')

from .resources.tab_sample import SampleRead, SampleCreate, SampleUpdate, SamplePollingCreate, SampleContactUpdate
api.add_resource(SampleCreate, '/sample/<string:client>/<string:contact>/<string:sampletype>/<string:datesampled>/<string:clientreference>/<string:clientordernumber>/<string:clientsampleID>')
api.add_resource(SamplePollingCreate, '/sample/<string:client>/<string:contact>/<string:sampletype>/<string:datesampled>/<string:clientreference>/<string:clientordernumber>/<string:clientsampleID>/<string:CCContact>/<string:EnvironmentalConditions>')
api.add_resource(SampleRead, '/sample')
api.add_resource(SampleUpdate, '/sample/<string:client_uuid>/<string:uid>/<string:batch>/<string:clientreference>')
api.add_resource(SampleContactUpdate, '/sample/<string:sample_uuid>/<string:client_uuid>/<string:contact_uuid>/<string:CCContact>/<string:EnvironmentalConditions>/<string:batch>/<string:clientordernumber>/<string:PID>')


from .resources.tab_contact import ContactCreate, ContactRead, ContactUpdate, ContactCreateReport
api.add_resource(ContactCreate, '/contact/<string:client_uuid>/<string:name>/<string:sex>/<string:contactID>/<string:phone>/<string:email>')
api.add_resource(ContactCreateReport, '/contactReport/<string:uid>/<string:contactID>/<string:name>/<string:inspector>/<string:sex_age>/<string:birthday>/<string:company>/<string:phone>/<string:other>/<string:Middleinitial>')
api.add_resource(ContactRead, '/contact')
api.add_resource(ContactUpdate, '/contact/<string:uid>/<string:username>')


from .resources.tab_batch import BatchRead, BatchCreate, BatchUpdate
api.add_resource(BatchRead, '/batch')
api.add_resource(BatchCreate, '/batch/<string:client_uuid>/<string:batchID>/<string:title>/<string:description>/<string:batch_date>/<string:remark>')
api.add_resource(BatchUpdate, '/batch/<string:batch_uuid>/<string:title>/<string:description>/<string:batch_date>/<string:remark>')

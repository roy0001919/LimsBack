from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'back_stage'
urlpatterns = [
    path('', views.first_type_report, name='report'),
    path('login/', auth_views.LoginView.as_view(template_name='myweb/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='myweb/logout.html'), name='logout'),
    path('reserveSample/', views.reserveSample, name='reserveSample'),
    path('nonreserveSample/', views.nonreserveSample, name='nonreserveSample'),
    path('search/', views.filter, name='search'),
    path('batchGraph/', views.batchGraph, name='batchGraph'),
    path('sampleImport/', views.sampleImport, name='sampleImport'),
    path('ifCovid/', views.ifCovid, name='ifCovid'),
    path('file_upload/', views.file_upload),
    path('reverseFunc/', views.reserveFunc, name='reverseFunc'),
    path('nonreverseFunc/', views.nonreserveFunc, name='nonreverseFunc'),
    path('get_file/', views.get_file, name='get_file'),
    path('batchGraphDownload/', views.batchGraphDownload, name='batchGraphDownload'),
    path('batchGraphFunc/', views.batchGraphFunc, name='batchGraphFunc'),
    path('sampleImportFunc/', views.sampleImportFunc, name='sampleImportFunc'),
    path('singleReport/', views.single_report, name='single_report'),
    path('mutiReport/', views.muti_report, name='muti_report'),
    path('ifCovidFunc/', views.ifCovidFunc, name='ifCovidFunc'),
    path('ifCovidDownload/', views.ifCovidDownload, name='ifCovidDownload'),
    path('reportDownload/', views.reportDownload, name='reportDownload'),
    path('generateBarcode/', views.generateBarcode, name='generateBarcode'),
    path('contactPolling/', views.contactPolling, name='contactPolling'),
    path('contactPollingFunc/', views.contactPollingFunc, name='contactPollingFunc'),
    path('update_barcode_contact_info/', views.update_barcode_contact_info, name='update_barcode_contact_info'),
    path('update_barcode_contact_infoFunc/', views.update_barcode_contact_infoFunc, name='update_barcode_contact_infoFunc'),
    path('update_sample_result/', views.update_sample_result, name='update_sample_result'),
    path('update_sample_resultFunc/', views.update_sample_resultFunc, name='update_sample_resultFunc'),
    path('queryReport/', views.queryReport, name='queryReport'),
]
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'back_stage'
urlpatterns = [
    path('', views.first_type_report, name='report'),  # 報表模板匯出
    path('login/', auth_views.LoginView.as_view(template_name='myweb/login.html'), name='login'),  # 登入
    path('logout/', auth_views.LogoutView.as_view(template_name='myweb/logout.html'), name='logout'),  # 登出
    path('reserveSample/', views.reserveSample, name='reserveSample'),
    path('nonreserveSample/', views.nonreserveSample, name='nonreserveSample'),  # 單位人員已知-顧客資料匯入
    path('search/', views.filter, name='search'),  # 報表模板匯出-查詢
    path('file_upload/', views.file_upload),  # 資料上傳
    path('reverseFunc/', views.reserveFunc, name='reverseFunc'),
    path('nonreverseFunc/', views.nonreserveFunc, name='nonreverseFunc'),  # 單位人員已知-顧客資料匯入-匯入結果
    path('get_file/', views.get_file, name='get_file'),  # 資料讀取
    path('singleReport/', views.single_report, name='single_report'),  # 機台模板匯出-單連模板
    path('mutiReport/', views.muti_report, name='muti_report'),  # 機台模板匯出-多連模板
    path('reportDownload/', views.reportDownload, name='reportDownload'),  # 檔案下載
    path('generateBarcode/', views.generateBarcode, name='generateBarcode'),  # 單位人員未知-預產生條碼
    path('contactPolling/', views.contactPolling, name='contactPolling'),  # 單位人員已知-PID對應條碼
    path('contactPollingFunc/', views.contactPollingFunc, name='contactPollingFunc'),  # 單位人員已知-匯入結果
    path('update_barcode_contact_info/', views.update_barcode_contact_info, name='update_barcode_contact_info'),# 單位人員未知-回填客戶資料
    path('update_barcode_contact_infoFunc/', views.update_barcode_contact_infoFunc, name='update_barcode_contact_infoFunc'),  # 單位人員未知-匯入結果
    path('update_sample_result/', views.update_sample_result, name='update_sample_result'),  # 提取表上傳
    path('update_sample_resultFunc/', views.update_sample_resultFunc, name='update_sample_resultFunc'),  # 提取表上傳-匯入結果
    path('queryReport/', views.queryReport, name='queryReport'),  # 單/多連模板轉換功能
]
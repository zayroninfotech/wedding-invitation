from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('preview/', views.wedding_preview, name='wedding_preview'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('panel/', views.admin_panel, name='admin_panel'),
    path('qr/', views.generate_qr, name='generate_qr'),
    path('save-names/', views.save_names, name='save_names'),
    path('upload-photo/', views.upload_photo, name='upload_photo'),
    path('qr-page/', views.qr_page, name='qr_page'),
    path('invite-card/', views.invite_card, name='invite_card'),
    path('thanks/', views.thanks_page, name='thanks_page'),
    path('dashboard/<slug:slug>/', views.invite_page, name='invite_page'),
    path('sms/', views.sms_page, name='sms_page'),
    path('sms/add/', views.sms_add, name='sms_add'),
    path('sms/list/', views.sms_list, name='sms_list'),
    path('sms/delete/', views.sms_delete, name='sms_delete'),
    path('upload-card/', views.upload_card, name='upload_card'),
    path('list-cards/', views.list_cards, name='list_cards'),
    path('delete-card/', views.delete_card, name='delete_card'),
]

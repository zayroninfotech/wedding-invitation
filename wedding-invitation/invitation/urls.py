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
]

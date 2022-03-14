from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download_config/<str:config_name>/', views.download_config, name='download_config'),
    path('pki_register', views.pki_register, name='pki_register'),
    path('pki_register_conf_ok', views.pki_register_conf_ok, name='pki_register_conf_ok'),
    path('pki_register_conf_error', views.pki_register_conf_error, name='pki_register_conf_error'),
    path('download_config_error', views.download_config_error, name='download_config_error'),
]

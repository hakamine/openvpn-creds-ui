from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download_config', views.download_config, name='download_config'),
    path('pki_register', views.pki_register, name='pki_register'),
    path('pki_register_conf', views.pki_register_conf, name='pki_register_conf'),

]

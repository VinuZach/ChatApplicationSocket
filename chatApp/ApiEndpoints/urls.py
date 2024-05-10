from django.urls import path
from . import views
urlpatterns = [

    path('authenticate_user', views.authenticate_user, name="index"),
    path('register_new_user', views.register_new_user, name="index"),
    path('tes', views.tesr, name="index"),
]
from django.urls import path
from . import views
urlpatterns = [

    path('authenticate_user', views.authenticate_user, name="index"),
]
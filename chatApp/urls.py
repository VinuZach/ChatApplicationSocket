from django.urls import path
from . import views
from .ApiEndpoints import urls as APIUrlEndpoints
urlpatterns = [

    path('', views.index, name="index"),
    path('<str:room_name>/', views.room, name="rooms"),
]

urlpatterns +=APIUrlEndpoints.urlpatterns




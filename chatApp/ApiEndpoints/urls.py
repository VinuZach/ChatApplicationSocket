from django.urls import path
from . import views
urlpatterns = [

    path('authenticate_user', views.authenticate_user, name="authenticate_user"),
    path('register_new_user', views.register_new_user, name="register_user"),
    path('assign_room_to_group', views.assign_room_to_group,name="assign_room_to_group"),
    path('create_update_chat', views.create_update_chat,name="create_update_chat"),
    path("retrieve_all_users",views.retrieve_all_users,name="retrieve_all_users"),
    path('tes', views.tesr, name="index"),
]

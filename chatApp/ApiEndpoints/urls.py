from django.urls import path
from . import views
urlpatterns = [

    path('authenticate_user', views.authenticate_user, name="authenticate_user"),
    path('register_new_user', views.register_new_user, name="register_user"),
    path('assign_room_to_group', views.assign_room_to_group,name="assign_room_to_group"),
    path('create_update_chat', views.create_update_chat,name="create_update_chat"),
    path('create_update_group',views.create_update_group,name="create_update_group"),
    path("retrieve_all_users",views.retrieve_all_users,name="retrieve_all_users"),
    path("retrieve_all_chats", views.retrieve_all_chats, name="retrieve_all_chats"),
    path('tes', views.tesr, name="index"),
    path('api/upload/', views.upload_file_api, name='document_upload_api'),
]

from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ChartRoomList)
admin.site.register(PublicRoomChatMessage)
admin.site.register(GroupClusterList)
admin.site.register(FileAttachment)
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class GroupClusterList(models.Model):
    clusterName = models.TextField(unique=True,
                                   default="Cluster " + str((lambda: GroupClusterList.objects.latest('id').serial + 1)))
    clusterChatCount = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)


class ChartRoomList(models.Model):
    roomName = models.CharField(max_length=255, unique=False, blank=False)
    userList = models.ManyToManyField(User, help_text="authorised users")
    clusterGroupId = models.ForeignKey(GroupClusterList, on_delete=models.SET_NULL, null=True, default=None,blank=True)

    def __str__(self):
        return str(self.id)


class PublicRoomChatMessageManager(models.Manager):
    def by_room(self, room):
        print(PublicRoomChatMessage.objects.filter(room=room).order_by("-id"))
        qs = PublicRoomChatMessage.objects.filter(room=room).order_by("-id")

        return qs



class ChatAttachment:
    def __init__(self, attachment_type, attachment):
        self.attachment_type = attachment_type
        self.attachment = attachment

    def to_dict(self):
        return {'attachment_type': self.attachment_type, 'attachment': self.attachment}

    @classmethod
    def from_dict(cls, data):
        return cls(data['attachment_type'], data['attachment'])

class ChatAttachmentData(models.JSONField):  # Or JSONField, CharField, etc., depending on how you store it
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        # Convert the stored database value (e.g., JSON string) back to your custom object
        data = json.loads(value)
        return ChatAttachmentData.from_dict(data)

    def get_prep_value(self, value):
        if value is None:
            return None
        # Convert your custom object to a database-compatible format (e.g., JSON string)
        return json.dumps(value.to_dict())

    # Optional: Implement value_to_string for serialization (e.g., for Django REST Framework)
    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)



class PublicRoomChatMessage(models.Model):
    """
    Chat message created by a user inside a PublicChatRoom
    """
    id = models.AutoField(auto_created=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChartRoomList, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(unique=False, blank=False, )
    blocked_users =models.TextField(unique=False,blank=False,default='[]')
    chatAttachment=models.JSONField(null=True, blank=True)
    objects = PublicRoomChatMessageManager()

    def __str__(self):
        return self.content


class FileAttachment(models.Model):
    fileName=models.TextField(max_length=40,null=False)
    uploadedFile = models.FileField(upload_to='documents/',null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=100, blank=True)



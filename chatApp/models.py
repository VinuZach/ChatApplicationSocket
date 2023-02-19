from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class ChartRoomList(models.Model):
    roomName = models.CharField(max_length=255, unique=False, blank=False)
    userList = models.ManyToManyField(User, help_text="authorised users")

    def __str__(self):
        return str(self.id)


class PublicRoomChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = PublicRoomChatMessage.objects.filter(room=room).order_by("-id")

        return qs


class PublicRoomChatMessage(models.Model):
    """
    Chat message created by a user inside a PublicChatRoom
    """
    id = models.AutoField(auto_created=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChartRoomList, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(unique=False, blank=False, )

    objects = PublicRoomChatMessageManager()

    def __str__(self):
        return self.content

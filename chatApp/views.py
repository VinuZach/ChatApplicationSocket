from django.shortcuts import render
from django.shortcuts import render
from .models import *


# Create your views here.
def index(request):
    print(request.user)
    chatRoomListOfUsers = {}
    if request.user.is_authenticated:
        chatRoomListOfUsers = ChartRoomList.objects.filter(userList=request.user)
    chatRoomWithTotalMessage = list(map(getMessageCountByRoomId, chatRoomListOfUsers))

    return render(request, 'index.html',
                  {"chatRoomWithTotalMessage": chatRoomWithTotalMessage})


def getMessageCountByRoomId(roomid):
    chatRoom = ChartRoomList.objects.all().filter(roomName=roomid)[0]
    return {"room": roomid, "totalMessages": PublicRoomChatMessage.objects.by_room(chatRoom).count()}


def room(request, room_name):
    return render(request, 'ChatRoom.html', {'room_name': room_name})

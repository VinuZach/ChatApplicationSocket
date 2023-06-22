import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.paginator import Paginator
from django.core.serializers.python import Serializer
from django.db.models import QuerySet

from .models import *

ALL_CHAT_ROOMS = "all_chat_master"


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        print("inside chatmessage")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        command = text_data_json['command']
        user = text_data_json['user']
        pageNumber = text_data_json['pageNumber']
        print(command)
        # Send message to room group
        print("create_room_chat_message  111")
        create_room_chat_message(self.room_name, user, message)
        if command != "join":
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'prevMessages': '',
                    'user': user,
                    "new_page_number": pageNumber
                }
            )
        else:
            prev_messages, new_page_number = get_room_chat_messages(self.room_name, pageNumber)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': "",
                    "prevMessages": prev_messages,
                    'user': "",
                    "new_page_number": new_page_number
                }
            )
        async_to_sync(self.channel_layer.group_send)(
            ALL_CHAT_ROOMS,
            {
                'type': 'refresh_chat_List'
            }
        )

    # Receive message from room group
    def chat_message(self, event):

        message = event['message']
        user = event['user']
        prevMessages = event['prevMessages']
        new_page_number = event['new_page_number']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'prevMessages': prevMessages,
            'user': user,
            "new_page_number": new_page_number
        }))


def create_room_chat_message(room, user, message):
    print("create_room_chat_message")
    print(str(room))
    chatRoom = ChartRoomList.objects.all().filter(id=room)[0]
    if ALL_CHAT_ROOMS != room:
        if len(message) != 0:
            PublicRoomChatMessage.objects.create(user=User.objects.get(email=user), room=chatRoom,
                                                 content=message)


def get_room_chat_messages(room, page_number):
    new_page_number = int(page_number)
    try:
        print("get_room_chat_messages")
        print(str(room))
        chatRoom = ChartRoomList.objects.all().filter(id=room)[0]
        qs = PublicRoomChatMessage.objects.by_room(chatRoom)
        p = Paginator(qs, 13)
        if new_page_number <= p.num_pages:
            new_page_number = new_page_number + 1
            s = LazyRoomChatMessageEncoder()
            payload = s.serialize(p.page(new_page_number))
        else:
            payload = {}
        return payload, new_page_number
    except Exception as e:
        print("EXCEPTION: " + str(e))
        return {}, new_page_number


class LazyRoomChatMessageEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'primaryId': int(obj.id)})
        dump_object.update({'message': str(obj.content)})
        dump_object.update({'timestamp': str(obj.timestamp)})
        dump_object.update({'user': str(obj.user)})
        return dump_object


''''
            ------------------------    Chat room List----------------------------------
'''


class RoomListConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = ALL_CHAT_ROOMS
        self.room_group_name = ALL_CHAT_ROOMS
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def chat_List(self, event):
        print("chat chat_List ")
        print(event['clusterId'])

        user = self.scope["user"]
        try:
            clusterId = event['clusterId']
        except:
            clusterId = -1
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'chatRoomWithTotalMessage': retrieveChatList(user, clusterId),
            'clusterRoomGroups': retrieveGroupList(user),
            "Chat_Type": "updated_chatlist",

        }))

    def refresh_chat_List(self, event):
        self.send(text_data=json.dumps({
            'Chat_Type': "refresh",
        }))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        user = text_data_json['user']
        clusterId = text_data_json['clusterId']
        print("inside chatroom ")
        print(clusterId)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_List',
                'user': user,
                'clusterId': str(clusterId),
            }
        )


def retrieveGroupList(user):
    chatRoomListOfUsers = ChartRoomList.objects.filter(userList=User.objects.get(email=user),
                                                       clusterGroupId__isnull=False).order_by('-clusterGroupId__clusterChatCount')

    chatRoomWithTotalMessage = list(map(getMessageCountForGroup, chatRoomListOfUsers))
    return chatRoomWithTotalMessage


def retrieveChatList(user, clusterId):
    print("retrieveChatList")
    print(clusterId)
    if clusterId != "-1":
        print("asdsadsad")
        chatRoomListOfUsers = ChartRoomList.objects.filter(userList=User.objects.get(email=user),
                                                           clusterGroupId=GroupClusterList.objects.get(id=clusterId),
                                                           clusterGroupId__isnull=False)
    else:
        chatRoomListOfUsers = ChartRoomList.objects.filter(userList=User.objects.get(email=user),
                                                           clusterGroupId__isnull=True)
    chatRoomWithTotalMessage = list(map(getMessageCountByRoomId, chatRoomListOfUsers))
    return sorted(chatRoomWithTotalMessage, key=lambda d: d["totalMessages"], reverse=True)


def getMessageCountForGroup(roomid):
    chatRoom = ChartRoomList.objects.all().filter(id=roomid.id)[0]
    chatWithCount = ChatListWithMessageCount()
    chatWithCount.roomName = str(GroupClusterList.objects.get(id=str(roomid.clusterGroupId)).clusterName)
    chatWithCount.totalMessage = PublicRoomChatMessage.objects.by_room(chatRoom).count()
    chatWithCount.roomId = roomid.id
    chatWithCount.clusterGroupId = str(roomid.clusterGroupId)
    return chatWithCount.__str__()


def getMessageCountByRoomId(roomid):
    chatRoom = ChartRoomList.objects.all().filter(id=roomid.id)[0]
    chatWithCount = ChatListWithMessageCount()
    chatWithCount.roomName = roomid.roomName
    chatWithCount.totalMessage = PublicRoomChatMessage.objects.by_room(chatRoom).count()
    chatWithCount.roomId = roomid.id
    chatWithCount.clusterGroupId = str(roomid.clusterGroupId)
    return chatWithCount.__str__()


class ChatListWithMessageCount:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, )

    def __int__(self, roomId, roomName, totalMessage, clusterGroupId):
        self.roomId = roomId
        self.roomName = roomName
        self.totalMessage = totalMessage
        self.clusterGroupId = clusterGroupId

    def __str__(self):
        return {"roomID": self.roomId,
                "roomName": self.roomName,
                "clusterGroupId": self.clusterGroupId,
                "totalMessages": self.totalMessage}

    def getMessageCount(self):
        return self.totalMessage

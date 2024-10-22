import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.paginator import Paginator
from django.core.serializers.python import Serializer
from django.db.models import QuerySet

from .models import *
import ast

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
        try:
            print(text_data)
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            blocked_user = None
            if 'blocked_user' in text_data_json.keys():
                blocked_user = text_data_json['blocked_user']
            command = text_data_json['command']
            user = text_data_json['user']
            pageNumber = text_data_json['pageNumber']
            # Send message to room group
            _, _, chat_room_user_list = get_room_chat_messages(self.room_name, pageNumber)
            create_room_chat_message(self.room_name, user, message, blocked_user)
            if command != "join":
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'prevMessages': None,
                        'user': user,
                        "new_page_number": pageNumber,
                        "blocked_user": blocked_user,
                        "chat_room_user_list": chat_room_user_list
                    }
                )
            else:
                prev_messages, new_page_number, chat_room_user_list = get_room_chat_messages(self.room_name, pageNumber)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': "",
                        "prevMessages": prev_messages,
                        'user': "",
                        "new_page_number": new_page_number,
                        "chat_room_user_list": chat_room_user_list

                    }
                )
            async_to_sync(self.channel_layer.group_send)(
                ALL_CHAT_ROOMS,
                {
                    'type': 'refresh_chat_List'
                }
            )
        except Exception as e:
            print(e)

    # Receive message from room group
    def chat_message(self, event):

        message = event['message']
        user = event['user']
        prevMessages = event['prevMessages']
        new_page_number = event['new_page_number']
        blocked_user = None
        chat_room_user_list = None
        if 'blocked_user' in event.keys():
            blocked_user = event['blocked_user']
        if 'chat_room_user_list' in event.keys():
            chat_room_user_list = event['chat_room_user_list']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'prevMessages': prevMessages,
            'user': user,
            "new_page_number": new_page_number,
            "blocked_user": blocked_user,
            "chat_room_user_list": chat_room_user_list
        }))


def create_room_chat_message(room, user, message, blocked_user):
    blocked_user_data = []
    if blocked_user:
        blocked_user_data.extend(blocked_user)

    chatRoom = ChartRoomList.objects.all().filter(id=room)[0]
    if ALL_CHAT_ROOMS != room:
        if len(message) != 0:
            PublicRoomChatMessage.objects.create(user=User.objects.get(email=user), room=chatRoom,
                                                 content=message, blocked_users=blocked_user_data)


def get_room_chat_messages(room, page_number):
    new_page_number = int(page_number)
    chat_room_user_list = []
    try:
        chatRoom = ChartRoomList.objects.all().filter(id=room)[0]
        chat_room_user_list_data = list(chatRoom.userList.all())
        for user in chat_room_user_list_data:
            chat_room_user_list.append(user.email)

        qs = PublicRoomChatMessage.objects.by_room(chatRoom)
        p = Paginator(qs, 13)
        if new_page_number <= p.num_pages:
            new_page_number = new_page_number + 1
            s = LazyRoomChatMessageEncoder()
            payload = s.serialize(p.page(new_page_number))
            print(payload)
        else:
            payload = {}
        return payload, new_page_number, chat_room_user_list
    except Exception as e:
        print("EXCEPTION: " + str(e))
        return {}, new_page_number, chat_room_user_list


class LazyRoomChatMessageEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'primaryId': int(obj.id)})
        dump_object.update({'message': str(obj.content)})
        dump_object.update({'timestamp': str(obj.timestamp)})
        dump_object.update({'user': str(obj.user)})
        if obj.blocked_users:
            print(obj.blocked_users)
            print(ast.literal_eval(obj.blocked_users))
            dump_object.update({'blocked_user': ast.literal_eval(obj.blocked_users)})
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
        user = event['user']
        try:
            clusterId = event['clusterId']
        except:
            clusterId = -1
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'chatRoomWithTotalMessage': retrieveChatList(user, clusterId),
            'clusterRoomGroups': retrieveGroupList(user),
            "Chat_Type": "updated_chatlist",
            "requested_user": user
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
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_List',
                'user': user,
                'clusterId': str(clusterId),
            }
        )


def retrieveGroupList(user):
    userDetails = User.objects.get(email=user)
    chatRoomListOfUsers = ChartRoomList.objects.filter(userList=userDetails,
                                                       clusterGroupId__isnull=False).order_by(
        '-clusterGroupId__clusterChatCount')

    # chatRoomWithTotalMessage = list(map(getMessageCountForGroup, chatRoomListOfUsers))
    return getGroupDetailsWithMessageCount(chatRoomListOfUsers, userDetails)


def getGroupDetailsWithMessageCount(chatRoomList, userDetails):
    groupDetailsDict = {}
    for chatRoom in chatRoomList:
        group_details = GroupClusterList.objects.get(id=str(chatRoom.clusterGroupId))
        chatRoomCount = ChartRoomList.objects.filter(userList=userDetails,
                                                     clusterGroupId=chatRoom.clusterGroupId).count()
        print(chatRoomCount)
        groupItem = groupDetailsDict.get(group_details.clusterName)
        if groupItem is None:
            chatWithCount = ChatListWithMessageCount()
            chatWithCount.roomName = group_details.clusterName
            chatWithCount.roomCountUnderGroup = chatRoomCount
            chatWithCount.totalMessage = PublicRoomChatMessage.objects.by_room(chatRoom).count()
            chatWithCount.clusterGroupId = str(group_details.id)
            chatWithCount.roomId = None
            groupDetailsDict[group_details.clusterName] = chatWithCount

        else:

            groupItem.totalMessage += PublicRoomChatMessage.objects.by_room(chatRoom).count()
    groupDetailsList = []
    for x in groupDetailsDict.values():
        groupDetailsList.append(x.__str__())
    return groupDetailsList


def retrieveChatList(user, clusterId):
    if clusterId != "-1":

        chatRoomListOfUsers = ChartRoomList.objects.filter(userList=User.objects.get(email=user),
                                                           clusterGroupId=GroupClusterList.objects.get(id=clusterId),
                                                           clusterGroupId__isnull=False)
    else:
        chatRoomListOfUsers = ChartRoomList.objects.filter(userList=User.objects.get(email=user))
    chatRoomWithTotalMessage = list(map(getMessageCountByRoomId, chatRoomListOfUsers))
    return sorted(chatRoomWithTotalMessage, key=lambda d: d["totalMessages"], reverse=True)


def getMessageCountByRoomId(roomid):
    chatRoom = ChartRoomList.objects.all().filter(id=roomid.id)[0]
    chatWithCount = ChatListWithMessageCount()
    chatWithCount.roomName = roomid.roomName
    chatWithCount.totalMessage = PublicRoomChatMessage.objects.by_room(chatRoom).count()
    chatWithCount.roomId = roomid.id
    chatWithCount.roomCountUnderGroup = 0
    chatWithCount.clusterGroupId = str(roomid.clusterGroupId)
    return chatWithCount.__str__()


class ChatListWithMessageCount:

    def __int__(self, roomId, roomName, totalMessage, clusterGroupId, roomsCount):
        self.roomId = roomId
        self.roomName = roomName
        self.roomCountUnderGroup = roomsCount
        self.totalMessage = totalMessage
        self.clusterGroupId = clusterGroupId

    def __str__(self):
        return {
            "roomID": self.roomId,
            "roomName": self.roomName,
            "clusterGroupId": self.clusterGroupId,
            "roomCountUnderGroup": self.roomCountUnderGroup,
            "totalMessages": self.totalMessage}

    def getMessageCount(self):
        return self.totalMessage

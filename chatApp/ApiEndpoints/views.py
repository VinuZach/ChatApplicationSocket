from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .serializer import *
from ..models import *


def api_exception_handler(exc, context):
    def handleApiException(response_data, message, status_code):
        response_data.data = {
            "message": message,
            "statusCode": status_code,
            "success": False
        }
        return response_data

    print(f"inside exception {exc}")
    response = exception_handler(exc, context)

    if response is not None:
        occurred_exception = exc.__class__.__name__
        print(occurred_exception)
        api_response = None
        match occurred_exception:
            case "MethodNotAllowed":
                api_response = handleApiException(response, "Invalid api", "400")  # handleInvalidMethod(response)
            case "AuthenticationFailed":
                api_response = handleApiException(response, "Invalid user", "200")  # handleAuthException(response)
            case "NotAuthenticated":
                api_response = handleApiException(response, "user not authenticated", "200")
        return api_response
    else:
        return Response({"success": False})


@authentication_classes([BasicAuthentication])
@api_view(['POST'])
def authenticate_user(request):
    user = User.objects.get(username="" + request.user.username)
    if user:
        token = Token.objects.get_or_create(user=user)
        print(token[0])
        return Response({"token": str(token[0]), "success": True})
    print(request.user.username)
    return Response({"message": "Invalid User", "success": False})


@api_view(["POST"])
def create_update_group(request):
    new_group_name = request.data["group_name"]
    assigned_rooms = request.data["roomIds"]
    print(request.data["group_name"])
    print(request.data["roomIds"])
    if GroupClusterList.objects.filter(clusterName=new_group_name).first():
        return Response({"message": "Group name already exists", "success": False})
    else:
        created_group = GroupClusterList(clusterName=new_group_name, clusterChatCount=len(assigned_rooms))
        created_group.save()
        ChartRoomList.objects.filter(id__in=assigned_rooms).update(clusterGroupId=created_group.id)
        return Response({"message": "Group created succesfully ", "success": True})


@api_view(["POST"])
def assign_room_to_group(request):
    print(request.data["roomId"])
    print(request.data["userOverride"])
    print(request.data["groupId"])
    chatroomList = ChartRoomList.objects.all().filter(id=request.data["roomId"])
    groupList = GroupClusterList.objects.all().filter(id=request.data["groupId"])
    if groupList.count() == 0:
        return Response({"message": "group does not exist", "success": False})
    groupItem = groupList.first()
    if chatroomList.count() > 0:
        chatRoom = chatroomList.first()
        if chatRoom.clusterGroupId:
            if not request.data["userOverride"]:
                return Response({"message": "Room already assigned group", "success": False})

        print(groupItem)
        chatRoom.clusterGroupId = groupItem
        chatRoom.save()

    else:
        print("no such room")
    return Response({"message": "Success", "success": True})


@api_view(["POST"])
def register_new_user(request):
    serializers = UserSerializer(data=request.data)
    if serializers.is_valid():
        serializers.save()
        user = User.objects.get(username=request.data["username"])
        user.set_password(request.data["password"])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "success": True})
    else:
        default_errors = serializers.errors
        print(default_errors)
        field_names = None
        for field_name, field_errors in default_errors.items():
            field_names = field_name + " "
        return Response({"message": f"invalid data in {field_names}", "success": False},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def retrieve_all_users(request):
    print(request.data["userName"])
    all_users_lists = User.objects.values_list('username', flat=True).exclude(username=request.data["userName"])
    # all_users_lists = User.objects.all().values()
    return JsonResponse(list(all_users_lists), safe=False)


@api_view(["POST"])
def retrieve_all_chats(request):
    block_assigned_chats = request.data["block_assigned_chats"]
    current_user = request.data["currentUserName"]
    all_chat_list = ChartRoomList.objects.all().filter(userList__username=current_user)
    if block_assigned_chats:
        all_chat_list = all_chat_list.filter(clusterGroupId=None)
    all_chat_list = all_chat_list.values()
    response = Response({"success":True,"chatListData": list(all_chat_list)})
    return response


@api_view(["POST"])
def create_update_chat(request):
    existing_chat_room = None
    chat_room_name = request.data["room_name"]
    chat_user_list = request.data["chat_user_list"]
    user_list = ()
    if len(chat_user_list) > 0:
        user_list = User.objects.all().filter(username__in=chat_user_list)
        print(chat_user_list)
        print(User.objects.all().filter(username__in=chat_user_list))
    if request.data["room_id"]:
        existing_chat_room = ChartRoomList.objects.filter(id=request.data["room_id"]).first()
        print(existing_chat_room.roomName)
        if len(chat_user_list) > 0:
            existing_chat_room.userList.add(user_list)

        else:
            user_list = existing_chat_room.userList
        existing_chat_room.roomName = chat_room_name
        existing_chat_room.userList.add(*user_list)
        existing_chat_room.save()
        if existing_chat_room is None:
            return Response({"message": "NO such room"})
    else:
        new_chat_room = ChartRoomList(roomName=chat_room_name, clusterGroupId=None)
        new_chat_room.save()
        new_chat_room.userList.add(*user_list)
    return Response({"message": "Success ", "success": True})


from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from chatApp.serializer import FileUploadSerializer

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file_api(request):
    serializer = FileUploadSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tesr(request):
    return Response("asdsad")

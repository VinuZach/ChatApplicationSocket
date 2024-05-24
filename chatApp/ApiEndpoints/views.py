from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework import status
from .serializer import *
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


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
def register_new_user(request):
    serializers = UserSerializer(data=request.data)
    if serializers.is_valid():
        serializers.save()
        user = User.objects.get(username=request.data["username"])
        user.set_password(request.data["password"])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"tokem": token.key, "user": serializers.data})
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tesr(request):
    return Response("asdsad")

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework import status
from .serializer import *
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    print("inside exception ")
    if response is not None:
        occurredException = exc.__class__.__name__
        print(occurredException)
        apiResponse=None
        match occurredException:
            case "MethodNotAllowed":
                apiResponse = handleInvalidMethod(response)
            case "AuthenticationFailed":
                apiResponse=handleAuthException(response)
        return apiResponse
    else:
        return Response({ "success": True})

def handleAuthException(response):
    response.data = {
        "message": "user unauthorised",
        "statusCode": "200",
        "success": False
    }
    return response


def handleInvalidMethod(response):
    response.data = {
        "message": "Invalid api",
        "statusCode": "405",
        "success": False
    }
    return response


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
        return Response({"token": token.key, "user": serializers.data})
    else:
        default_errors = serializers.errors
        field_names = None
        for field_name, field_errors in default_errors.items():
            field_names=field_name+" "
        return Response({"message": f"invalid data in {field_names}", "success": False},status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tesr(request):
    return Response("asdsad")

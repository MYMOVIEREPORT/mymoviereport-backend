from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_jwt.settings import api_settings

from .serializers import UserSerializer

from passlib.hash import django_pbkdf2_sha256

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny, ])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        password = serializer.validated_data.get('password')
        hashed_password = django_pbkdf2_sha256.hash(password)
        user = serializer.save(password=hashed_password)

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return JsonResponse({'token': token})
    return HttpResponse(status=400)

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

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
        serializer.save(password=hashed_password)
        return JsonResponse({
            'username': serializer.validated_data.get('username'),
            'password': serializer.validated_data.get('password')
            })
    return HttpResponse(status=400)  # 잘못된 입력에 따른 에러

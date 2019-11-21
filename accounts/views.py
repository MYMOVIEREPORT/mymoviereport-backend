from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .serializers import UserSerializer

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny, ])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)  # 잘못된 입력에 따른 에러

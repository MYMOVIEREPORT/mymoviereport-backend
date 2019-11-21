from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view

from .serializers import UserSerializer

# Create your views here.


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(request.POST)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return HttpResponse(status=400)  # 잘못된 입력에 따른 에러
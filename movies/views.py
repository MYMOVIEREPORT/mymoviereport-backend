from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import (UserSerializer, GenreSerializer, DirectorSerializer,
                        ActorSerializer, MovieSerializer, PostSerializer)
from .models import Genre, Director, Actor, Movie, Hashtag, Post

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def user(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    if request.user == user:
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)
    return HttpResponse('허가되지않은 접근입니다.', status=403)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def genres(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def directors(request):
    directors = Director.objects.all()
    serializer = DirectorSerializer(directors, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def actors(request):
    actors = Actor.objects.all()
    serializer = ActorSerializer(actors, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movies(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def posts(request):
    posts = Post.objects.filter(published=True)
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)
    
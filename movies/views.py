from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import (UserSerializer, GenreSerializer, DirectorSerializer,
                          ActorSerializer, MovieSerializer, PostSerializer)
from .models import Genre, Director, Actor, Movie, Hashtag, Post

from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
from decouple import config

import requests

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def user_detail(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    if request.user == user:
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)
    return HttpResponse('허가되지않은 접근입니다.', status=403)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def all_genres(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def all_directors(request):
    directors = Director.objects.all()
    serializer = DirectorSerializer(directors, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def all_actors(request):
    actors = Actor.objects.all()
    serializer = ActorSerializer(actors, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def all_movies(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def all_posts(request):
    posts = Post.objects.filter(published=True)
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def user_posts(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    posts = user.posts.all()
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def some_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    serializer = PostSerializer(post)
    return JsonResponse(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def update_db(request):
    loop = 100

    movie_key = config('MOVIE_KEY')
    movie_url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={movie_key}&curPage=1&itemPerPage={loop}'

    movie_res = requests.get(movie_url).json()
    for i in range(loop):
        title = movie_res.get('movieListResult').get(
            'movieList')[i].get('movieNmEn')
        title_ko = movie_res.get('movieListResult').get(
            'movieList')[i].get('movieNm')

        genre = movie_res.get('movieListResult').get(
            'movieList')[i].get('repGenreNm')
        genre = Genre.objects.get_or_create(name=genre)[0]

        naver_id = config('NAVER_ID')
        naver_secret = config('NAVER_SECRET')

        naver_url = 'https://openapi.naver.com/v1/search/movie.json'
        headers = {
            'X-Naver-Client-Id': naver_id,
            'X-Naver-Client-Secret': naver_secret
        }

        combined_naver_url = f'{naver_url}?query={title}'
        naver_res = requests.get(combined_naver_url, headers=headers).json()

        if naver_res.get('items'):
            score = naver_res.get('items')[0].get('userRating')

            directors = naver_res.get('items')[0].get(
                'director').split('|')[:-1]
            for director in directors:
                director = Director.objects.get_or_create(name=director)[0]

            actors = naver_res.get('items')[0].get('actor').split('|')[:-1]
            for actor in actors:
                actor = Actor.objects.get_or_create(name=actor)[0]

            result_link = naver_res.get('items')[0].get('link').split('=')[-1]
            poster_link = f'https://movie.naver.com/movie/bi/mi/photoViewPopup.nhn?movieCode={result_link}'
            poster = requests.get(poster_link).text
            soup = BeautifulSoup(poster, 'html.parser')
            img = soup.find('img')
            if img:
                poster_url = img.get('src')
        else:
            score = 0
            directors = ''
            actors = ''
            poster_url = ''

        youtube_key = config('YOUTUBE_KEY')
        youtube_url = 'https://www.googleapis.com/youtube/v3/search'

        combined_youtube_url = f'{youtube_url}?part=snippet&q={title}&type=video&key={youtube_key}'
        youtube_res = requests.get(combined_youtube_url).json()

        youtube_id_res = youtube_res.get('items')
        if youtube_id_res:
            videoId = youtube_id_res[0].get('id').get('videoId')
            video_url = f'https://www.youtube.com/embed/{videoId}'
        else:
            video_url = ''

        movie, created = Movie.objects.get_or_create(
            title=title, title_ko=title_ko, score=score, poster_url=poster_url, video_url=video_url, genre=genre)
        if created:
            for director in directors:
                director = get_object_or_404(Director, name=director)
                movie.directors.add(director)
            for actor in actors:
                actor = get_object_or_404(Actor, name=actor)
                movie.actors.add(actor)

    return JsonResponse({'message': 'done!'})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import (UserSerializer, GenreSerializer,
                          MovieSerializer, PostSerializer, PostCreateSerializer)
from .models import Genre, Director, Actor, Movie, Hashtag, Post

from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from decouple import config
import requests

# Create your views here.


def hashtag_create(post, content):
    for word in content:
        if word.startswith('#'):
            hashtag = Hashtag.objects.get_or_create(tag=word)[0]
            post.hashtags.add(hashtag)


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
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def user_posts(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    posts = user.posts.all()
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def genres_entire(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movies_entire(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movies_new(request):
    movies = Movie.objects.order_by('-created_at', '-id')[:10]
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    serializer = MovieSerializer(movie)
    return JsonResponse(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movie_posts(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    posts = movie.posts.all()
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def posts_entire(request):
    posts = Post.objects.filter(published=True)
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def post_create(request):
    movie = get_object_or_404(Movie, id=request.data.get('movie_id'))
    post = PostCreateSerializer(data=request.data)
    if post.is_valid(raise_exception=True):
        post = post.save(movie_id=movie.id, user=request.user)

        content = request.data.get('content').split(' ')
        hashtag_create(post, content)

        serializer = PostSerializer(instance=post)
        return JsonResponse(serializer.data)
    return HttpResponse(status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny, ])
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return JsonResponse(serializer.data)
    else:
        if request.user == post.user:
            if request.method == 'PUT':
                serializer = PostCreateSerializer(
                    instance=post,
                    data=request.data)
                if serializer.is_valid(raise_exception=True):
                    post = serializer.save(
                        movie_id=request.data.get('movie_id'),
                        user=request.user)

                    for hashtag in post.hashtags.all():
                        post.hashtags.remove(hashtag)

                    content = request.data.get('content').split(' ')
                    hashtag_create(post, content)

                    serializer = PostSerializer(post)
                    return JsonResponse(serializer.data)
            else:
                post.delete()
                return JsonResponse({'message': '삭제가 완료되었습니다.'})
    return HttpResponse('잘못된 요청입니다.', status=403)


@api_view(['PUT'])
@permission_classes([IsAdminUser, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def update_db(request):
    today = date.strftime(date.today(), '%Y%m%d')

    movie_key = config('MOVIE_KEY')
    naver_id = config('NAVER_ID')
    naver_secret = config('NAVER_SECRET')
    youtube_key = config('YOUTUBE_KEY')

    for d in range(2):  # 최초 DB 생성을 위해서는 50으로 바꿔야합니다.(기본값은 이번주와 저번주를 확인하기 위해서 2로 고정)
        movie_url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json?key={movie_key}&targetDt={today}&weekGb=0'
        movie_res = requests.get(movie_url).json().get(
            'boxOfficeResult').get(
            'weeklyBoxOfficeList')
        if movie_res:
            for i in range(10):
                movie_cd = movie_res[i].get('movieCd')

                movie_detail_url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?key={movie_key}&movieCd={movie_cd}'
                movie_detail_res = requests.get(movie_detail_url).json().get(
                    'movieInfoResult').get(
                    'movieInfo')

                title_ko = movie_detail_res.get('movieNm')
                title_en = movie_detail_res.get('movieNmEn')

                genre = movie_detail_res.get('genres')[0].get('genreNm')
                genre = Genre.objects.get_or_create(name=genre)[0]

                release_date = movie_detail_res.get('openDt')
                release_date = f'{release_date[:4]}-{release_date[4:6]}-{release_date[6:]}'

                watch_grade = movie_detail_res.get(
                    'audits')[0].get(
                    'watchGradeNm')
                if not watch_grade:
                    watch_grade = ''

                naver_url = 'https://openapi.naver.com/v1/search/movie.json'
                headers = {
                    'X-Naver-Client-Id': naver_id,
                    'X-Naver-Client-Secret': naver_secret
                }

                combined_naver_url = f'{naver_url}?query={title_ko}'
                naver_res = requests.get(
                    combined_naver_url,
                    headers=headers).json().get('items')
                if naver_res:
                    score = naver_res[0].get('userRating')

                    directors = naver_res[0].get('director').split('|')[:-1]
                    for director in directors:
                        director = Director.objects.get_or_create(
                            name=director)[0]

                    actors = naver_res[0].get('actor').split('|')[:-1]
                    for actor in actors:
                        actor = Actor.objects.get_or_create(name=actor)[0]

                    naver_poster_number = naver_res[0].get(
                        'link').split(
                        '=')[-1]
                    naver_poster = f'https://movie.naver.com/movie/bi/mi/photoViewPopup.nhn?movieCode={naver_poster_number}'
                    poster = requests.get(naver_poster).text
                    soup = BeautifulSoup(poster, 'html.parser')
                    img = soup.find('img')
                    if img:
                        poster_url = img.get('src')
                else:
                    score = 0
                    directors = ''
                    actors = ''
                    poster_url = ''

                youtube_url = 'https://www.googleapis.com/youtube/v3/search'

                combined_youtube_url = f'{youtube_url}?part=snippet&q={title_ko}+예고편&type=video&key={youtube_key}'
                youtube_res = requests.get(combined_youtube_url).json()

                youtube_id_res = youtube_res.get('items')
                if youtube_id_res:
                    videoId = youtube_id_res[0].get('id').get('videoId')
                    video_url = f'https://www.youtube.com/embed/{videoId}'
                else:
                    video_url = ''

                movie, created = Movie.objects.get_or_create(
                    title_ko=title_ko, title_en=title_en,
                    score=score, poster_url=poster_url, video_url=video_url,
                    genre=genre, release_date=release_date, watch_grade=watch_grade)
                if created:
                    for director in directors:
                        director = get_object_or_404(Director, name=director)
                        movie.directors.add(director)
                    for actor in actors:
                        actor = get_object_or_404(Actor, name=actor)
                        movie.actors.add(actor)

        str_time = f'{today}'
        conv_time = datetime.strptime(
            str_time, '%Y%m%d').date() - timedelta(weeks=1)
        today = conv_time.strftime('%Y%m%d')

    return JsonResponse({'message': 'DB가 갱신되었습니다!'})

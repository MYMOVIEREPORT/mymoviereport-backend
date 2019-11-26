from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from accounts.serializers import UserSerializer, UserSimpleSerializer
from .serializers import (GenreSerializer, MovieSerializer, MovieSimpleSerializer,
                          PostSerializer, PostSimpleSerializer, PostCreateSerializer)
from .models import Genre, Director, Actor, Movie, Hashtag, Post

from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from decouple import config

import requests


def hashtag_create(post, content):
    for word in content:
        if word.startswith('#'):
            if len(word) > 1 and '#' not in word[1:]:
                hashtag = Hashtag.objects.get_or_create(hashtag=word)[0]
                post.hashtags.add(hashtag)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def search(request):
    keywords = request.GET.get('keywords')
    keywords = keywords.split(' ')

    result = {'movies': []}
    for keyword in keywords:
        movies = Movie.objects.filter(
            Q(title_ko__contains=keyword) |
            Q(title_en__contains=keyword)
        )
        for movie in movies:
            result['movies'].append({
                'id': movie.id,
                'title_ko': movie.title_ko,
                'score': movie.score,
                'poster_url': movie.poster_url,
            })

    return JsonResponse(result)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def user_ranks(request):
    users = get_user_model().objects.annotate(
        user_posts=Count('posts')
    ).order_by(
        '-user_posts', 'username'
    )[:10]
    serializer = UserSimpleSerializer(users, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def user_detail(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    serializer = UserSerializer(user)
    return JsonResponse(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def user_posts(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    posts = user.posts.all()
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def user_recos(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    posts = user.posts.all()
    if posts:
        reco_dict = {}
        for post in posts:
            user_genre = post.movie.genre
            if user_genre in reco_dict:
                reco_dict[user_genre] += 1
            else:
                reco_dict[user_genre] = 1

        reco_genre, user_val = None, 0
        for key, val in reco_dict.items():
            if user_val < val:
                user_val = val
                reco_genre = key

        reco_movies = Movie.objects.filter(
            ~Q(watched_user__in=[user.id]) &
            Q(genre=reco_genre)
        ).order_by(
            '-score'
        )[:12]

        serializer = MovieSerializer(reco_movies, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'message': '아직 추천에 필요한 포스트 정보가 존재하지 않습니다.'})


@api_view(['GET'])
@permission_classes([AllowAny, ])
def genres_entire(request):
    target = request.GET.get('target')
    if target:
        genre = get_object_or_404(Genre, id=target)
        serializer = GenreSerializer(genre)
    else:
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movies_entire(request):
    page = request.GET.get('page')
    items = request.GET.get('items')

    movies = Movie.objects.all()
    if page and items:
        start = int(items) * (int(page) - 1)
        movies = movies[start:start + int(items)]
    else:
        if page:
            start = 24 * (int(page) - 1)
            movies = movies[start:start + 24]
        elif items:
            movies = movies[:int(items)]
        else:
            movies = movies[0:24]
    serializer = MovieSimpleSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movies_new(request):
    movies = Movie.objects.order_by('-release_date', '-id')[:12]
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movies_hot(request):
    today = timezone.now()
    lastweek = today - timedelta(weeks=1)

    posts = Post.objects.filter(
        Q(created_at__gte=lastweek) &
        Q(created_at__lte=today))

    movies = {}
    for post in posts:
        movie_id = post.movie.id
        if movie_id in movies:
            movies[movie_id] += 1
        else:
            movies[movie_id] = 1

    movies = sorted(list(
        movies.items()),
        key=lambda x: x[1],
        reverse=True
    )[:12]

    hot_movies = [get_object_or_404(Movie, id=movie[0]) for movie in movies]
    serializer = MovieSerializer(hot_movies, many=True)
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
    page = request.GET.get('page')
    items = request.GET.get('items')

    posts = Post.objects.filter(published=True)
    if page and items:
        start = int(items) * (int(page) - 1)
        posts = posts[start:start + int(items)]
    else:
        if page:
            start = 24 * (int(page) - 1)
            posts = posts[start:start + 24]
        elif items:
            posts = posts[:int(items)]
        else:
            posts = posts[0:24]

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
        movie.watched_user.add(request.user)

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
                    data=request.data
                )

                if serializer.is_valid(raise_exception=True):
                    post = serializer.save()

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

    for d in range(100):
        movie_url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json?key={movie_key}&targetDt={today}&weekGb=0'
        movie_res = requests.get(movie_url).json(
        ).get('boxOfficeResult').get('weeklyBoxOfficeList')

        if movie_res != []:
            for i in range(10):
                movie_nm = movie_res[i].get('movieNm')

                try:
                    movie_instance = Movie.objects.get(title_ko=movie_nm)
                except ObjectDoesNotExist:
                    movie_cd = movie_res[i].get('movieCd')

                    movie_detail_url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?key={movie_key}&movieCd={movie_cd}'
                    movie_detail_res = requests.get(movie_detail_url).json(
                    ).get('movieInfoResult')

                    if movie_detail_res:
                        movie_detail_res = movie_detail_res.get('movieInfo')

                        title_ko = movie_detail_res.get('movieNm')
                        title_en = movie_detail_res.get('movieNmEn')

                        genre = movie_detail_res.get(
                            'genres'
                        )[0].get('genreNm')
                        genre = Genre.objects.get_or_create(name=genre)[0]

                        open_dt = movie_detail_res.get('openDt')
                        if open_dt:
                            release_date = f'{open_dt[:4]}-{open_dt[4:6]}-{open_dt[6:]}'
                        else:
                            release_date = '9999-12-31'

                        audits = movie_detail_res.get('audits')
                        if audits:
                            watch_grade = audits[0].get('watchGradeNm')
                        else:
                            watch_grade = ''

                        naver_url = 'https://openapi.naver.com/v1/search/movie.json'
                        headers = {
                            'X-Naver-Client-Id': naver_id,
                            'X-Naver-Client-Secret': naver_secret
                        }

                        combined_naver_url = f'{naver_url}?query={title_ko}'
                        naver_res = requests.get(
                            combined_naver_url,
                            headers=headers
                        ).json().get('items')

                        if naver_res:
                            score = naver_res[0].get('userRating')

                            directors = naver_res[0].get(
                                'director'
                            ).split('|')[:-1]
                            for director in directors:
                                director = Director.objects.get_or_create(
                                    name=director)[0]

                            actors = naver_res[0].get('actor').split('|')[:-1]
                            for actor in actors:
                                actor = Actor.objects.get_or_create(
                                    name=actor
                                )[0]

                            link = naver_res[0].get('link')
                            html = requests.get(link).text
                            soup = BeautifulSoup(html, 'html.parser')
                            head = soup.find('h5', {'class': 'h_tx_story'})
                            body = soup.find('p', {'class': 'con_tx'})
                            if head or body:
                                head = '' if not head else head.text
                                body = '' if not body else body.text

                                description = head + '\n' + body.replace(
                                    '\r', '\n'
                                ).replace('\xa0', '')

                            naver_poster_number = naver_res[0].get(
                                'link'
                            ).split('=')[-1]
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
                            description = ''

                        youtube_url = 'https://www.googleapis.com/youtube/v3/search'

                        combined_youtube_url = f'{youtube_url}?part=snippet&q={title_ko}+예고편&type=video&key={youtube_key}'
                        youtube_res = requests.get(combined_youtube_url).json()

                        youtube_id_res = youtube_res.get('items')
                        if youtube_id_res:
                            videoId = youtube_id_res[0].get(
                                'id'
                            ).get('videoId')
                            video_url = f'https://www.youtube.com/embed/{videoId}'
                        else:
                            video_url = ''

                        movie = Movie.objects.create(
                            title_ko=title_ko, title_en=title_en, description=description,
                            score=score, poster_url=poster_url, video_url=video_url,
                            genre=genre, release_date=release_date, watch_grade=watch_grade
                        )

                        for director in directors:
                            director = get_object_or_404(
                                Director,
                                name=director
                            )
                            movie.directors.add(director)
                        for actor in actors:
                            actor = get_object_or_404(Actor, name=actor)
                            movie.actors.add(actor)

        str_time = f'{today}'
        conv_time = datetime.strptime(
            str_time,
            '%Y%m%d'
        ).date() - timedelta(weeks=1)
        today = conv_time.strftime('%Y%m%d')

    return JsonResponse({'message': 'DB가 갱신되었습니다!'})

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from movies.models import Genre, Director, Actor, Movie

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from decouple import config

import requests


def get_movie_info(MOVIE, code):
    url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?key={MOVIE}&movieCd={code}'
    res = requests.get(url).json().get('movieInfoResult')

    title_ko, title_en, genre, release_date, watch_grade, step = '', '', '', '9999-12-31', '', False
    if res:
        step = True
        res = res.get('movieInfo')

        title_ko = res.get('movieNm')
        title_en = res.get('movieNmEn')

        genreNm = res.get('genres')
        if genreNm:
            genreNm = genreNm[0].get('genreNm')
            genre = Genre.objects.get_or_create(name=genreNm)[0]

        openDt = res.get('openDt')
        if openDt:
            release_date = f'{openDt[:4]}-{openDt[4:6]}-{openDt[6:]}'

        audits = res.get('audits')
        if audits:
            watch_grade = audits[0].get('watchGradeNm')

    return title_ko, title_en, genre, release_date, watch_grade, step


def get_naver_info(title_ko, NAVER_ID, NAVER_SECRET):
    url = f'https://openapi.naver.com/v1/search/movie.json?query={title_ko}'
    headers = {
        'X-Naver-Client-Id': NAVER_ID,
        'X-Naver-Client-Secret': NAVER_SECRET
    }

    res = requests.get(url, headers=headers).json().get('items')

    score, directors, actors, mini_poster_url, link = 0, '', '', '', ''
    if res:
        res = res[0]

        link = res.get('link')
        score = res.get('userRating')
        mini_poster_url = res.get('image')

        directors = res.get('director').split('|')[:-1]
        for director in directors:
            Director.objects.get_or_create(name=director)

        actors = res.get('actor').split('|')[:-1]
        for actor in actors:
            Actor.objects.get_or_create(name=actor)

    return score, mini_poster_url, directors, actors, link


def get_naver_craw(link):
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'html.parser')

    head = soup.find('h5', {'class': 'h_tx_story'})
    body = soup.find('p', {'class': 'con_tx'})

    description = ''
    if head or body:
        head = head.text if head else ''
        body = body.text if body else ''

        description += head + '\n'
        description += body.replace('\r', '\n').replace('\xa0', '')

    code = link.split('=')[-1]
    poster = f'https://movie.naver.com/movie/bi/mi/photoViewPopup.nhn?movieCode={code}'
    res = requests.get(poster).text

    soup = BeautifulSoup(res, 'html.parser')
    img = soup.find('img')

    poster_url = img.get('src') if img else ''

    return description, poster_url


def get_youtube_info(title_ko, YOUTUBE):
    youtube_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={title_ko}+예고편&type=video&key={YOUTUBE}'
    youtube_res = requests.get(youtube_url).json().get('items')

    video_url = ''
    if youtube_res:
        videoId = youtube_res[0].get('id').get('videoId')
        video_url = f'https://www.youtube.com/embed/{videoId}'

    return video_url


@api_view(['PUT'])
@permission_classes([IsAdminUser, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def update_db(request):
    start = day = date.strftime(date.today(), '%Y%m%d')

    MOVIE = config('MOVIE_KEY')
    NAVER_ID = config('NAVER_ID')
    NAVER_SECRET = config('NAVER_SECRET')
    YOUTUBE = config('YOUTUBE_KEY')

    for d in range(50):
        movie_url = f'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json?key={MOVIE}&targetDt={day}&weekGb=0'
        movie_res = requests.get(movie_url).json().get(
            'boxOfficeResult'
        ).get(
            'weeklyBoxOfficeList'
        )

        if movie_res:
            for i in range(10):
                try:
                    title_ko = movie_res[i].get('movieNm')

                    movie = Movie.objects.get(title_ko=title_ko)
                    updated_at = date.strftime(movie.updated_at, '%Y%m%d')
                    if updated_at < start:
                        movie.score = get_naver_info(
                            title_ko, NAVER_ID, NAVER_SECRET
                        )[0]

                    video_url = movie.video_url
                    if not video_url:
                        movie.video_url = get_youtube_info(title_ko, YOUTUBE)

                    movie.save()

                except ObjectDoesNotExist:
                    code = movie_res[i].get('movieCd')
                    title_ko, title_en, genre, release_date, watch_grade, step = \
                        get_movie_info(MOVIE, code)

                    if step:
                        score, mini_poster_url, directors, actors, link = \
                            get_naver_info(title_ko, NAVER_ID, NAVER_SECRET)

                        if link:
                            description, poster_url = get_naver_craw(link)

                        video_url = get_youtube_info(title_ko, YOUTUBE)

                        movie = Movie.objects.create(
                            title_ko=title_ko, title_en=title_en, description=description,
                            score=score, poster_url=poster_url, mini_poster_url=mini_poster_url, video_url=video_url,
                            genre=genre, release_date=release_date, watch_grade=watch_grade
                        )

                        for director in directors:
                            director = Director.objects.get(name=director)
                            movie.directors.add(director)

                        for actor in actors:
                            actor = Actor.objects.get(name=actor)
                            movie.actors.add(actor)

        ctime = datetime.strptime(f'{day}', '%Y%m%d') - timedelta(weeks=1)
        day = ctime.strftime('%Y%m%d')

    return HttpResponse(status=200)


@api_view(['DELETE'])
@permission_classes([IsAdminUser, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def delete_db(request):
    # 서버를 돌리는 해 기준, 10년 전 영화 제거
    movies = Movie.objects.all()

    day = date.strftime(date.today(), '%Y%m%d')
    past = datetime.strptime(f'{day}', '%Y%m%d') - timedelta(days=3650)
    day = past.strftime('%Y-%m-%d')

    movies = Movie.objects.filter(release_date__lte=day)
    for movie in movies:
        Movie.objects.get(id=movie.id).delete()

    # 제목이 중복인 영화 제거
    movies = Movie.objects.all()

    titles = set()
    for movie in movies:
        titles.add(movie.title_ko)

    dups = []
    for title in titles:
        movies = sorted(
            Movie.objects.filter(title_ko=title),
            key=lambda x: x.release_date,
            reverse=True
        )
        if len(movies) > 1:
            for movie in movies[1:]:
                dups += [movie.id]

    for dup in dups:
        Movie.objects.get(id=dup).delete()

    # 포스터가 없는 영화 제거
    movies = Movie.objects.all()

    for movie in movies:
        if not movie.poster_url:
            Movie.objects.get(id=movie.id).delete()

    # 포스터가 중복인 영화 제거
    movies = Movie.objects.all()

    posters = set()
    for movie in movies:
        posters.add(movie.poster_url)

    dups = []
    for poster in posters:
        movies = sorted(
            Movie.objects.filter(poster_url=poster),
            key=lambda x: x.release_date,
            reverse=True
        )
        if len(movies) > 1:
            for movie in movies[1:]:
                dups += [movie.id]

    for dup in dups:
        Movie.objects.get(id=dup).delete()

    # 영화가 하나도 없는 배우 혹은 감독 제거
    actors = Actor.objects.all()
    for actor in actors:
        if not actor.movies.all():
            Actor.objects.get(id=actor.id).delete()

    directors = Director.objects.all()
    for director in directors:
        if not director.movies.all():
            Director.objects.get(id=director.id).delete()

    # 이름이 중복되는 배우 혹은 감독 제거
    actors = Actor.objects.all()

    names = set()
    for actor in actors:
        names.add(actor.name)

    for name in names:
        actors = sorted(Actor.objects.filter(name=name))
        if len(actors) > 1:
            for actor in actors[1:]:
                Actor.objects.get(id=actor.id).delete()

    directors = Director.objects.all()

    names = set()
    for director in directors:
        names.add(director.name)

    for name in names:
        directors = sorted(Director.objects.filter(name=name))
        if len(directors) > 1:
            for director in directors[1:]:
                Director.objects.get(id=director.id).delete()

    return HttpResponse(status=200)

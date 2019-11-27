from django.http import JsonResponse
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

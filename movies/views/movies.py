from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q

from movies.serializers import MovieSerializer, PostSerializer
from movies.models import Genre, Movie, Post

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from datetime import timedelta


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movies_entire(request):
    page = int(request.GET.get('page'))
    target = int(request.GET.get('target', 0))
    maxS = int(request.GET.get('maxScore', 10))
    minS = int(request.GET.get('minScore', 0))

    if target != 0:
        genre = Genre.objects.get(id=target)
        movies = genre.movies.filter(
            score__gte=minS,
            score__lte=maxS
        )
    else:
        movies = Movie.objects.filter(
            score__gte=minS,
            score__lte=maxS
        )

    movies = movies[12 * (page - 1):12 * page]
    serializer = MovieSerializer(movies, many=True)
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
        Q(updated_at__gte=lastweek) &
        Q(updated_at__lte=today))

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

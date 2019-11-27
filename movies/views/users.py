from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.http import JsonResponse

from accounts.serializers import UserSerializer
from movies.serializers import MovieSerializer, PostSerializer
from movies.models import Movie

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


@api_view(['GET'])
@permission_classes([AllowAny, ])
def user_ranks(request):
    users = get_user_model().objects.annotate(
        user_posts=Count('posts')
    ).order_by(
        '-user_posts', 'username'
    )[:10]
    serializer = UserSerializer(users, many=True)
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

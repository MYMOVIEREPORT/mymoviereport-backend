from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse

from accounts.serializers import UserSerializer, UserChangeSerializer
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


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([JSONWebTokenAuthentication, ])
def user_detail(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)
    else:
        if request.user == user:
            if request.method == 'PUT':
                serializer = UserChangeSerializer(user, request.data)
                if serializer.is_valid():
                    serializer.save()
                    serializer = UserSerializer(user)
                    return JsonResponse(serializer.data)
            else:
                username = user.username
                user.delete()
                return JsonResponse({'message': f'그동안 감사했습니다. {username}님. 다시 만나기를 기대하겠습니다.'})
    return HttpResponse('잘못된 접근입니다.', status=403)


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
            user_score = post.score
            if user_genre in reco_dict:
                reco_dict[user_genre] += user_score
            else:
                reco_dict[user_genre] = user_score

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

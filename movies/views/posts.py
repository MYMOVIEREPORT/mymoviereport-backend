from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from movies.models import Movie, Post, Hashtag
from movies.serializers import PostSerializer, PostCreateSerializer


def hashtag_create(post, content):
    for word in content:
        if word.startswith('#'):
            if len(word) > 1 and '#' not in word[1:]:
                hashtag = Hashtag.objects.get_or_create(hashtag=word)[0]
                post.hashtags.add(hashtag)


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

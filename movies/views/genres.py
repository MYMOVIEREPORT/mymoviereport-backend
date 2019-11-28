from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from movies.serializers import MovieSerializer
from movies.models import Genre


@api_view(['GET'])
@permission_classes([AllowAny, ])
def genres_entire(request):
    page = int(request.GET.get('page'))
    target = request.GET.get('target')
    if target:
        genre = get_object_or_404(Genre, id=target)
        movies = genre.movies.all()[24 * (page - 1): 24 * page]
        serializer = MovieSerializer(movies, many=True)
    else:
        genres = Genre.objects.all()
        movies = genre.movies.all()[24 * (page - 1): 24 * page]
        serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)

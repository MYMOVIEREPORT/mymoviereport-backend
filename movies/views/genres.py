from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from movies.serializers import GenreSerializer
from movies.models import Genre


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

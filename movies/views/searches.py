
from django.http import JsonResponse
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from movies.models import Movie


@api_view(['GET'])
@permission_classes([AllowAny, ])
def search(request):
    keywords = request.GET.get('keywords')
    keywords = keywords.split(' ')

    page = request.GET.get('page')
    items = request.GET.get('items')

    results = []
    for keyword in keywords:
        movies = Movie.objects.filter(
            Q(title_ko__contains=keyword) |
            Q(title_en__contains=keyword)
        )
        for movie in movies:
            results.append({
                'id': movie.id,
                'title_ko': movie.title_ko,
                'score': movie.score,
                'poster_url': movie.poster_url,
            })

    if page and items:
        start = int(items) * (int(page) - 1)
        end = start + int(items)
    else:
        if page:
            start = 12 * (int(page) - 1)
            end = start + 12
        elif items:
            start, end = 0, int(items)
        else:
            start, end = 0, 12

    serializer = {'movies': []}
    for result in results[start:end]:
        serializer['movies'].append(result)

    return JsonResponse(serializer)

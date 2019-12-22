from django.urls import path
from .views import searches, users, genres, movies, posts, db


urlpatterns = [
    path('search/', searches.search),

    path('user/ranks/', users.user_ranks),
    path('user/<int:user_id>/', users.user_detail),
    path('user/<int:user_id>/posts/', users.user_posts),
    path('user/<int:user_id>/recos/', users.user_recos),

    path('genres/', genres.genres_entire),

    path('movies/', movies.movies_entire),
    path('movies/new/', movies.movies_new),
    path('movies/hot/', movies.movies_hot),
    path('movie/<int:movie_id>/', movies.movie_detail),
    path('movie/<int:movie_id>/posts/', movies.movie_posts),

    path('posts/', posts.posts_entire),
    path('post/create/', posts.post_create),
    path('post/<int:post_id>/', posts.post_detail),

    path('update/db/', db.update_db),
    path('delete/db/', db.delete_db),
]

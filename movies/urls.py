from django.urls import path
from . import views

urlpatterns = [
    path('user/<int:user_id>/', views.user_detail),
    path('user/<int:user_id>/posts/', views.user_posts),

    path('genres/', views.genres_entire),

    path('movies/', views.movies_entire),
    path('movie/<int:movie_id>/', views.movie_detail),
    path('movie/<int:movie_id>/posts/', views.movie_posts),

    path('posts/', views.posts_entire),
    path('post/create/', views.post_create),
    path('post/<int:post_id>/', views.post_detail),

    path('update/db/', views.update_db),
]

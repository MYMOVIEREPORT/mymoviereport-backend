from django.urls import path
from . import views

urlpatterns = [
    path('user/<int:user_id>/', views.user_detail),
    path('user/<int:user_id>/posts/', views.user_posts),

    path('genres/', views.genres_entire),

    path('movies/', views.movies_entire),
    path('movie/<int:movie_id>/', views.movie_detail),

    path('posts/', views.posts_entire),
    path('<int:movie_id>/post/create/', views.post_create),
    path('<int:movie_id>/post/<int:post_id>/', views.post_detail),

    path('update/db/', views.update_db),
]

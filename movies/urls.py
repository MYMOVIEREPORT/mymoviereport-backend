from django.urls import path
from . import views

urlpatterns = [
    path('user/<int:user_id>/', views.user_detail),
    path('user/<int:user_id>/posts/', views.user_posts),

    path('genres/', views.all_genres),
    path('directors/', views.all_directors),
    path('actors/', views.all_actors),

    path('movies/', views.all_movies),
    path('movie/<int:movie_id>/', views.some_movie),

    path('posts/', views.all_posts),
    path('post/<int:post_id>/', views.some_post),
    path('<int:movie_id>/post/create/', views.post_create),

    path('update/db/', views.update_db),
]

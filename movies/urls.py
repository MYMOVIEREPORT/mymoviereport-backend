from django.urls import path
from . import views

urlpatterns = [
    path('user/<int:user_id>/', views.user),
    path('user/<int:user_id>/posts/', views.user_posts),

    path('genres/', views.genres),
    path('directors/', views.directors),
    path('actors/', views.actors),
    path('movies/', views.movies),
    path('posts/', views.posts),

    path('post/<int:post_id>/', views.post),

    path('update/db/', views.update_db),
]

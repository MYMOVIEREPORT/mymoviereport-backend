from django.urls import path
from . import views

urlpatterns = [
    path('user/<int:user_id>/', views.user),
    path('genres/', views.genres),
    path('directors/', views.directors),
    path('actors/', views.actors),
]

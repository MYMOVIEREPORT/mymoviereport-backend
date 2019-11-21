from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.users),
    path('genres/', views.genres),
    path('directors/', views.directors),
]

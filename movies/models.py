from django.db import models
from django.contrib.auth import settings

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=100)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_genres')


class Director(models.Model):
    name = models.CharField(max_length=100)


class Actor(models.Model):
    name = models.CharField(max_length=100)


class Movie(models.Model):
    title = models.CharField(max_length=200)
    title_ko = models.CharField(max_length=200)
    score = models.FloatField()
    poster_url = models.CharField(max_length=500)
    video_url = models.CharField(max_length=500, null=True)
    descriptrion = models.TextField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    directors = models.ManyToManyField(Director, related_name='movies')
    actors = models.ManyToManyField(Actor, related_name='movies')


class Hashtag(models.Model):
    tag = models.CharField(max_length=100)


class Post(models.Model):
    content = models.TextField()
    score = models.FloatField()
    published = models.BooleanField()
    image = models.CharField(max_length=200)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    hashtags = models.ManyToManyField(Hashtag, related_name='posts')
    
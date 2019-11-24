from django.db import models
from django.contrib.auth import settings

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title_ko = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    score = models.FloatField()
    poster_url = models.CharField(max_length=500)
    video_url = models.CharField(max_length=500, null=True)
    description = models.TextField()
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='movies')
    directors = models.ManyToManyField(Director, related_name='movies')
    actors = models.ManyToManyField(Actor, related_name='movies')

    def __str__(self):
        return self.title_ko


class Hashtag(models.Model):
    hashtag = models.CharField(max_length=100)

    def __str__(self):
        return self.hashtag


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    score = models.FloatField()
    published = models.BooleanField()
    image = models.CharField(max_length=200)
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='posts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='posts')
    hashtags = models.ManyToManyField(Hashtag, related_name='posts')

    def __str__(self):
        return self.title

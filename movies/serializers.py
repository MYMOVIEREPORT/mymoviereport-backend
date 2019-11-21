from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Genre, Director, Actor, Movie, Hashtag, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', ]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = '__all__'
        

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
                    'id', 'title', 'title_ko', 'score',
                    'poster_url', 'video_url', 'description',
                    'genres', 'directors', 'actors'
        ]
        

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
                    'id', 'title', 'title_ko', 'score',
                    'poster_url', 'video_url', 'description',
                    'genres', 'directors', 'actors'
        ]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
                    'id', 'title', 'title_ko', 'score',
                    'poster_url', 'video_url', 'description',
                    'genres', 'directors', 'actors'
        ]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
                    'id', 'title', 'title_ko', 'score',
                    'poster_url', 'video_url', 'description',
                    'genres', 'directors', 'actors'
        ]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
                    'id', 'title', 'title_ko', 'score',
                    'poster_url', 'video_url', 'description',
                    'genres', 'directors', 'actors'
        ]

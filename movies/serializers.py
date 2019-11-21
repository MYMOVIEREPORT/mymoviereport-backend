from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Genre, Director, Actor, Movie, Hashtag, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    like_users = serializers.SlugRelatedField(many=True, read_only=True, slug_field='username')
    class Meta:
        model = Genre
        fields = ('like_users',)


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


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
                    'id', 'title', 'title_ko', 'score',
                    'poster_url', 'video_url', 'description',
                    'genres', 'directors', 'actors'
        ]

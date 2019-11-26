from django.contrib.auth import get_user_model
from accounts.serializers import UserSimpleSerializer
from .models import Genre, Director, Actor, Movie, Post, Hashtag

from rest_framework import serializers


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = '__all__'


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()
    actors = ActorSerializer(many=True)
    directors = DirectorSerializer(many=True)
    watched_user = UserSimpleSerializer(many=True)

    class Meta:
        model = Movie
        fields = '__all__'


class MovieSimpleSerializer(serializers.ModelSerializer):
    watched_user = UserSimpleSerializer(many=True)

    class Meta:
        model = Movie
        fields = ['id', 'title_ko', 'title_en', 'poster_url', 'watched_user']


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    movie = MovieSimpleSerializer()
    hashtags = HashtagSerializer(many=True)

    class Meta:
        model = Post
        fields = '__all__'


class PostSimpleSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer()
    hashtags = HashtagSerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content',
                  'score', 'image', 'hashtags']


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'score', 'published', 'image', ]

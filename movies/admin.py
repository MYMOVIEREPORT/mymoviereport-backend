from django.contrib import admin
from .models import Genre, Director, Actor, Movie, Hashtag, Post

# Register your models here.

admin.site.register(Genre)
admin.site.register(Director)
admin.site.register(Actor)
admin.site.register(Movie)
admin.site.register(Hashtag)
admin.site.register(Post)

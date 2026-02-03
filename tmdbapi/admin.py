from django.contrib import admin
from .models import MlGenre, MlMovie

@admin.register(MlGenre)
class MlGenreAdmin(admin.ModelAdmin):
    list_display = (
        'genre_guid',
        'name',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
    )
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('genre_guid', 'created_at', 'updated_at')

@admin.register(MlMovie)
class MlMovieAdmin(admin.ModelAdmin):
    list_display = (
        'movie_guid',
        'title',
        'original_title',
        'genre',
        'release_date',
        'popularity',
        'vote_average',
        'vote_count',
        'created_at',
    )
    search_fields = (
        'title',
        'original_title',
    )
    list_filter = (
        'genre',
        'adult',
        'original_language',
        'release_date',
    )
    ordering = ('-popularity', '-vote_average')
    readonly_fields = ('movie_guid', 'created_at', 'updated_at')

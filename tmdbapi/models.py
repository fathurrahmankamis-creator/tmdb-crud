import uuid
from django.db import models

# Test Git cli


class MlGenre(models.Model):
    
    class Meta:
        db_table = "ml_genre"
    
    genre_guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class MlMovie(models.Model):
    
    class Meta:
        db_table = 'ml_movie'
    
    movie_guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255)
    overview = models.TextField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    backdrop_path = models.CharField(max_length=255, null=True, blank=True)
    media_type = models.CharField(max_length=50, null=True, blank=True)
    adult = models.BooleanField(null=True, blank=True)
    original_language = models.CharField(max_length=50, null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    video = models.BooleanField(null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    genre = models.ForeignKey(
        MlGenre,
        on_delete=models.CASCADE,
        to_field='genre_guid',
        related_name='movies'
    )

    def __str__(self):
        return self.title

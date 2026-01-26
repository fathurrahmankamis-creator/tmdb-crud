from django.db import transaction
from rest_framework import serializers
from .models import MlGenre, MlMovie

class MlMovieSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(write_only=True, required=False)
    genre_detail = serializers.SerializerMethodField(read_only=True)
    genre = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MlMovie
        fields = [
            'movie_guid','title','original_title','overview','poster_path','backdrop_path',
            'media_type','adult','original_language','popularity','release_date','video',
            'vote_average','vote_count','created_at','created_by','updated_at','updated_by',
            'genre','genre_detail','genre_name'
        ]
        read_only_fields = ['movie_guid','created_at','updated_at','genre_detail']

    def get_genre_detail(self, obj):
        if obj.genre:
            return {
                "genre_guid": obj.genre.genre_guid,
                "name": obj.genre.name,
                "created_at": obj.genre.created_at,
                "created_by": obj.genre.created_by,
                "updated_at": obj.genre.updated_at,
                "updated_by": obj.genre.updated_by
            }
        return None

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()

    def validate(self, attrs):
        title = attrs.get("title")
        genre = attrs.get("genre")
        genre_name = attrs.get("genre_name")

        if not title or not title.strip():
            raise serializers.ValidationError({"title": "Title cannot be empty."})

        if not genre and not self.instance:
            if not genre_name or not genre_name.strip():
                raise serializers.ValidationError({"genre_name": "Genre name cannot be empty."})
            try:
                genre = MlGenre.objects.get(name__iexact=genre_name.strip())
            except MlGenre.DoesNotExist:
                raise serializers.ValidationError({"genre_name": f"Genre '{genre_name}' does not exist."})
            attrs["genre"] = genre

        if self.instance and not genre:
            attrs["genre"] = self.instance.genre

        qs = MlMovie.objects.filter(title__iexact=title.strip(), genre=attrs["genre"])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({"title": "A movie with this title already exists in this genre."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("genre_name", None)
        return MlMovie.objects.create(**validated_data)

class NestedMlMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = MlMovie
        fields = [
            'title','original_title','overview','poster_path','backdrop_path',
            'media_type','adult','original_language','popularity','release_date','video',
            'vote_average','vote_count','created_by'
        ]

class MlGenreSerializer(serializers.ModelSerializer):
    movie_list = NestedMlMovieSerializer(many=True, required=False, source="movies")

    class Meta:
        model = MlGenre
        fields = ["genre_guid","name","created_at","created_by","updated_at","updated_by","movie_list"]
        read_only_fields = ["genre_guid","created_at","updated_at"]

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Genre name cannot be empty.")
        qs = MlGenre.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Genre with this name already exists.")
        return value.strip()

    def create(self, validated_data):
        movies_data = validated_data.pop("movies", [])
        with transaction.atomic():
            genre = MlGenre.objects.create(**validated_data)
            for movie_data in movies_data:
                MlMovie.objects.create(genre=genre, **movie_data)
        return genre

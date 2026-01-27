from django.db import transaction
from rest_framework import serializers
from django.db import transaction
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
        from_parent = bool(self.context.get("from_genre", False))
        genre_name = attrs.pop("genre_name", None)

        if self.instance:
            genre = self.instance.genre
        else:
            genre = attrs.get("genre", None)

        if not genre and not from_parent:
            if not genre_name or not genre_name.strip():
                raise serializers.ValidationError({"genre_name": "Genre name cannot be empty."})
            try:
                genre = MlGenre.objects.get(name__iexact=genre_name.strip())
            except MlGenre.DoesNotExist:
                raise serializers.ValidationError({"genre_name": f"Genre '{genre_name}' does not exist."})
            attrs["genre"] = genre

        title = attrs.get("title") or (self.instance.title if self.instance else None)
        if title and genre:
            qs = MlMovie.objects.filter(title__iexact=title.strip(), genre=genre)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"title": "A movie with this title already exists in this genre."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("genre_name", None)
        return MlMovie.objects.create(**validated_data)

    def update(self, instance, validated_data):
        genre_name = validated_data.pop("genre_name", None)

        if genre_name and genre_name.strip():
            try:
                genre = MlGenre.objects.get(name__iexact=genre_name.strip())
            except MlGenre.DoesNotExist:
                raise serializers.ValidationError({"genre_name": f"Genre '{genre_name}' does not exist."})
            instance.genre = genre
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if instance.title and instance.genre:
            qs = MlMovie.objects.filter(title__iexact=instance.title.strip(), genre=instance.genre)
            qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"title": "A movie with this title already exists in this genre."})

        instance.save()
        return instance

class NestedMlMovieSerializer(serializers.ModelSerializer):
    """
    Nested serializer for creating movies under genre.
    """
    class Meta:
        model = MlMovie
        fields = [
            'title', 'original_title', 'overview', 'poster_path', 'backdrop_path',
            'media_type', 'adult', 'original_language', 'popularity', 'release_date', 'video',
            'vote_average', 'vote_count', 'created_by'
        ]


class MlGenreSerializer(serializers.ModelSerializer):
    movie_list = NestedMlMovieSerializer(many=True, required=False, source="movies")

class NestedMlMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = MlMovie
        fields = [
            'genre_guid', 'name', 'created_at', 'created_by', 'updated_at', 'updated_by', 'movie_list'
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
        seen_titles = set()

        with transaction.atomic():
            genre = MlGenre.objects.create(**validated_data)

            for movie_data in movies_data:
                title = movie_data.get("title", "")
                if not title or not title.strip():
                    raise serializers.ValidationError({"movie_list": "Movie title cannot be empty."})

                key = title.strip().lower()
                if key in seen_titles:
                    raise serializers.ValidationError({"movie_list": f"Duplicate movie title in payload: {title}"})
                seen_titles.add(key)

                serializer = MlMovieSerializer(
                    data=movie_data,
                    context={"from_genre": True}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(genre=genre)

        return genre

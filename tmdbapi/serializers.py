from rest_framework import serializers
from .models import MlGenre, MlMovie

class MlMovieSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(write_only=True)
    genre_detail = serializers.SerializerMethodField(read_only=True)
    genre = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MlMovie
        fields = [
            'movie_guid',
            'title',
            'original_title',
            'overview',
            'poster_path',
            'backdrop_path',
            'media_type',
            'adult',
            'original_language',
            'popularity',
            'release_date',
            'video',
            'vote_average',
            'vote_count',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'genre',       
            'genre_detail',
            'genre_name'
        ]
        read_only_fields = ['movie_guid', 'created_at', 'updated_at', 'genre_detail']

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
        genre_name = attrs.pop("genre_name", None)
        
        if not genre_name or not genre_name.strip():
            raise serializers.ValidationError({"genre_name": "Genre name cannot be empty."})
        
        try:
            genre = MlGenre.objects.get(name__iexact=genre_name.strip())
        except MlGenre.DoesNotExist:
            raise serializers.ValidationError({"genre_name": f"Genre '{genre_name}' does not exist."})
        
        attrs['genre'] = genre
                    
        if title and genre:
            qs = MlMovie.objects.filter(title__iexact=title, genre=genre)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"title": "A movie with this title already exists in this genre."})
        return attrs

class MlGenreSerializer(serializers.ModelSerializer):
    movies = MlMovieSerializer(many=True, required=False)

    class Meta:
        model = MlGenre
        fields = [
            'genre_guid',
            'name',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'movies'
        ]
        read_only_fields = ['genre_guid', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Genre name cannot be empty.")
        
        qs = MlGenre.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Genre with this name already exist.")
        return value.strip()

    def create(self, validated_data):
        movies_data = validated_data.pop('movies', [])
        
        seen_titles = set()
        for movie in movies_data:
            title = movie.get("title", "")
            if not title or not title.strip():
                raise serializers.ValidationError({"movies": "Movie title cannot be empty."})
            key = title.strip().lower()
            if key in seen_titles:
                raise serializers.ValidationError({"movies": f"Duplicate movie title in payload: {title}"})
            seen_titles.add(key)
            
        genre = MlGenre.objects.create(**validated_data)

        for movie_data in movies_data:
            title = movie_data.get("title").strip()
            if MlMovie.objects.filter(title__iexact=title, genre=genre).exists():
                raise serializers.ValidationError({"movies": f"Movie '{title}' already exists in this genre."})
            
            MlMovie.objects.create(
                genre=genre,
                **movie_data
            )

        return genre

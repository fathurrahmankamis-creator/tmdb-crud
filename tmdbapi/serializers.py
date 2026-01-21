from rest_framework import serializers
from .models import MlGenre, MlMovie

class MlMovieSerializer(serializers.ModelSerializer):
    genre = serializers.PrimaryKeyRelatedField(
        queryset=MlGenre.objects.all(),
        write_only=True
    )
    genre_detail = serializers.SerializerMethodField(read_only=True)

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
            'genre_detail'  
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

    def create(self, validated_data):
        movies_data = validated_data.pop('movies', [])
        genre = MlGenre.objects.create(**validated_data)

        for movie_data in movies_data:
            MlMovie.objects.create(
                genre=genre,
                **movie_data
            )

        return genre

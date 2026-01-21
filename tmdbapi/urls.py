from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MlGenreViewSet, MlMovieViewSet

router = DefaultRouter()
router.register('ml_genre', MlGenreViewSet, basename='ml_genre')
router.register('ml_movie', MlMovieViewSet, basename='ml_movie')

urlpatterns = [
    path('', include(router.urls)),
]

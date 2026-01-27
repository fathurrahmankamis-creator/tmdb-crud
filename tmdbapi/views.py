from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from .models import MlGenre, MlMovie
from .serializers import MlGenreSerializer, MlMovieSerializer


def success_response(message, data=None, results=None, result=None, status_code=status.HTTP_200_OK):
    payload = {
        "status": True,
        "message": message
    }
    if data is not None:
        payload["data"] = data
    if results is not None:
        payload["results"] = results
    if result is not None:
        payload["result"] = result
    return Response(payload, status=status_code)


def error_response(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    payload = {
        "status": False,
        "message": message
    }
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=status_code)


class DefaultPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class MlGenreViewSet(viewsets.ModelViewSet):
    queryset = MlGenre.objects.all()
    serializer_class = MlGenreSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return success_response(
            message="Get Successfully",
            results=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        genre = serializer.save()
        return success_response(
            message="Create Successfully",
            data=self.get_serializer(genre).data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        genre = serializer.save()
        return success_response(
            message="Update Successfully",
            data=self.get_serializer(genre).data,
            status_code=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        genre = serializer.save()
        return success_response(
            message="Update Successfully",
            data=self.get_serializer(genre).data,
            status_code=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return success_response(
            message="Delete Successfully",
            status_code=status.HTTP_200_OK
        )


class MlMovieViewSet(viewsets.ModelViewSet):
    queryset = MlMovie.objects.all().order_by("-created_at")
    serializer_class = MlMovieSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data

            return success_response(
                message="Get Successfully",
                result=paginated_data,
                status_code=status.HTTP_200_OK
            )

        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            message="Get Successfully",
            results=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        movie = serializer.save()
        return success_response(
            message="Create Successfully",
            data=self.get_serializer(movie).data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        movie = serializer.save()
        return success_response(
            message="Update Successfully",
            data=self.get_serializer(movie).data,
            status_code=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        movie = serializer.save()
        return success_response(
            message="Update Successfully",
            data=self.get_serializer(movie).data,
            status_code=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return success_response(
            message="Delete Successfully",
            status_code=status.HTTP_200_OK
        )

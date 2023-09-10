from datetime import datetime

from django.db.models import F, Count
from rest_framework import status, mixins,viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    ShowSession,
    Reservation,
    PlanetariumDome
)
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly

from planetarium.serializers import (
    ShowThemeSerializer,
    PlanetariumDomeSerializer,
    AstronomyShowSerializer,
    AstronomyShowDetailSerializer,
    AstronomyShowListSerializer,
    AstronomyShowImageSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer
)


def params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class Pagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class ShowThemeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class PlanetariumDomeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class AstronomyShowViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer

    def get_queryset(self):
        title = self.request.query_params.get("title")
        show_themes = self.request.query_params.get("show-themes")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__contains=title)
        if show_themes:
            show_themes_ids = params_to_ints(show_themes)
            queryset = queryset.filter(show_themes__in=show_themes_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        if self.action == "upload_image":
            return AstronomyShowImageSerializer
        return AstronomyShowSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image"
    )
    def upload_image(self, request, pk=None):
        astronomy_show = self.get_object()
        serializer = self.get_serializer(astronomy_show, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShowSessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = (
        ShowSession.objects.all()
        .select_related("astronomy_show", "planetarium_dome")
        .annotate(
            tickets_available=F("planetarium_dome__rows")
            * F("planetarium_dome__seats_in_row")
            - Count("tickets")
        )
    )
    serializer_class = ShowSessionSerializer
    pagination_class = Pagination

    def get_queryset(self):
        date = self.request.query_params.get("date")
        astronomy_show = self.request.query_params.get("astronomy-show")
        planetarium_dome = self.request.query_params.get("planetarium-dome")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)
        if astronomy_show:
            astronomy_show_id = params_to_ints(astronomy_show)
            queryset = queryset.filter(astronomy_show_id__in=astronomy_show_id)
        if planetarium_dome:
            planetarium_dome_id = params_to_ints(planetarium_dome)
            queryset = queryset.filter(planetarium_dome_id__in=planetarium_dome_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return ShowSessionSerializer


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = Pagination

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer

        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

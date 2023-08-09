from rest_framework import serializers

from planetarium.models import(
    ShowTheme,
    AstronomyShow,
    ShowSession,
    Ticket,
    Reservation,
    PlanetariumDome
)


class ShowThemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class PlanetariumDomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")

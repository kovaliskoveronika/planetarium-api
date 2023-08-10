from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import PlanetariumDome
from planetarium.serializers import PlanetariumDomeSerializer

PLANETARIUM_DOME_URL = reverse("planetarium:planetariumdome-list")


def sample_planetarium_dome(**params):
    defaults = {
        "name": "Sample planetarium dome",
        "rows": 10,
        "seats_in_row": 90,
    }
    defaults.update(params)

    return PlanetariumDome.objects.create(**defaults)


class UnauthorizedPlanetaryDomeTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PLANETARIUM_DOME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedPlanetariumDomeTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "testpassword123"
        )
        self.dome1 = sample_planetarium_dome(name="planetarium dome 1")
        self.dome2 = sample_planetarium_dome(name="planetarium dome 2")

        self.client.force_authenticate(self.user)

    def test_list_dome(self):
        res = self.client.get(PLANETARIUM_DOME_URL)
        domes = PlanetariumDome.objects.all()
        serializer = PlanetariumDomeSerializer(domes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_create_planetarium_dome_forbidden(self):
        payload = {
            "name": "Sample planetarium dome test create",
            "rows": 10,
            "seats_in_row": 90,
        }

        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlanetariumDome(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "testadminpassword123",
            is_staff=True
        )

        self.dome1 = sample_planetarium_dome(name="planetarium dome 1")
        self.dome2 = sample_planetarium_dome(name="planetarium dome 2")

        self.client.force_authenticate(self.user)

    def test_create_dome(self):
        payload = {
            "name": "Sample planetarium dome test create",
            "rows": 10,
            "seats_in_row": 90,
        }

        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        movie = PlanetariumDome.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))

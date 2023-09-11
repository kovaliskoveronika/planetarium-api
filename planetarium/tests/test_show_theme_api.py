from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import ShowTheme
from planetarium.serializers import ShowThemeSerializer

PLANETARIUM_DOME_URL = reverse("planetarium:showtheme-list")


def sample_show_theme(**params):
    defaults = {
        "name": "Sample show theme"
    }
    defaults.update(params)

    return ShowTheme.objects.create(**defaults)


class UnauthorizedShowThemeTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PLANETARIUM_DOME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedShowThemeTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "testpassword123"
        )

        self.theme1 = sample_show_theme(name="show theme 1")
        self.theme2 = sample_show_theme(name="show theme 2")

        self.client.force_authenticate(self.user)

    def test_list_theme(self):
        res = self.client.get(PLANETARIUM_DOME_URL)
        domes = ShowTheme.objects.all()
        serializer = ShowThemeSerializer(domes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_create_theme_forbidden(self):
        payload = {
            "name": "Sample show theme test create",
        }

        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowTheme(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "testadminpassword123",
            is_staff=True
        )

        self.theme1 = sample_show_theme(name="show theme 1")
        self.theme2 = sample_show_theme(name="show theme 2")

        self.client.force_authenticate(self.user)

    def test_create_theme(self):
        payload = {
            "name": "Sample show theme test create",
        }

        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        movie = ShowTheme.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))

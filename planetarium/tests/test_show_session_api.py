from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import AstronomyShow, PlanetariumDome, ShowSession
from planetarium.serializers import (
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer
)

SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def sample_planetarium_dome(**params):
    defaults = {
        "name": "Sample planetarium dome",
        "rows": 10,
        "seats_in_row": 90,
    }
    defaults.update(params)

    return PlanetariumDome.objects.create(**defaults)


def sample_astronomy_show(**params):
    defaults = {
        "title": "Sample astronomy show",
        "description": "Sample description",
    }
    defaults.update(params)

    return AstronomyShow.objects.create(**defaults)


def sample_show_session(**params):
    defaults = {
        "astronomy_show": sample_astronomy_show(),
        "planetarium_dome": sample_planetarium_dome(),
        "show_time": "2002-12-08"
    }
    defaults.update(params)

    return ShowSession.objects.create(**defaults)


class UnauthenticatedShowSessionTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(SHOW_SESSION_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedShowSessionTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "testpassword123"
        )

        self.show = sample_astronomy_show(title="Show_1")
        self.dome = sample_planetarium_dome(name="Dome_1")

        self.session1 = sample_show_session()
        self.session2 = sample_show_session(show_time="2023-12-12")

        self.client.force_authenticate(self.user)

    def test_list_show_sessions(self):
        response = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_show_sessions_by_date(self):
        res = self.client.get(SHOW_SESSION_URL, {"date": "2002-12-08"})

        serializer1 = ShowSessionListSerializer(self.session1)
        serializer2 = ShowSessionListSerializer(self.session2)

        self.assertContains(res, serializer1.data['show_time'])
        self.assertNotContains(res, serializer2.data['show_time'])

    def test_filter_show_sessions_by_astronomy_show(self):
        response = self.client.get(SHOW_SESSION_URL, {"astronomy-show": "1,2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_show_sessions_by_planetarium_dome(self):
        response = self.client.get(SHOW_SESSION_URL, {"planetarium-dome": "1,2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminShowSessionTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "testadminpassword123",
            is_staff=True
        )

        self.show = sample_astronomy_show(title="Show_1")
        self.dome = sample_planetarium_dome(name="Dome_1")

        self.session1 = sample_show_session()
        self.session2 = sample_show_session(show_time="2023-12-12")

        self.client.force_authenticate(self.user)

    def test_create_show_session(self):
        payload = {
            "astronomy_show": sample_astronomy_show().id,
            "planetarium_dome": sample_planetarium_dome().id,
            "show_time": "2002-12-08"
        }

        res = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import AstronomyShow, ShowTheme
from planetarium.serializers import (
    AstronomyShowListSerializer,
)

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")


def sample_astronomy_show(**params):
    defaults = {
        "title": "Sample astronomy show",
        "description": "Sample description",
    }
    defaults.update(params)

    return AstronomyShow.objects.create(**defaults)


def sample_show_theme(**params):
    defaults = {
        "name": "Mars",
    }
    defaults.update(params)

    return ShowTheme.objects.create(**defaults)


def image_upload_url(movie_id):
    """Return URL for recipe image upload"""
    return reverse("planetarium:astronomyshow-upload-image", args=[movie_id])


class AstronomyShowImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.show = sample_astronomy_show()
        self.theme = sample_show_theme()

    def tearDown(self):
        self.show.image.delete()

    def test_upload_image_to_movie(self):
        """Test uploading an image to movie"""
        url = image_upload_url(self.show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.show.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.show.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.show.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_movie_list(self):
        url = ASTRONOMY_SHOW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {

                    "title": "Title",
                    "description": "Sample description",
                    "show_themes": [self.theme.id],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        show = AstronomyShow.objects.get(title="Title")
        self.assertTrue(show.image)

    def test_image_url_is_shown_on_movie_list(self):
        url = image_upload_url(self.show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(ASTRONOMY_SHOW_URL)

        self.assertIn("image", res.data[0].keys())


class UnauthenticatedAstronomyShowTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ASTRONOMY_SHOW_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "testpassword123"
        )

        self.show_theme = sample_show_theme()
        self.show1 = sample_astronomy_show(title="Show_1")
        self.show2 = sample_astronomy_show(title="Show_2")

        self.client.force_authenticate(self.user)

    def test_filter_astronomy_shows_by_title(self):
        res = self.client.get(ASTRONOMY_SHOW_URL, {"title": "Show_1"})

        serializer1 = AstronomyShowListSerializer(self.show1)
        serializer2 = AstronomyShowListSerializer(self.show2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_astronomy_shows_by_themes(self):
        self.show1.show_themes.add(self.show_theme)

        res = self.client.get(ASTRONOMY_SHOW_URL, {"show-themes": f"{self.show_theme.id}"})

        serializer1 = AstronomyShowListSerializer(self.show1)
        serializer2 = AstronomyShowListSerializer(self.show2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_create_movie_forbidden(self):
        payload = {
            "title": "Sample astronomy show create",
            "description": "Sample description",
        }

        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAstronomyShowTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "testadminpassword123",
            is_staff=True
        )

        self.show_theme = sample_show_theme()
        self.show1 = sample_astronomy_show(title="Show_1")
        self.show2 = sample_astronomy_show(title="Show_2")

        self.client.force_authenticate(self.user)

    def test_create_astronomy_show(self):
        payload = {
            "title": "Sample astronomy show create",
            "description": "Sample description",
        }

        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        show = AstronomyShow.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(show, key))

    def test_create_astronomy_show_with_theme(self):
        payload = {
            "title": "Sample astronomy show create",
            "description": "Sample description",
            "show_themes": [self.show_theme.id]
        }

        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        show = AstronomyShow.objects.get(id=res.data["id"])
        themes = show.show_themes.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(self.show_theme, themes)

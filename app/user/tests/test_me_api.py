import os
import tempfile
from decimal import Decimal
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files import File
from rest_framework import status
from rest_framework.test import APIClient
from .test_models import create_user
from user.serializers import UserSerializer

ME_URL = reverse("user:me")
IMAGE_UPLOAD_URL = reverse("user:upload-image")


class PublicProfileAPITests(TestCase):
    """Test unauthenticated requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to make requests"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProfileAPITests(TestCase):
    """Test authenticated requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile(self):
        """Test retrieving profile"""
        res = self.client.get(ME_URL)
        profile_serializer = UserSerializer(self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, profile_serializer.data)

    def test_partial_update_profile(self):
        """Test partial updating profile"""
        original_name = self.user.name
        payload = {
            "email": "foobar@example.com",
            "password": "verygoodpass",
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))
        # Ensure original name didn't change
        self.assertEqual(self.user.name, original_name)

    def test_full_update_profile(self):
        """Test full update required all fields error"""
        payload = {"email": "newemail@example.com"}
        res = self.client.put(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure email didn't change
        self.assertNotEqual(self.user.email, payload["email"])

    def test_delete_user(self):
        """Test deleting user himself"""
        res = self.client.delete(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        me_exists = get_user_model().objects.filter(email=self.user.email)
        self.assertFalse(me_exists)

    def test_post_not_allowed(self):
        """Test post method not allowed"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_upload_profile_image(self):
        """Test uploading image to existing user"""
        # Create temporary file and save an image in it
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, "JPEG")
            image_file.seek(0)

            payload = {"profile_photo": image_file}
            res = self.client.post(IMAGE_UPLOAD_URL, payload, format="multipart")

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("profile_photo", res.data)
        self.assertTrue(os.path.exists(self.user.profile_photo.path))

    def test_upload_image_bad_request(self):
        """Test invalid payload error"""
        payload = {"profile_photo": "not image"}
        res = self.client.post(IMAGE_UPLOAD_URL, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_profile_image(self):
        """Test removing user image"""
        # Create temporary file and save an image in it
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, "JPEG")
            image_file.seek(0)

            # Read created image file and save it in user
            with open(image_file.name, "rb") as file_content:
                self.user.profile_photo.save(
                    f"test-name.jpg",
                    File(file_content),
                    save=True,
                )

        # Send empty None/null to clear image field
        payload = {"profile_photo": None}
        res = self.client.post(IMAGE_UPLOAD_URL, payload, format="json")

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Ensure there is no more image path
        with self.assertRaises(ValueError):
            os.path.exists(self.user.profile_photo.path)

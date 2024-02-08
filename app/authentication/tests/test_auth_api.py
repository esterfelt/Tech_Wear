from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from user.serializers import UserRegisterSerializer
from user.tests.test_models import create_user

CREATE_USER_URL = reverse("authentication:register")
CREATE_TOKEN_URL = reverse("authentication:token")


class AuthAPITests(TestCase):
    """Test auth API requests"""

    # Set test environment
    def setUp(self):
        # Client to simulate requests
        self.client = APIClient()

    def test_create_user(self):
        """Test user creating"""
        payload = {
            "email": "test@example.com",
            "password": "testpass",
            "name": "testname",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.get(email=payload["email"])
        user_serializer = UserRegisterSerializer(user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload["password"]))
        payload.pop("password")
        for k, v in payload.items():
            self.assertEqual(getattr(user, k), v)
        self.assertEqual(res.data, user_serializer.data)
        # Ensure there is no password in response
        self.assertNotIn("password", res.data)

    def test_email_duplication_error(self):
        """Test duplication of user email returns error"""
        payload = {"email": "test@example.com"}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_count = get_user_model().objects.filter(email=payload["email"]).count()
        self.assertEqual(user_count, 1)

    def test_password_too_short_error(self):
        """Test password shorter than 6 returns error"""
        payload = {
            "email": "test@example.com",
            "password": "12",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_generate_user_token(self):
        """Test user token creation"""
        user_credentials = {
            "email": "test@example.com",
            "password": "testpass",
        }
        create_user(**user_credentials)
        res = self.client.post(CREATE_TOKEN_URL, user_credentials)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_token_wrong_credentials(self):
        """Test wrong user credentials at token creation returns error"""
        user_credentials = {
            "email": "test@example.com",
            "password": "testpass",
        }
        create_user(**user_credentials)
        wrong_credentials = {"email": "wrong@example.com", "password": ""}
        res = self.client.post(CREATE_TOKEN_URL, wrong_credentials)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

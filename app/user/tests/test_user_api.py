from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from .test_models import create_user
from user.serializers import UserSerializer

USER_LIST_URL = reverse("user:user-list")


def get_detail_url(user_id):
    return reverse("user:user-detail", kwargs={"pk": user_id})


class PublicUserAPITests(TestCase):
    """Test unauthenticated requests"""

    def setUp(self):
        self.client = APIClient()

    def test_list_users(self):
        """Test listing users"""
        create_user("test1@example.com")
        create_user("test2@example.com")

        res = self.client.get(USER_LIST_URL)
        users = get_user_model().objects.all().order_by("id")
        serializer = UserSerializer(users, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_specific_user(self):
        """Test restrieving specific user"""
        user = create_user()
        serializer = UserSerializer(user)

        url = get_detail_url(user.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_order_by_date(self):
        """Test ordering users by date"""
        create_user("test1@example.com")
        create_user("test2@example.com")

        query_params = {"ordering": "-created_at"}
        res = self.client.get(USER_LIST_URL, query_params)
        users = get_user_model().objects.all().order_by("-created_at")
        serializer = UserSerializer(users, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_method_not_allowed_error(self):
        """Test methods except GET are not allowed"""
        res = self.client.post(USER_LIST_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from .test_models import create_category
from product.models import Category
from product.serializers import CategorySerializer

CATEGORY_LIST_URL = reverse("product:category-list")


def get_detail_url(category_id):
    return reverse("product:category-detail", kwargs={"pk": category_id})


class PublicCategoryAPITests(TestCase):
    """Test unauthenticated requests"""

    # Set test environment
    def setUp(self):
        self.client = APIClient()

    def test_list_categories(self):
        """Test category listing"""
        create_category("category_1")
        create_category("category_2")

        res = self.client.get(CATEGORY_LIST_URL)
        categories = Category.objects.all().order_by("id")
        category_serializer = CategorySerializer(instance=categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], category_serializer.data)

    def test_retrieve_specific_category(self):
        """Test retrieving a specific category"""
        category = create_category()
        url = get_detail_url(category.id)
        res = self.client.get(url)
        category_serializer = CategorySerializer(category)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, category_serializer.data)

    def test_only_admin_creates_category(self):
        """Test not admin can't create category"""
        payload = {"name": "sample category"}
        res = self.client.post(CATEGORY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        category_exists = Category.objects.filter(**payload).exists()
        self.assertFalse(category_exists)


class PrivateCategoryAPITests(TestCase):
    """Test admin requests"""

    def setUp(self):
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser("admin@example.com")
        self.client.force_authenticate(admin)

    def test_create_category(self):
        """Test category creation"""
        payload = {"name": "sample category"}
        res = self.client.post(CATEGORY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(category, k), v)
        category_serializer = CategorySerializer(category)
        self.assertEqual(res.data, category_serializer.data)

    def test_partial_update_category(self):
        """Test PATCH update category"""
        category = create_category()
        payload = {"name": "new name"}
        url = get_detail_url(category.id)
        res = self.client.patch(url, payload)

        category.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(category, k), v)
        category_serializer = CategorySerializer(category)
        self.assertEqual(res.data, category_serializer.data)

    def test_delete_category(self):
        """Test category deletion"""
        category = create_category()
        category_serializer = CategorySerializer(category)
        url = get_detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

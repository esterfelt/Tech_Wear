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
from .test_models import create_category, create_product
from product.models import Product
from product.serializers import ProductSerializer, ProductDetailSerializer

PRODUCT_LIST_URL = reverse("product:product-list")


def get_product_detail_url(product_id):
    """Get url of specific product"""
    return reverse("product:product-detail", kwargs={"pk": product_id})


def get_image_upload_url(product_id):
    """Get url to upload image to specific product"""
    return reverse("product:product-upload-image", args=[product_id])


class PublicProductAPITests(TestCase):
    """Test unauthenticated requests"""

    def setUp(self):
        self.client = APIClient()

    def test_list_products(self):
        """Test listing products"""
        category = create_category()
        create_product(category=category)
        create_product(category=category)
        res = self.client.get(PRODUCT_LIST_URL)
        products = Product.objects.all().order_by("id")
        product_serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], product_serializer.data)

    def test_retrieve_product(self):
        """Test retrieving specific product"""
        category = create_category()
        product = create_product(category=category)
        product_serializer = ProductDetailSerializer(product)
        url = get_product_detail_url(product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, product_serializer.data)

    def test_filter_by_category(self):
        """Test filtering products by category"""
        c1 = create_category("c1")
        c2 = create_category("c2")
        c3 = create_category("c3")

        p1 = create_product(c1)
        p2 = create_product(c2)
        p3 = create_product(c3)

        p1_serializer = ProductSerializer(p1)
        p2_serializer = ProductSerializer(p2)
        p3_serializer = ProductSerializer(p3)

        query_params = {"category__in": f"{c1.id},{c2.id}"}
        res = self.client.get(PRODUCT_LIST_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(p1_serializer.data, res.data["results"])
        self.assertIn(p2_serializer.data, res.data["results"])
        # This one has other category so it shouldn't be in response
        self.assertNotIn(p3_serializer.data, res.data["results"])

    def test_order_by_price(self):
        """Test ordering products by price"""
        c1 = create_category("c1")
        c2 = create_category("c2")
        create_product(c1, price=Decimal("100"))
        create_product(c2, price=Decimal("500"))

        query_params = {"ordering": "-price"}
        res = self.client.get(PRODUCT_LIST_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        products = Product.objects.all().order_by("-price")
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_order_by_rating(self):
        """Test ordering products by rating"""
        c1 = create_category("c1")
        c2 = create_category("c2")
        create_product(c1, rating=1)
        create_product(c2, rating=5)

        query_params = {"ordering": "-rating"}
        res = self.client.get(PRODUCT_LIST_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        products = Product.objects.all().order_by("-rating")
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_multiple_field_ordering(self):
        """Test ordering by multiple fields together"""
        c1 = create_category("c1")
        c2 = create_category("c2")
        c3 = create_category("c3")

        create_product(c1, rating=3, price=100)
        create_product(c2, rating=3, price=500)
        create_product(c3, rating=1, price=1000)

        query_params = {"ordering": "-price,-rating"}
        res = self.client.get(PRODUCT_LIST_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        products = Product.objects.all().order_by("-price", "-rating")
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_pagination(self):
        """Test paginating products"""
        pass

    def test_no_admin_permission_error(self):
        """Test only admin can create or edit products"""
        client = APIClient()
        user = get_user_model().objects.create_user("test@example.com")
        client.force_authenticate(user=user)

        payload = {
            "name": "testname",
            "description": "some desc",
            "brand": "test brand",
            "price": Decimal("100.99"),
            "stock": 100,
        }
        res = client.post(PRODUCT_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        # Ensure the product isn't created
        product_exists = Product.objects.filter(**payload).exists()
        self.assertFalse(product_exists)


class PrivateProductAPITests(TestCase):
    """Test authenticated admin requests"""

    def setUp(self):
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser("admin@example.com")
        self.client.force_authenticate(admin)

    def test_create_product(self):
        """Test creating a product"""
        category = create_category()
        payload = {
            "name": "testname",
            "description": "some desc",
            "brand": "test brand",
            "price": Decimal("100.99"),
            "stock": 100,
            "category": category.id,
        }
        res = self.client.post(PRODUCT_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(pk=res.data["id"])
        self.assertEqual(product.category, category)
        payload.pop("category")
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        product_serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, product_serializer.data)

    def test_partial_update_product(self):
        """Test partial update of product"""
        category = create_category()
        original_name = "original-name"
        product = create_product(category=category, name=original_name)

        payload = {
            "description": "new desc",
            "brand": "new brand",
        }
        url = get_product_detail_url(product.id)
        res = self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Ensure original name didn't change
        self.assertEqual(product.name, original_name)
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        product_serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, product_serializer.data)

    def test_full_update_product_error(self):
        """Test full update of product requires all fields"""
        category = create_category()
        product = create_product(category=category)

        payload = {"name": "new name"}
        url = get_product_detail_url(product.id)
        res = self.client.put(url, payload)

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure the product fields didn't change
        for k, v in payload.items():
            self.assertNotEqual(getattr(product, k), v)

    def test_delete_product(self):
        """Test product deletion"""
        category = create_category()
        product = create_product(category=category)
        url = get_product_detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_upload_product_image(self):
        """Test uploading image to existing product"""
        category = create_category()
        product = create_product(category=category)
        url = get_image_upload_url(product.id)

        # Create temporary file and save an image in it
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, "JPEG")
            image_file.seek(0)

            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(product.image.path))

    def test_upload_product_image_bad_request(self):
        """Test invalid payload"""
        category = create_category()
        product = create_product(category=category)

        url = get_image_upload_url(product.id)
        payload = {"image": "not image"}
        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_product_image(self):
        """Test removing product image"""

        # Create temporary file and save an image in it
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, "JPEG")
            image_file.seek(0)

            # Read created image file and save it in product
            with open(image_file.name, "rb") as file_content:
                category = create_category()
                product = create_product(category=category)
                product.image.save(f"test-name.jpg", File(file_content), save=True)

        url = get_image_upload_url(product.id)
        # Send empty None/null to clear image field
        payload = {"image": None}
        res = self.client.post(url, payload, format="json")

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Ensure there is no more image path
        with self.assertRaises(ValueError):
            os.path.exists(product.image.path)

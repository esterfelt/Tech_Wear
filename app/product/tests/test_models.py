from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from product.models import (
    Category,
    Product,
    generate_product_image_path,
    Review,
)


def create_category(name="sample category"):
    return Category.objects.create(name=name)


def create_product(category, **fields):
    default_fields = {
        "name": "testname",
        "description": "some desc",
        "brand": "test brand",
        "price": Decimal("100.99"),
        "stock": 100,
    }
    default_fields.update(**fields)
    return Product.objects.create(category=category, **default_fields)


def create_review(user, product, **fields):
    default_fields = {
        "rating": 5,
        "commentary": "sample commentary",
    }
    default_fields.update(**fields)
    return Review.objects.create(user=user, product=product, **default_fields)


class CategoryModelTests(TestCase):
    """Test Category model"""

    def test_create_category(self):
        """Test creating Category instance"""
        category_name = "sample category"
        category = create_category(category_name)

        self.assertEqual(str(category), category_name)


class ProductModelTests(TestCase):
    """Test Product model"""

    def test_create_product(self):
        """Test creating Product instance"""
        category = create_category()
        product_name = "sample product"
        product = create_product(name=product_name, category=category)

        self.assertEqual(str(product), product_name)

    @patch("product.models.uuid4")
    def test_product_image_uuid(self, mock_uuid):
        """Test generating product image path"""
        sample_uuid = "sample-uuid"
        mock_uuid.return_value = sample_uuid
        image_path = generate_product_image_path(None, "example.jpg")

        self.assertEqual(image_path, f"uploads/product/{sample_uuid}.jpg")

    def test_no_product_prop_name_duplication(self):
        """Test product must have unique property names"""
        category = create_category()

        # Should raise error cuz product can't have
        # two props with the same name
        with self.assertRaises(ValidationError):
            create_product(
                category=category,
                properties={"Color": "red", "COLOR": "blue"},
            )

    def test_rating_update_when_review_added(self):
        """
        Test product's rating is updated whenever review
        for that created or edited
        """
        category = create_category()
        product = create_product(category=category)

        user = get_user_model().objects.create_user(email="test@example.com")
        create_review(user, product, rating=3)

        self.assertEqual(product.rating, 3)


class ReviewModelTests(TestCase):
    """Test Review model"""

    def setUp(self):
        category = create_category()
        self.product = create_product(category)
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
        )

    def test_create_review(self):
        """Test creating Review instance"""
        fields = {"rating": 1, "commentary": "test comment"}
        review = create_review(self.user, self.product, **fields)

        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)
        for k, v in fields.items():
            self.assertEqual(getattr(review, k), v)

    def test_limit_user_review_per_product(self):
        """Test user can leave only 1 review for the product"""
        with self.assertRaises(IntegrityError):
            create_review(self.user, self.product)
            create_review(self.user, self.product)

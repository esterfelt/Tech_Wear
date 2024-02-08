from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from .test_models import create_review, create_category, create_product
from product.models import Review
from product.serializers import ReviewSerializer

REVIEW_LIST_URL = reverse("product:review-list")


def get_detail_url(review_id):
    return reverse("product:review-detail", kwargs={"pk": review_id})


class PublicReviewAPITests(TestCase):
    """Test unauthenticated requests"""

    # Set test environment
    def setUp(self):
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(email="test@example.com")
        self.user2 = get_user_model().objects.create_user(email="test2@example.com")

    def test_list_reviews(self):
        """Test listing reviews"""
        category = create_category()
        p1 = create_product(category)
        p2 = create_product(category)
        create_review(user=self.user1, product=p1)
        create_review(user=self.user2, product=p2)

        res = self.client.get(REVIEW_LIST_URL)
        reviews = Review.objects.all().order_by("id")
        review_serializer = ReviewSerializer(instance=reviews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], review_serializer.data)

    def test_retrieve_specific_review(self):
        """Test retrieving a specific review"""
        category = create_category()
        product = create_product(category)
        review = create_review(self.user1, product)

        url = get_detail_url(review.id)
        res = self.client.get(url)
        review_serializer = ReviewSerializer(review)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, review_serializer.data)

    def test_filter_reviews_by_product(self):
        """Test filtering reviews by product"""
        category = create_category()
        p1 = create_product(category)
        p2 = create_product(category)

        r1 = create_review(user=self.user1, product=p1)
        r2 = create_review(user=self.user2, product=p2)
        r1_serializer = ReviewSerializer(r1)
        r2_serializer = ReviewSerializer(r2)

        query_params = {"product": p1.id}
        res = self.client.get(REVIEW_LIST_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(r1_serializer.data, res.data["results"])
        self.assertNotIn(r2_serializer.data, res.data["results"])

    def test_filter_reviews_by_user(self):
        """Test filtering reviews by user"""
        category = create_category()
        product = create_product(category)

        r1 = create_review(user=self.user1, product=product)
        r2 = create_review(user=self.user2, product=product)
        r1_serializer = ReviewSerializer(r1)
        r2_serializer = ReviewSerializer(r2)

        query_params = {"user": self.user2.id}
        res = self.client.get(REVIEW_LIST_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(r2_serializer.data, res.data["results"])
        self.assertNotIn(r1_serializer.data, res.data["results"])

    def test_order_by_rating(self):
        """Test ordering reviews by rating"""
        category = create_category()
        product = create_product(category)
        create_review(self.user1, product, rating=5)
        create_review(self.user2, product, rating=1)

        query_params = {"ordering": "rating"}
        res = self.client.get(REVIEW_LIST_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        reviews = Review.objects.all().order_by("rating")
        serializer = ReviewSerializer(reviews, many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_order_by_date(self):
        """Test ordering reviews by date"""
        category = create_category()
        product = create_product(category)
        create_review(self.user1, product)
        create_review(self.user2, product)

        query_params = {"ordering": "-created_at"}
        res = self.client.get(REVIEW_LIST_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        reviews = Review.objects.all().order_by("-created_at")
        serializer = ReviewSerializer(reviews, many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_auth_required_error(self):
        """Test auth is required to create or edit reviews"""
        category = create_category()
        product = create_product(category)

        payload = {
            "rating": 3,
            "user": self.user1.id,
            "product": product.id,
        }
        res = self.client.post(REVIEW_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        # Ensure the review isn't created
        review_count = Review.objects.all().count()
        self.assertEqual(review_count, 0)


class PrivateReviewAPITests(TestCase):
    """Test authenticated requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@example.com")
        self.client.force_authenticate(self.user)
        category = create_category()
        self.product = create_product(category)

    def test_create_review(self):
        """Test review creation"""
        payload = {
            "rating": 1,
            "user": self.user.id,
            "product": self.product.id,
        }
        res = self.client.post(REVIEW_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        review = Review.objects.get(id=res.data["id"])
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)
        review_serializer = ReviewSerializer(review)
        self.assertEqual(res.data, review_serializer.data)

    def test_one_user_review_per_product(self):
        """
        Test return error if user tries create more
        than 1 review on product
        """
        create_review(self.user, self.product)

        payload = {
            "rating": 1,
            "user": self.user.id,
            "product": self.product.id,
        }
        res = self.client.post(REVIEW_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure second review not created
        review_count = Review.objects.filter(
            user=self.user,
            product=self.product,
        ).count()
        self.assertEqual(review_count, 1)

    def test_partial_update_review(self):
        """Test PATCH update review"""
        original_rating = 1
        review = create_review(self.user, self.product, rating=original_rating)

        payload = {"commentary": "new comment"}
        url = get_detail_url(review.id)
        res = self.client.patch(url, payload)

        review.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(review.commentary, payload["commentary"])
        self.assertEqual(review.rating, original_rating)
        review_serializer = ReviewSerializer(review)
        self.assertEqual(res.data, review_serializer.data)

    def test_full_update_review(self):
        """Test PUT update requires all fields error"""
        review = create_review(self.user, self.product)
        payload = {"commentary": "new comment"}
        url = get_detail_url(review.id)
        res = self.client.put(url, payload)

        review.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure the review fields didn't change
        for k, v in payload.items():
            self.assertNotEqual(getattr(review, k), v)

    def test_no_update_review_user(self):
        """Test once review is created user field can't be changed"""
        other_user = get_user_model().objects.create_user("other@example.com")
        review = create_review(self.user, self.product)

        payload = {"user": other_user.id}
        url = get_detail_url(review.id)
        self.client.patch(url, payload)

        review.refresh_from_db()
        self.assertEqual(review.user, self.user)

    def test_no_update_review_product(self):
        """Test once review is created product field can't be changed"""
        category = create_category("c")
        other_product = create_product(category)
        review = create_review(self.user, self.product)

        payload = {"product": other_product.id}
        url = get_detail_url(review.id)
        self.client.patch(url, payload)

        review.refresh_from_db()
        self.assertEqual(review.product, self.product)

    def test_delete_review(self):
        """Test review deletion"""
        review = create_review(self.user, self.product)
        review_serializer = ReviewSerializer(review)

        url = get_detail_url(review.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_user_review_error(self):
        """Test deleting other users's review returns error"""
        other_user = get_user_model().objects.create_user("other@example.com")
        review = create_review(user=other_user, product=self.product)

        url = get_detail_url(review.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        # Ensure not deleted
        self.assertTrue(Review.objects.filter(id=review.id).exists())


class AdminReviewAPITests(TestCase):
    """Test admin requests"""

    def setUp(self):
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser("admin@example.com")
        self.client.force_authenticate(admin)

    def test_delete_other_user_review(self):
        """Test admin deleting other user review"""
        category = create_category()
        product = create_product(category)
        other_user = get_user_model().objects.create_user("other@example.com")
        review = create_review(other_user, product)

        url = get_detail_url(review.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

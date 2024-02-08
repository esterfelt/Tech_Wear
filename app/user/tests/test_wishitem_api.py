from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .test_models import (
    create_user,
    create_category,
    create_product,
    create_wishitem,
)
from user.models import WishItem
from user.serializers import (
    WishItemSerializer,
    WishItemExpandedSerializer,
)


WISH_ITEM_LIST_URL = reverse("user:wishitem-list")


def get_wishitem_detail_url(wishitem_id):
    return reverse("user:wishitem-detail", args=[wishitem_id])


class PublicWishItemAPITests(TestCase):
    """Test unautenticated requests"""

    def test_auth_required(self):
        """Test auth required to make requests"""
        client = APIClient()
        res = client.get(WISH_ITEM_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWishItemAPITests(TestCase):
    """Test authenticated requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_wishitems(self):
        """Test listing wish items"""
        category = create_category()
        prod1 = create_product(category)
        prod2 = create_product(category)

        create_wishitem(self.user, prod1)
        create_wishitem(self.user, prod2)

        res = self.client.get(WISH_ITEM_LIST_URL)
        wish_items = WishItem.objects.all().order_by("id")
        serializer = WishItemExpandedSerializer(wish_items, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_wishitems_limited_to_user(self):
        """Test user can only deal with his own wish items"""
        other_user = create_user("other@example.com")
        category = create_category()
        prod = create_product(category)

        create_wishitem(other_user, prod)
        create_wishitem(self.user, prod)

        res = self.client.get(WISH_ITEM_LIST_URL)
        wish_items = WishItem.objects.filter(user=self.user)
        serializer = WishItemExpandedSerializer(wish_items, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_specific_wishitem(self):
        """Test retrieve specific wish item"""
        category = create_category()
        prod = create_product(category)
        wish_item = create_wishitem(self.user, prod)

        url = get_wishitem_detail_url(wish_item.id)
        res = self.client.get(url)
        serializer = WishItemExpandedSerializer(wish_item)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_wishitem(self):
        """Test creating wish item"""
        category = create_category()
        prod = create_product(category)

        payload = {
            "product": prod.id,
        }
        res = self.client.post(WISH_ITEM_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        wish_item = WishItem.objects.get(id=res.data["id"])
        serializer = WishItemSerializer(wish_item)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(wish_item.user, self.user)
        self.assertEqual(wish_item.product, prod)

    def test_duplicating_wishitems_error(self):
        """Test duplication of user and product fields leads to error"""
        category = create_category()
        prod = create_product(category)
        create_wishitem(self.user, prod)

        payload = {
            "user": self.user.id,
            "product": prod.id,
        }
        res = self.client.post(WISH_ITEM_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        wish_item_count = WishItem.objects.filter(
            user=self.user,
            product=prod,
        ).count()
        # Ensure duplicate not created
        self.assertEqual(wish_item_count, 1)

    def test_delete_wishitem(self):
        """Test deleting wish item"""
        category = create_category()
        prod = create_product(category)
        wish_item = create_wishitem(self.user, prod)

        url = get_wishitem_detail_url(wish_item.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .test_models import create_user, create_cartitem, create_category, create_product
from user.models import Cart, CartItem
from user.serializers import CartItemSerializer, CartItemExpandedSerializer


CART_ITEM_LIST_URL = reverse("user:cartitem-list")


def get_cartitem_detail_url(cartitem_id):
    return reverse("user:cartitem-detail", args=[cartitem_id])


class PublicCartItemAPITests(TestCase):
    """Test unautenticated requests"""

    def test_auth_required(self):
        """Test auth required to make requests"""
        client = APIClient()
        res = client.get(CART_ITEM_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCartItemAPITests(TestCase):
    """Test autenticated requests"""

    def setUp(self):
        user = create_user()
        self.cart = Cart.objects.get(user=user)
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_list_cartitems(self):
        """Test listing cart items"""
        category = create_category()
        prod1 = create_product(category)
        prod2 = create_product(category)

        create_cartitem(self.cart, prod1)
        create_cartitem(self.cart, prod2)

        res = self.client.get(CART_ITEM_LIST_URL)
        cart_items = CartItem.objects.all().order_by("id")
        serializer = CartItemExpandedSerializer(cart_items, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_cartitems_limited_to_user(self):
        """Test user can only deal with his own cart items"""
        other_user = create_user("other@example.com")
        other_cart = Cart.objects.get(user=other_user)

        category = create_category()
        prod = create_product(category)

        create_cartitem(other_cart, prod)
        create_cartitem(self.cart, prod)

        res = self.client.get(CART_ITEM_LIST_URL)
        cart_items = CartItem.objects.filter(cart=self.cart)
        serializer = CartItemExpandedSerializer(cart_items, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_specific_cartitem(self):
        """Test retrieving specific cart item"""
        category = create_category()
        prod = create_product(category)
        cart_item = create_cartitem(self.cart, prod)

        url = get_cartitem_detail_url(cart_item.id)
        res = self.client.get(url)
        serializer = CartItemExpandedSerializer(cart_item)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_cartitem(self):
        """Test creating cart item"""
        category = create_category()
        prod = create_product(category)

        payload = {
            "product": prod.id,
            "quantity": 5,
        }
        res = self.client.post(CART_ITEM_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cart_item = CartItem.objects.get(id=res.data["id"])
        serializer = CartItemSerializer(cart_item)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, prod)
        self.assertEqual(cart_item.quantity, payload["quantity"])

    def test_partial_update_cartitem(self):
        """Test partial updating cart item"""
        category = create_category()
        prod = create_product(category)
        cart_item = create_cartitem(self.cart, prod)

        payload = {"quantity": 10}
        url = get_cartitem_detail_url(cart_item.id)
        res = self.client.patch(url, payload)

        cart_item.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(cart_item.quantity, payload["quantity"])
        # Ensure other fields didn't change
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, prod)

    def test_full_update_cartitem(self):
        """Test full update requires all fields"""
        category = create_category()
        prod = create_product(category)
        cart_item = create_cartitem(self.cart, prod)

        payload = {"quantity": 10}
        url = get_cartitem_detail_url(cart_item.id)
        res = self.client.put(url, payload)

        cart_item.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure original field didn't change
        self.assertNotEqual(cart_item.quantity, payload["quantity"])

    def test_delete_cartitem(self):
        """Test deleting cart item"""
        category = create_category()
        prod = create_product(category)
        cart_item = create_cartitem(self.cart, prod)

        url = get_cartitem_detail_url(cart_item.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

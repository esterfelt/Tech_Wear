from unittest.mock import patch
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from user.models import Address, generate_user_image_path, Cart, CartItem, WishItem
from product.tests.test_models import create_category, create_product


def create_user(email="test@example.com", password=None, **fields):
    return get_user_model().objects.create_user(email, password, **fields)


def create_address(**fields):
    default_fields = {
        "country": "Wakanda",
        "city": "Sample city",
        "street": "Sample street",
        "house": 100,
        "postal_code": "021333",
    }
    default_fields.update(**fields)
    return Address.objects.create(**default_fields)


def create_cartitem(cart, product, quantity=1):
    return CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=quantity,
    )


def create_wishitem(user, product):
    return WishItem.objects.create(user=user, product=product)


class UserModelTests(TestCase):
    """Test User model"""

    def test_create_user_with_email(self):
        """Test creating a user with email"""
        email = "test@example.com"
        password = "testpass"
        user = create_user(email, password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_creating_user_without_email_error(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            create_user(email="")

    def test_normalize_new_user_email(self):
        """Test whether new user's email is normalized"""
        sample_emails = [
            ["TEST@EXAMPLE.COM", "TEST@example.com"],
            ["Test@Example.com", "Test@example.com"],
            ["tesT@example.Com", "tesT@example.com"],
        ]

        for raw, expected in sample_emails:
            user = create_user(email=raw)
            self.assertEqual(user.email, expected)

    def test_create_user_with_address(self):
        """Test creating user with address"""
        address = create_address()
        user = create_user(address=address)

        self.assertEqual(user.address, address)

    def test_create_superuser(self):
        """Test creating super user"""
        email = "test@example.com"
        password = "testpass"
        superuser = get_user_model().objects.create_superuser(email, password)

        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.check_password(password))
        self.assertTrue(superuser.is_superuser)

    @patch("user.models.uuid4")
    def test_user_image_uuid(self, mock_uuid):
        """Test generating user profile image path"""
        sample_uuid = "sample-uuid"
        mock_uuid.return_value = sample_uuid
        image_path = generate_user_image_path(None, "example.jpg")

        self.assertEqual(image_path, f"uploads/user/{sample_uuid}.jpg")

    def test_create_user_with_address(self):
        """Test creating user with address"""
        address = create_address()
        user = create_user(address=address)

        self.assertEqual(user.address, address)


class AddressModelTests(TestCase):
    """Test address model"""

    def test_create_address(self):
        """Test creating an address"""
        fields = {
            "country": "Wakanda",
            "city": "Sample city",
            "street": "Sample street",
            "house": 100,
            "postal_code": "021333",
        }
        address = create_address(**fields)

        for k, v in fields.items():
            self.assertEqual(getattr(address, k), v)


class CartModelTests(TestCase):
    """Test Cart model"""

    def test_create_cart_with_user(self):
        """Test a cart for the new user is created"""
        user = create_user()
        cart_exists = Cart.objects.filter(user=user).exists()

        self.assertTrue(cart_exists)


class CartItemModelTests(TestCase):
    """Test CartItem model"""

    def setUp(self):
        user = create_user()
        self.cart = Cart.objects.get(user=user)
        category = create_category()
        self.prod = create_product(category)

    def test_create_cartitem(self):
        """Test creating cart item"""
        cart_item = CartItem.objects.create(
            cart=self.cart, product=self.prod, quantity=1
        )

        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.prod)

    # Merge same cart items by increasing quantity
    def test_merge_same_cartitems(self):
        """Test merging two same cartitems"""
        first = create_cartitem(self.cart, self.prod, 1)
        create_cartitem(self.cart, self.prod, 1)

        first.refresh_from_db()
        self.assertEqual(first.quantity, 2)
        cartitem_count = CartItem.objects.filter(
            cart=self.cart,
            product=self.prod,
        ).count()
        self.assertEqual(cartitem_count, 1)


class WishItemModelTests(TestCase):
    """Test WishItem model"""

    def test_create_withitem(self):
        """Test creating wish item"""
        user = create_user()
        category = create_category()
        prod = create_product(category)
        wishitem = create_wishitem(user, prod)

        self.assertEqual(wishitem.user, user)
        self.assertEqual(wishitem.product, prod)

    def test_wishitem_duplication_error(self):
        """Test duplicating user and product fields raises error"""
        user = create_user()
        category = create_category()
        prod = create_product(category)

        with self.assertRaises(IntegrityError):
            create_wishitem(user, prod)
            create_wishitem(user, prod)

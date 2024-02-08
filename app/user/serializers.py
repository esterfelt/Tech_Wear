from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Address, CartItem, WishItem
from .tests.test_models import create_user
from product.serializers import ProductSerializer


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["country", "city", "street", "house", "postal_code"]
        read_only_fields = ["id"]
        required_fields = ["country, street"]


class UserRegisterSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user registration"""

    class Meta:
        model = get_user_model()
        fields = ["name", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 6},
        }

    def create(self, validated_data):
        # Create user with hashing password
        return get_user_model().objects.create_user(**validated_data)


class UserSerializer(UserRegisterSerializer):
    address = AddressSerializer(required=False)

    class Meta(UserRegisterSerializer.Meta):
        fields = UserRegisterSerializer.Meta.fields + [
            "id",
            "surname",
            "profile_photo",
            "address",
        ]
        read_only_fields = ["id", "profile_photo"]

    def create(self, validated_data):
        address_data = validated_data.pop("address", None)
        # Create user with hashing password
        user = super().create(validated_data)
        # Create address and relate it to user
        if address_data:
            self._set_address(address_data, user)
        return user

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)
        password = validated_data.pop("password", None)
        super().update(instance, validated_data)
        # Update password separately to hash it
        if password:
            instance.set_password(password)

        # Reset address
        if address_data is not None:
            self._reset_address(address_data, instance)

        instance.save()
        return instance

    def _set_address(self, address_data, user):
        """Create address and relate it to user"""
        address_obj = Address.objects.create(**address_data)
        user.address = address_obj
        user.save()

    def _reset_address(self, address_data, user):
        """Reset address with ensuring no missing fields"""
        if user.address:
            user.address.delete()
            user.address = None
        if address_data == {}:
            return
        # Ensure all fields provided even when PATCH request
        missing_fields = set(AddressSerializer.Meta.fields) - set(address_data)
        if missing_fields:
            msg = f"These fields are required: {missing_fields}"
            raise serializers.ValidationError(msg)
        self._set_address(address_data, user)


# Simplified one to return only user id and image in response
class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "profile_photo"]
        read_only_fields = ["id"]
        extra_kwargs = {"profile_photo": {"required": True}}


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "quantity"]
        read_only_fields = ["id", "cart"]


class CartItemExpandedSerializer(CartItemSerializer):
    """Extended to output all product data when list, retrieve actions"""

    product = ProductSerializer()


class WishItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishItem
        fields = ["id", "user", "product"]
        read_only_fields = ["id", "user"]

    # Check for uniqueness constraint violation during creation
    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs.get("product")

        # If the constraint violated return validation error
        if WishItem.objects.filter(user=user, product=product):
            msg = "You have already wished this product!"
            raise serializers.ValidationError(msg)

        return attrs


class WishItemExpandedSerializer(WishItemSerializer):
    """Extended to output all product data when list, retrieve actions"""

    product = ProductSerializer()

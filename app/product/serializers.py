from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "price",
            "image",
            "rating",
        ]
        read_only_fields = ["id", "image", "rating"]


class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            "description",
            "stock",
            "category",
            "properties",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ProductSerializer.Meta.read_only_fields + [
            "created_at",
            "updated_at",
        ]


# Simplified one to return only product id and image in response
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "commentary",
            "user",
            "product",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate(self, attrs):
        # Get default user from request
        user_id = self.context["request"].user
        product_id = attrs.get("product")

        # Return error if the user already wrote review for the product
        if Review.objects.filter(user=user_id, product=product_id):
            msg = "You already wrote a review for this product!"
            raise serializers.ValidationError(msg)

        return attrs

    # TODO Indicate in api docs that "product" field isn't available when PATCH and PUT
    # Prevent updating field "product"
    def update(self, instance, validated_data):
        validated_data.pop("product", None)
        return super().update(instance, validated_data)

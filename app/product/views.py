from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductSerializer,
    ProductImageSerializer,
    ReviewSerializer,
)
from .models import Category, Product, Review


class BaseViewSet(viewsets.ModelViewSet):
    """Basic attributes for category and products"""

    authentication_classes = [TokenAuthentication]

    # Permis only admins to create and edit
    def get_permissions(self):
        if self.action not in ["list", "retrieve"]:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class CategoryViewSet(BaseViewSet):
    """Manage categories"""

    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("id")


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="category__in",
                type=OpenApiTypes.STR,
                description="Comma separated list of category IDs to filter by",
            ),
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                description="Comma separated list of fields to order by: `price`, `rating`",
            ),
        ]
    )
)
class ProductViewSet(BaseViewSet):
    """Manage products"""

    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all().order_by("id")
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {"category": ["in"]}
    ordering_fields = ["price", "rating"]

    # Manually implemented filtering, ordering features
    # def get_queryset(self):
    #     queryset = self.queryset

    #     # Filter by category feature
    #     category_ids = self.request.query_params.get("categories")
    #     if category_ids:
    #         ids = [int(id) for id in category_ids.split(",")]
    #         queryset = queryset.filter(category__id__in=ids)

    #     # Sort feature
    #     fields_str = self.request.query_params.get("ordering")
    #     if fields_str:
    #         fields = fields_str.split(",")
    #         queryset = queryset.order_by(*fields)

    #     return queryset

    # Change serializer when "list" and "upload_image" actions
    def get_serializer_class(self):
        if self.action == "list":
            return ProductSerializer
        elif self.action == "upload_image":
            return ProductImageSerializer
        return super().get_serializer_class()

    # Custom action to update specific product's image field
    @action(["post"], detail=True, url_name="upload-image")
    def upload_image(self, request, pk):
        """Upload image to specific product"""
        product = self.get_object()
        image_serializer = self.get_serializer(
            instance=product,
            data=request.data,
        )
        image_serializer.is_valid(raise_exception=True)
        image_serializer.save()
        return Response(image_serializer.data, status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="product",
                type=OpenApiTypes.STR,
                description="Comma separated list of product IDs to filter by",
            ),
            OpenApiParameter(
                name="user",
                type=OpenApiTypes.STR,
                description="Comma separated list of user IDs to filter by",
            ),
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                description="Comma separated list of fields to order by. Available fields: `created_at`, `rating`",
            ),
        ]
    )
)
class ReviewViewSet(viewsets.ModelViewSet):
    """Manage reviews"""

    authentication_classes = [TokenAuthentication]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all().order_by("id")
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["product", "user"]
    ordering_fields = ["created_at", "rating"]

    # Permis only authenticated users to create and edit
    def get_permissions(self):
        if self.action not in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if self.action not in ["update", "partial_update", "destroy"]:
            return queryset

        # Allow admin to delete any review
        if user.is_staff and self.action == "destroy":
            return super().get_queryset()

        # Allow regular user to edit only his own reviews
        return self.queryset.filter(user=self.request.user)

    # Set field "user" as "request.user" by default when creating review
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

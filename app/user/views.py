from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework import viewsets, views
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from .serializers import (
    UserSerializer,
    UserImageSerializer,
    CartItemSerializer,
    CartItemExpandedSerializer,
    WishItemSerializer,
    WishItemExpandedSerializer,
)
from .models import Cart, WishItem


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                description="Comma separated list of fields to order by: `created_at`",
            ),
        ]
    )
)
class UserListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Manage User list and retrieve operations"""

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all().order_by("id")
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]


class ProfileRUDView(generics.RetrieveUpdateDestroyAPIView):
    """Manage user profile retrieve, update, destroy operations"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ProfileImageAPIView(views.APIView):
    """Manage User profile image uploading"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserImageSerializer

    def post(self, request):
        image_serializer = self.serializer_class(
            self.request.user,
            request.data,
        )
        image_serializer.is_valid(raise_exception=True)
        image_serializer.save()
        return Response(data=image_serializer.data, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):
    """Manage cart items"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = CartItemSerializer

    # Limit cart items to user
    def get_queryset(self):
        cart = Cart.objects.get(user=self.request.user)
        return cart.cartitem_set.all().order_by("id")

    def get_serializer_class(self):
        # Expand product data when list and retrieve actions
        if self.action in ["list", "retrieve"]:
            return CartItemExpandedSerializer
        return super().get_serializer_class()

    # Associate cart item with user's cart by default
    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        serializer.save(cart=cart)


class WishItemViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Manage whish items"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = WishItemSerializer

    # Limit wish items to user
    def get_queryset(self):
        user = self.request.user
        return user.wishitem_set.all().order_by("id")

    def get_serializer_class(self):
        # Expand product data when list and retrieve actions
        if self.action in ["list", "retrieve"]:
            return WishItemExpandedSerializer
        return super().get_serializer_class()

    # Associate the wish item with the user by default
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

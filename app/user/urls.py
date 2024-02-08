from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserListRetrieveViewSet,
    ProfileRUDView,
    ProfileImageAPIView,
    CartItemViewSet,
    WishItemViewSet,
)

app_name = "user"

router = DefaultRouter()
router.register("users", UserListRetrieveViewSet)
router.register("cart", CartItemViewSet, basename="cartitem")
router.register("whishlist", WishItemViewSet, basename="wishitem")

urlpatterns = [
    path("", include(router.urls)),
    path("me/", ProfileRUDView.as_view(), name="me"),
    path("me/upload-image/", ProfileImageAPIView.as_view(), name="upload-image"),
]

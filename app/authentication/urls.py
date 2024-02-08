from django.urls import path
from .views import RegisterUserView, ObtainTokenView

app_name = "authentication"

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("token/", ObtainTokenView.as_view(), name="token"),
]

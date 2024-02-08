from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import AuthTokenSeralizer
from user.serializers import UserRegisterSerializer


class RegisterUserView(CreateAPIView):
    """Manage user creation"""

    serializer_class = UserRegisterSerializer


class ObtainTokenView(ObtainAuthToken):
    """Manage token creation and obtaining"""

    serializer_class = AuthTokenSeralizer

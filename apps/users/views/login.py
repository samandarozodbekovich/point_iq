from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.serializers.login import LoginSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

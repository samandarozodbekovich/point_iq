from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.serializers.login_refresh import LoginRefreshSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer

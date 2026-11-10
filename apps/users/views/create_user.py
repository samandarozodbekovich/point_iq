from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.shared.throttles import SignupThrottle
from apps.users.serializers.sign_up import SignUpSerializer
from apps.users.models.user import User


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny,]
    throttle_classes = [SignupThrottle]



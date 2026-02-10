
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.serializers.resend_code import ResendCodeSerializer

class ResendCodeView(APIView):
    permission_classes = [AllowAny,]
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "success": True,
            "message": "Code sent successfully",
            "auth_status": user.auth_status,
        })
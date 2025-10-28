from django.urls import path

from apps.users.views import LoginView, LogoutView, ResetPasswordView, VerifyAPIView, ChangeUserInfoView, \
    LoginRefreshView, GetNewVerificationView, ForgotPasswordView, ResendCodeView
from apps.users.views.create_user import CreateUserView

urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('resend-code/', ResendCodeView.as_view(), name='resend_code'),
    path('change-info/', ChangeUserInfoView.as_view(), name='change_info'),
    path('login/', LoginView.as_view(), name='login'),
    path('login-refresh/', LoginRefreshView.as_view(), name='login_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('get-new-verification/', GetNewVerificationView.as_view(), name='get_new_verification'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('verify/', VerifyAPIView.as_view(), name='verify'),
]
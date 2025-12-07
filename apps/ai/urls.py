from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminHistoryViewSet,
    UniversalAIView,
    UserHistoryView,
    UserDeleteHistoryView
)

router = DefaultRouter()
router.register(r'admin/history', AdminHistoryViewSet, basename='admin_history')

app_name = 'ai'

urlpatterns = [
    # Admin routes (router)
    path('', include(router.urls)),

    # User routes
    path('chat/', UniversalAIView.as_view(), name='chat'),
    path('history/', UserHistoryView.as_view(), name='history_list'),
    path('history/<int:pk>/', UserHistoryView.as_view(), name='history_detail'),
    path('history/<int:pk>/delete/', UserDeleteHistoryView.as_view(), name='history_delete'),
]
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    logout_view,
    current_user_view,
    ChangePasswordView,
    UserAPIKeyListCreateView,
    UserAPIKeyDetailView,
    event_register_view,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('me/', current_user_view, name='current-user'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Event registration
    path('event-register/', event_register_view, name='event-register'),
    
    # API Keys
    path('api-keys/', UserAPIKeyListCreateView.as_view(), name='api-key-list-create'),
    path('api-keys/<uuid:pk>/', UserAPIKeyDetailView.as_view(), name='api-key-detail'),
]

from django.urls import path

from .views import RegistrationView, SecurityTokenView, ChangePasswordView

urlpatterns = [
    path('account/', RegistrationView.as_view(), name='account'),
    path('security/token/', SecurityTokenView.as_view(), name='security_token'),
    path('security/change-password/', ChangePasswordView.as_view(), name='change_password'),
]

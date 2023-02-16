from django.urls import path

from .views import SecurityTokenView, RequestRegistrationView, ConfirmRegistrationView, RequestRestorePasswordView, \
    RestorePasswordView

urlpatterns = [
    path('security/token/', SecurityTokenView.as_view(), name='security_token'),
    path('account/new/', RequestRegistrationView.as_view(), name='request_reg'),
    path('account/', ConfirmRegistrationView.as_view(), name='confirm'),
    path('account/password/restore/', RequestRestorePasswordView.as_view(), name='request_res'),
    path('account/password/', RestorePasswordView.as_view(), name='restore'),
]

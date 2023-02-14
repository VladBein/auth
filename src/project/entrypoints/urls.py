from django.urls import path

from .views import UserView, SecurityToken

urlpatterns = [
    path('account/', UserView.as_view(), name='account'),
    path('security/token/', SecurityToken.as_view(), name='security_token'),
]

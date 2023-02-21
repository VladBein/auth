from rest_framework import routers

from .views import SecurityTokenView, AccountView

router = routers.DefaultRouter()
router.register('account', AccountView, basename="account")
router.register('security', SecurityTokenView, basename="security_token")
urlpatterns = router.urls

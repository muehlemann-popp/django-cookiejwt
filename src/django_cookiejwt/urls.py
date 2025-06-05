from django.urls import path

from .views import CookieTokenBlacklistView, CookieTokenObtainPairView

app_name = "authentication"

urlpatterns = [
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/blacklist/", CookieTokenBlacklistView.as_view(), name="token_blacklist"),
]

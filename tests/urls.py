from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),  # For basic functionality of the admin panel
    # Connect plugin URLs for testing
    path("api/auth/", include("django_cookiejwt.urls")),  # The prefix should be that is planned in the real project
]

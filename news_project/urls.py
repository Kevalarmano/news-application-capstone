"""
Project URL configuration.

Includes:
- admin
- app URLs
- built-in auth URLs at /accounts/ (login/logout etc.)
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("news.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]

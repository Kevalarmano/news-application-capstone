"""
Admin registrations for quick management during marking/testing.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser."""
    fieldsets = UserAdmin.fieldsets + (
        ("Role & Subscriptions", {"fields": ("role", "subscribed_publishers", "subscribed_journalists")}),
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin configuration for Publisher."""
    list_display = ("name",)
    filter_horizontal = ("editors", "journalists")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for Article."""
    list_display = ("title", "journalist", "publisher", "approved", "created_at")
    list_filter = ("approved", "publisher")
    search_fields = ("title", "content")

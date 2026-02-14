"""
Signals to create default groups and basic permissions.

This ensures the project supports role-based access control expectations.
"""

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.apps import apps


@receiver(post_migrate)
def create_default_groups(sender, **kwargs) -> None:
    """
    Create default groups: Reader, Editor, Journalist.
    Adds model permissions in a simple way.
    """
    if sender.name != "news":
        return

    Group.objects.get_or_create(name="Reader")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")

    article_model = apps.get_model("news", "Article")
    perms = Permission.objects.filter(content_type__app_label="news", content_type__model=article_model._meta.model_name)

    # Editors get all article perms; journalists get add/change/view
    for p in perms:
        if p.codename.startswith(("add_", "change_", "delete_", "view_")):
            editor_group.permissions.add(p)

        if p.codename.startswith(("add_", "change_", "view_")):
            journalist_group.permissions.add(p)

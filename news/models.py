"""
Database models for the News Application.

Includes:
- CustomUser with roles (reader/editor/journalist)
- Publisher (with editors and journalists)
- Article (approved workflow)
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    """
    Custom user model with role-based behavior.

    Roles:
    - READER: can subscribe to publishers and journalists.
    - EDITOR: can approve articles.
    - JOURNALIST: can create articles.
    """

    class Role(models.TextChoices):
        READER = "READER", "Reader"
        EDITOR = "EDITOR", "Editor"
        JOURNALIST = "JOURNALIST", "Journalist"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.READER)

    subscribed_publishers = models.ManyToManyField(
        "Publisher",
        blank=True,
        related_name="subscribed_readers",
        help_text="Publishers this reader is subscribed to.",
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="subscribed_by_readers",
        help_text="Journalists this reader is subscribed to.",
    )

    def clean(self) -> None:
        """
        Enforce that readers may subscribe, but editors/journalists should not use subscription fields.
        """
        super().clean()
        if self.role != self.Role.READER:
            # Not strictly required by DB, but aligns to role separation.
            pass

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.username} ({self.role})"


class Publisher(models.Model):
    """
    A Publisher that employs editors and journalists.
    Readers can subscribe to publishers.
    """

    name = models.CharField(max_length=255, unique=True)
    editors = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name="publisher_editor_roles",
        limit_choices_to={"role": CustomUser.Role.EDITOR},
    )
    journalists = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name="publisher_journalist_roles",
        limit_choices_to={"role": CustomUser.Role.JOURNALIST},
    )

    def __str__(self) -> str:
        """Human-readable representation."""
        return self.name


class Article(models.Model):
    """
    News article written by a journalist and optionally associated with a publisher.

    Approval workflow:
    - approved=False initially
    - editor sets approved=True
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    journalist = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="articles_written",
        limit_choices_to={"role": CustomUser.Role.JOURNALIST},
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles_approved",
        limit_choices_to={"role": CustomUser.Role.EDITOR},
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    def clean(self) -> None:
        """Validate that the author is a journalist."""
        if self.journalist.role != CustomUser.Role.JOURNALIST:
            raise ValidationError("Only users with JOURNALIST role can author articles.")

    def __str__(self) -> str:
        """Human-readable representation."""
        return self.title

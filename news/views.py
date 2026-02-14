"""
Views for the News Application.

Includes:
- Public-ish article list (only approved)
- Editor review list (unapproved)
- Approve action (emails to subscribers)
- JSON API endpoint based on subscriptions
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.mail import send_mail

from .models import Article, CustomUser


def is_editor(user: CustomUser) -> bool:
    """Return True if the user has Editor role."""
    return getattr(user, "role", None) == CustomUser.Role.EDITOR


def article_list(request: HttpRequest) -> HttpResponse:
    """
    Display approved articles.
    """
    articles = Article.objects.filter(approved=True).order_by("-created_at")
    return render(request, "news/article_list.html", {"articles": articles})


@login_required
@user_passes_test(is_editor)
def editor_review_list(request: HttpRequest) -> HttpResponse:
    """
    Display unapproved articles for editors to review.
    """
    pending = Article.objects.filter(approved=False).order_by("-created_at")
    return render(request, "news/editor_review.html", {"articles": pending})


@login_required
@user_passes_test(is_editor)
def approve_article(request: HttpRequest, article_id: int) -> HttpResponse:
    """
    Approve an article and notify subscribed readers via email.

    Emails are sent using the console backend in dev.
    """
    article = get_object_or_404(Article, pk=article_id)

    article.approved = True
    article.approved_by = request.user  # type: ignore
    article.approved_at = timezone.now()
    article.save()

    # Notify subscribed readers:
    # - readers subscribed to article.publisher
    # - readers subscribed to article.journalist
    recipient_emails = set()

    if article.publisher:
        for reader in article.publisher.subscribed_readers.all():
            if reader.email:
                recipient_emails.add(reader.email)

    for reader in article.journalist.subscribed_by_readers.all():
        if reader.email:
            recipient_emails.add(reader.email)

    if recipient_emails:
        send_mail(
            subject=f"New approved article: {article.title}",
            message=f"{article.title}\n\n{article.content[:400]}...",
            from_email=None,
            recipient_list=list(recipient_emails),
            fail_silently=True,
        )

    return redirect("editor_review_list")


@login_required
def api_articles(request: HttpRequest) -> JsonResponse:
    """
    REST-style JSON endpoint returning approved articles based on a reader's subscriptions.

    Rules:
    - Only approved articles
    - Include if publisher is subscribed OR journalist is subscribed
    """
    user: CustomUser = request.user  # type: ignore

    if user.role != CustomUser.Role.READER:
        return JsonResponse({"detail": "Only READER accounts can use this endpoint."}, status=403)

    subscribed_publisher_ids = list(user.subscribed_publishers.values_list("id", flat=True))
    subscribed_journalist_ids = list(user.subscribed_journalists.values_list("id", flat=True))

    qs = Article.objects.filter(approved=True).order_by("-created_at")
    qs = qs.filter(
        (  # publisher match OR journalist match
            # Django Q import avoided by using filter chaining below
        )
    )

    # Use Q properly:
    from django.db.models import Q  # local import for clarity

    qs = Article.objects.filter(approved=True).filter(
        Q(publisher_id__in=subscribed_publisher_ids) | Q(journalist_id__in=subscribed_journalist_ids)
    ).order_by("-created_at")

    data = [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "created_at": a.created_at.isoformat(),
            "approved": a.approved,
            "publisher": a.publisher.name if a.publisher else None,
            "journalist": a.journalist.username,
        }
        for a in qs
    ]
    return JsonResponse({"results": data})

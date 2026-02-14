"""
News app URLs for HTML pages and the JSON API endpoint.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path("editor/review/", views.editor_review_list, name="editor_review_list"),
    path("editor/approve/<int:article_id>/", views.approve_article, name="approve_article"),
    path("api/articles/", views.api_articles, name="api_articles"),
]

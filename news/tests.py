"""
Automated tests for the subscription-based API.
"""

from django.test import TestCase
from django.urls import reverse
from .models import CustomUser, Publisher, Article


class ApiArticlesTests(TestCase):
    """Tests for /api/articles/ endpoint behavior based on subscriptions."""

    def setUp(self) -> None:
        """Create users, publishers, and articles for testing."""
        self.reader = CustomUser.objects.create_user(username="reader", password="pass1234", role=CustomUser.Role.READER)
        self.editor = CustomUser.objects.create_user(username="editor", password="pass1234", role=CustomUser.Role.EDITOR)
        self.j1 = CustomUser.objects.create_user(username="j1", password="pass1234", role=CustomUser.Role.JOURNALIST)
        self.j2 = CustomUser.objects.create_user(username="j2", password="pass1234", role=CustomUser.Role.JOURNALIST)

        self.pub_a = Publisher.objects.create(name="Publisher A")
        self.pub_b = Publisher.objects.create(name="Publisher B")

        # Reader subscriptions: pub_a and journalist j2
        self.reader.subscribed_publishers.add(self.pub_a)
        self.reader.subscribed_journalists.add(self.j2)

        # Articles
        Article.objects.create(title="A1 approved pubA j1", content="x", journalist=self.j1, publisher=self.pub_a, approved=True)
        Article.objects.create(title="A2 approved pubB j1", content="x", journalist=self.j1, publisher=self.pub_b, approved=True)
        Article.objects.create(title="A3 approved noPub j2", content="x", journalist=self.j2, publisher=None, approved=True)
        Article.objects.create(title="A4 NOT approved pubA j1", content="x", journalist=self.j1, publisher=self.pub_a, approved=False)

    def test_reader_gets_only_subscribed_and_approved(self) -> None:
        """Reader should receive approved articles from subscribed publisher or subscribed journalist."""
        self.client.login(username="reader", password="pass1234")
        url = reverse("api_articles")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        titles = [a["title"] for a in res.json()["results"]]
        self.assertIn("A1 approved pubA j1", titles)      # pubA subscribed
        self.assertIn("A3 approved noPub j2", titles)     # j2 subscribed

        self.assertNotIn("A2 approved pubB j1", titles)   # pubB not subscribed
        self.assertNotIn("A4 NOT approved pubA j1", titles)  # not approved

    def test_non_reader_forbidden(self) -> None:
        """Editors/journalists should be blocked from using the reader subscription endpoint."""
        self.client.login(username="editor", password="pass1234")
        url = reverse("api_articles")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)

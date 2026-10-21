"""Regression checks for importing unpublished editorial material."""

import unittest
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from unittest.mock import patch

import seed


class DraftImportTests(unittest.TestCase):
    def article(self, slug, **extra):
        return dict(slug=slug, title=slug, description="Description", content="<p>Text</p>", tags=[], **extra)

    def test_draft_payload_has_no_publication_date(self):
        payload = seed.build_payload(self.article("draft", published=False), {}, {}, datetime.now(seed.NOVOSIBIRSK))
        self.assertFalse(payload["published"])
        self.assertIsNone(payload["published_at"])

    def test_existing_files_keep_default_publication_behavior(self):
        payload = seed.build_payload(self.article("legacy"), {}, {}, datetime.now(seed.NOVOSIBIRSK))
        self.assertTrue(payload["published"])
        self.assertIsNotNone(payload["published_at"])

    def run_import(self, articles, existing=None, update=False):
        argv = ["seed.py", "--api", "https://example.test", "--token", "test"]
        if update:
            argv.append("--update")
        with patch("sys.argv", argv), \
             patch.object(seed, "load_json", side_effect=lambda path: [] if path == seed.PLAN_FILE else {}), \
             patch.object(seed, "load_articles", return_value=articles), \
             patch.object(seed, "ensure_tags", return_value={}), \
             patch.object(seed, "AdminApi") as api_class, \
             patch.object(seed, "notify_indexnow") as notify:
            api_class.return_value.get.return_value = existing or []
            with redirect_stdout(StringIO()):
                seed.main()
            return api_class.return_value.post.call_args_list, notify.call_args_list

    def test_mixed_import_only_announces_public_articles(self):
        calls, notifications = self.run_import([
            self.article("draft", published=False), self.article("public"),
        ])
        self.assertEqual(len(calls), 2)
        self.assertIsNone(calls[0].args[1]["published_at"])
        self.assertIsNotNone(calls[1].args[1]["published_at"])
        self.assertEqual(notifications[0].args[0], ["public"])

    def test_draft_only_import_never_announces_urls(self):
        calls, notifications = self.run_import([self.article("draft", published=False)])
        self.assertEqual(len(calls), 1)
        self.assertEqual(notifications, [])

    def test_publishing_existing_draft_announces_its_url(self):
        calls, notifications = self.run_import(
            [self.article("ready", published=True)],
            existing=[dict(slug="ready", id=7, published_at=None)], update=True,
        )
        self.assertEqual(calls, [])
        self.assertEqual(notifications[0].args[0], ["ready"])

    def test_updating_public_article_does_not_announce_it_as_new(self):
        calls, notifications = self.run_import(
            [self.article("old")],
            existing=[dict(slug="old", id=8, published_at="2026-01-01T09:00:00+07:00")], update=True,
        )
        self.assertEqual(notifications, [])


class SourceLinkTests(unittest.TestCase):
    def test_verified_technical_sources_survive_import(self):
        sources = [
            "https://www.mos.ru/upload/documents/files/order.pdf",
            "https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/",
            "https://api.faufcc.ru/api/assets/document",
        ]
        for url in sources:
            link = f'<a href="{url}">Источник</a>'
            with self.subTest(url=url):
                self.assertEqual(seed.clean_links(link), link)


class CoverCreditTests(unittest.TestCase):
    def test_credit_preserves_source_license_and_changes(self):
        credit = seed.credit_paragraph(dict(
            author="Photographer", source="https://example.test/photo",
            license="CC BY 4.0", license_url="https://creativecommons.org/licenses/by/4.0/",
            modifications="Cropped and resized",
        ))
        self.assertIn('href="https://example.test/photo"', credit)
        self.assertIn('href="https://creativecommons.org/licenses/by/4.0/"', credit)
        self.assertIn("Cropped and resized", credit)

    def test_credit_escapes_metadata_and_rejects_non_web_urls(self):
        credit = seed.credit_paragraph(dict(
            author="<script>bad</script>", source="javascript:bad()",
            license="CC0", license_url="javascript:bad()",
        ))
        self.assertNotIn("<script>", credit)
        self.assertNotIn("javascript:", credit)
        self.assertIn("&lt;script&gt;", credit)


if __name__ == "__main__":
    unittest.main()

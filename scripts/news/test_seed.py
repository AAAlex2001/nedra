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

    def run_import(self, articles):
        with patch("sys.argv", ["seed.py", "--api", "https://example.test", "--token", "test"]), \
             patch.object(seed, "load_json", side_effect=lambda path: [] if path == seed.PLAN_FILE else {}), \
             patch.object(seed, "load_articles", return_value=articles), \
             patch.object(seed, "ensure_tags", return_value={}), \
             patch.object(seed, "AdminApi") as api_class, \
             patch.object(seed, "notify_indexnow") as notify:
            api_class.return_value.get.return_value = []
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


if __name__ == "__main__":
    unittest.main()

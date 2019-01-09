from newsration import app
import unittest
from unittest import mock


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @mock.patch("newsration.views.home.feed_service")
    def test_settings_index_get(self, mock_feed_service):
        response = self.client.get("/settings/")

        self.assertEqual(response.status_code, 200)

    @mock.patch("newsration.views.home.feed_service")
    def test_settings_index_post_status_code_200(self, mock_feed_service):
        response = self.client.post("/settings/")

        self.assertEqual(response.status_code, 200)

    @mock.patch("newsration.views.home.feed_service")
    def test_settings_index_post_sets_cookie(self, mock_feed_service):
        response = self.client.post("/settings/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("sources", response.headers["Set-Cookie"])

    @mock.patch("newsration.views.home.feed_service")
    def test_settings_delete_cookie_expires_cookie(self, mock_feed_service):
        response = self.client.post("/settings/deletecookie")

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "sources=; Expires=Thu, 01-Jan-1970 00:00:00 GMT; Path=/",
            response.headers["Set-Cookie"],
        )

from newsration import app
import unittest
from unittest import mock


class TestHome(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @mock.patch("newsration.views.home.feed_service")
    def test_index(self, mock_feed_service):
        result = self.client.get("/")

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"NewsRation", result.data)

    @mock.patch("newsration.views.home.feed_service")
    def test_source_feed_with_source(self, mock_feed_service):
        result = self.client.get("/source")

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"NewsRation", result.data)

    @mock.patch("newsration.views.home.feed_service")
    def test_source_feed_with_source_and_topic(self, mock_feed_service):
        result = self.client.get("/source/topic")

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"NewsRation", result.data)

    @mock.patch("newsration.views.home.feed_service")
    def test_source_feed_when_source_invalid_return_404(self, mock_feed_service):
        mock_feed_service.validate = mock.Mock(return_value=False)
        result = self.client.get("/source/topic")

        self.assertEqual(result.status_code, 404)
        self.assertIn(b"NewsRation", result.data)

    def test_robotstxt(self):
        result = self.client.get("/robots.txt")

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"User-agent: *", result.data)
        self.assertIn(b"Disallow: /", result.data)

    def test_gzip_compression_applied(self):
        headers = [("Accept-Encoding", "gzip")]

        response = self.client.options("/", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_encoding, "gzip")


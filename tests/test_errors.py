from newsration import app
import unittest
from unittest import mock
from newsration import feed_service


class TestErrors(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_pagenotfound(self):
        result = self.client.get("/missing-page")

        self.assertEqual(result.status_code, 404)
        self.assertIn(b"Page Not Found", result.data)

    def test_unhandledexception(self):
        result = self.client.put("/settings/")

        self.assertEqual(result.status_code, 500)
        self.assertIn(b"Something Went Wrong", result.data)

    def test_internalservererror(self):
        mock_function = mock.Mock()
        mock_function.side_effect = Exception

        with mock.patch(
            "newsration.views.home.feed_service.get_top_feeds", mock_function
        ):
            result = self.client.get("/")

        self.assertEqual(result.status_code, 500)
        self.assertIn(b"Something Went Wrong", result.data)


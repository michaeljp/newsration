from newsration import app
from typing import List
import unittest
from unittest import mock
from multiprocessing.pool import ThreadPool
from newsration import feed_service
from datetime import datetime, timedelta, timezone


class MockCurrentApp:
    pool = ThreadPool(4)


class MockFeed:
    title = "TestTitle"
    items: List = []
    pub_date = datetime.now(timezone.utc)
    link = "TestLink"
    description = "TestDescription"


cookies_test_feeds = {
    "test_source": {"title": "test_title"},
    "test_source2": {"title": "test_title2"},
}


class TestFeedService(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @mock.patch("newsration.feed_service.get_feed_from_url", return_value=MockFeed())
    def test_get_top_feeds_returns_3_feeds(self, mock_get_feed_from_url):
        top_feeds = feed_service.get_top_feeds(active_app=MockCurrentApp())

        self.assertEqual(3, len(top_feeds))

    @mock.patch("newsration.feed_service.get_feed_from_url", return_value=MockFeed())
    def test_get_feed_uses_default_topic(self, mock_get_feed_from_url):
        feed = feed_service.get_feed("bbc")

        feed_service.get_feed_from_url.assert_called_with(
            "http://feeds.bbci.co.uk/news/rss.xml"
        )
        self.assertEqual(MockFeed().title, feed.title)

    @mock.patch("newsration.feed_service.get_feed_from_url", return_value=MockFeed())
    def test_get_feed_with_topic(self, mock_get_feed_from_url):
        feed = feed_service.get_feed("bbc", "top")

        self.assertEqual(MockFeed().title, feed.title)

    def test_humanize_time_day(self):
        test_time = datetime.now(timezone.utc) - timedelta(days=1)
        value = feed_service.humanise_time(test_time)

        self.assertEqual("1d", value)

    def test_humanize_time_hour(self):
        test_time = datetime.now(timezone.utc) - timedelta(hours=1)
        value = feed_service.humanise_time(test_time)

        self.assertEqual("1h", value)

    def test_humanize_time_minute(self):
        test_time = datetime.now(timezone.utc) - timedelta(minutes=1)
        value = feed_service.humanise_time(test_time)

        self.assertEqual("1m", value)

    def test_humanize_time_second(self):
        test_time = datetime.now(timezone.utc) - timedelta(seconds=1)
        value = feed_service.humanise_time(test_time)

        self.assertIn("s", value)

    def test_humanize_return_empty_str_when_exception(self):
        value = feed_service.humanise_time("foo")

        self.assertEqual("", value)

    def test_strip_tags(self):
        results = [
            feed_service.strip_tags("<b>Test</b>"),
            feed_service.strip_tags("<b><a>Test</a></b>"),
        ]

        self.assertTrue(all(x == "Test" for x in results))

    def test_parse_entry(self):
        test_date = datetime.now(timezone.utc)
        result = feed_service.parse_entry(MockFeed())

        self.assertEqual(MockFeed().title, result.title)

    def test_parse_description_if_none_return_emtpy_str(self):
        result = feed_service.parse_description(None)

        self.assertEqual("", result)

    def test_parse_description_split_on_paragraphs(self):
        result = feed_service.parse_description("<p>Test</p>")

        self.assertEqual("Test", result)

    def test_parse_description_split_on_long_text(self):
        result = feed_service.parse_description("Test." + "a" * 250)

        self.assertEqual("Test", result)

    def test_parse_description_empty_str_when_exception(self):
        result = feed_service.parse_description(100)

        self.assertEqual("", result)

    @mock.patch("newsration.feed_service.urllib.request")
    @mock.patch("newsration.feed_service.atoma")
    def test_get_feed_from_url(self, mock_atoma, mock_request):
        feed_service.get_feed_from_url("test")
        mock_request.urlopen.assert_called()
        mock_atoma.parse_rss_bytes.assert_called()

    def test_validate(self):
        test_feeds = {"test_source": {"topics": {"test_topic"}}}

        self.assertFalse(feed_service.validate("foo", None, feeds=test_feeds))
        self.assertFalse(feed_service.validate(None, None, feeds=test_feeds))
        self.assertFalse(feed_service.validate("test_source", "foo", feeds=test_feeds))
        self.assertTrue(feed_service.validate("test_source", None, feeds=test_feeds))
        self.assertTrue(
            feed_service.validate("test_source", "test_topic", feeds=test_feeds)
        )

    def test_get_topics(self):
        test_feeds = {
            "test_source": {"topics": {"test_topic": {"title": "test_title"}}}
        }

        results = feed_service.get_topics("test_source", feeds=test_feeds)

        self.assertTrue(1, len(results))
        self.assertEqual("test_topic", results[0].url)
        self.assertEqual("test_title", results[0].title)

    def test_get_sources_no_cookies(self):
        results = feed_service.get_sources(feeds=cookies_test_feeds)

        self.assertEqual(2, len(results))
        self.assertEqual("test_title", results[0]["title"])
        self.assertEqual("test_source", results[0]["url"])

    def test_get_sources_cookies_str(self):
        results = feed_service.get_sources(
            cookie_sources="test_source", feeds=cookies_test_feeds
        )

        self.assertEqual(1, len(results))
        self.assertEqual("test_title", results[0]["title"])
        self.assertEqual("test_source", results[0]["url"])

    def test_get_sources_cookies_list(self):
        results = feed_service.get_sources(
            cookie_sources=["test_source"], feeds=cookies_test_feeds
        )

        self.assertEqual(1, len(results))
        self.assertEqual("test_title", results[0]["title"])
        self.assertEqual("test_source", results[0]["url"])

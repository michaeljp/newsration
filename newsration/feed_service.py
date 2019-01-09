import re
import datetime
from typing import Any, List, Optional, Dict

import atoma
import urllib.request
from flask import current_app

from newsration import app, cache
from newsration.feeds_source import FEEDS
from newsration.models import Feed, Entry, Topic


def get_top_feeds(active_app=current_app) -> List[Feed]:
    sources = [source["url"] for source in get_sources()]
    results = active_app.pool.map(get_feed, sources[:4])
    return results


def get_feed(
    source: str, topic: Optional[str] = None, max_articles: Optional[int] = 5
) -> Optional[Feed]:
    if not topic:
        topic = str(FEEDS[source]["default_topic"])
    url = FEEDS[source]["topics"][topic]["url"]
    rss_feed = get_feed_from_url(url)
    return parse_feed(rss_feed, max_articles)


def get_sources(cookie_sources=None, feeds=FEEDS) -> List[Dict[str, Any]]:
    sources = [{"title": feeds[key]["title"], "url": key} for key in feeds]

    if cookie_sources:
        if type(cookie_sources) is list:
            cookie_sources = ",".join(cookie_sources)
        sources = [s for s in sources if s["url"] in cookie_sources.split(",")]

    return sources


def get_topics(source: str, feeds=FEEDS) -> List[Topic]:
    return [
        Topic(title=feeds[source]["topics"][key]["title"], url=key)
        for key in feeds[source]["topics"]
    ]


def validate(source: str, topic: Optional[str], feeds=FEEDS) -> bool:
    if source not in feeds:
        return False
    if topic is not None and topic not in feeds[source]["topics"]:
        return False
    return True


@cache.memoize(timeout=300)
def get_feed_from_url(url: str) -> atoma.rss.RSSChannel:
    feed_text = urllib.request.urlopen(url).read()
    return atoma.parse_rss_bytes(feed_text)


def parse_feed(rss_feed: atoma.rss.RSSChannel, max_articles: Optional[int]) -> Feed:
    return Feed(
        title=rss_feed.title,
        entries=[parse_entry(x) for x in rss_feed.items[:max_articles]],
    )


def parse_entry(entry: atoma.rss.RSSItem) -> Entry:
    return Entry(
        title=entry.title,
        url=entry.link,
        summary=parse_description(entry.description),
        published=humanise_time(entry.pub_date),
    )


def strip_tags(value: str) -> str:
    while "<" in value and ">" in value:
        value = re.sub("<[^>]+>|&nbsp;", " ", value)

    return value.strip()


def humanise_time(date: datetime.datetime) -> str:
    try:
        delta = datetime.datetime.now(datetime.timezone.utc) - date
        if delta.days >= 1:
            value = "{0}d".format(delta.days)
        elif delta.seconds < 60:
            value = "{0}s".format(delta.seconds)
        elif delta.seconds < (60 * 60):
            value = "{0}m".format(delta.seconds // 60)
        else:
            value = "{0}h".format(delta.seconds // (60 * 60))

        return value

    except Exception as e:
        with app.app_context():
            current_app.logger.error("Error humanising time:{0}".format(date), e)
        return ""


def parse_description(description) -> str:
    if not description:
        return ""
    try:
        parsed_summary = strip_tags(description.split("<p>", 1)[0])
        if not parsed_summary:
            parsed_summary = strip_tags(description.split("</p>", 1)[0])
        if len(parsed_summary) > 250:
            parsed_summary = parsed_summary.split(".", 1)[0]

        return parsed_summary
    except Exception as e:
        with app.app_context():
            current_app.logger.error(
                "Error parsing entry summary: {0}".format(description), e
            )
        return ""

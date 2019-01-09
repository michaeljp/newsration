from typing import List


class Feed:
    def __init__(self, title: str, entries: List) -> None:
        self.title = title
        self.entries = entries


class Entry:
    def __init__(self, title: str, url: str, summary: str, published: str) -> None:
        self.title = title
        self.url = url
        self.summary = summary
        self.published = published


class Topic:
    def __init__(self, title: str, url: str) -> None:
        self.title = title
        self.url = url

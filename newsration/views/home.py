from flask import Blueprint, abort, request, render_template, send_from_directory

from newsration import app, feed_service


mod: Blueprint = Blueprint("home", __name__)


@mod.route("/robots.txt")
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@mod.route("/")
def index():
    feeds = feed_service.get_top_feeds()
    cookie_sources = request.cookies.get("sources")
    sources = feed_service.get_sources(cookie_sources)
    topics = []

    return render_template(
        "home/home.html",
        sources=sources,
        topics=topics,
        feeds=feeds,
        request_source=None,
        request_topic=None,
    )


@mod.route("/<source>")
@mod.route("/<source>/<topic>")
def source_feed(source, topic=None):
    if not feed_service.validate(source, topic):
        abort(404)
    feed = feed_service.get_feed(source, topic, None)
    cookie_sources = request.cookies.get("sources")
    sources = feed_service.get_sources(cookie_sources)
    topics = feed_service.get_topics(source)

    return render_template(
        "home/articles.html",
        sources=sources,
        topics=topics,
        feed=feed,
        request_source=source,
        request_topic=topic,
    )

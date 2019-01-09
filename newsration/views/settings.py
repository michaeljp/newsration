import datetime

from flask import Blueprint, render_template, request, make_response, redirect, url_for

from newsration import feed_service

mod = Blueprint("settings", __name__, url_prefix="/settings")


@mod.route("/", methods=["POST", "GET"])
def settings_index():
    cookie_sources = request.cookies.get("sources")
    if request.method == "POST":
        cookie_sources = request.form.getlist("source")

    sources = feed_service.get_sources(cookie_sources)
    all_sources = feed_service.get_sources()
    resp = make_response(
        render_template(
            "settings/settings.html",
            cookie_sources=cookie_sources,
            sources=sources,
            all_sources=all_sources,
            existing_cookie=cookie_sources is not None,
        )
    )

    if request.method == "POST" and sources is not None:
        resp.set_cookie(
            "sources",
            value=",".join(cookie_sources),
            expires=datetime.datetime.now() + datetime.timedelta(days=90),
        )

    return resp


@mod.route("/deletecookie", methods=["POST"])
def delete_cookie():
    response = make_response(redirect(url_for("settings.settings_index")))
    response.set_cookie("sources", value="", expires=0)
    return response

import logging.handlers
from multiprocessing.pool import ThreadPool
import gzip

from flask import Flask, request, render_template
from flask_caching import Cache
import werkzeug

app = Flask(__name__, instance_relative_config=True, template_folder="templates")

# Configure app
app.config.from_object("config")
app.config.from_pyfile("config.py", silent=True)

# Strip blank spaces from templates
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Configure logging
handler = logging.handlers.RotatingFileHandler(
    app.config["LOGGING_LOCATION"], maxBytes=1024 * 1024, backupCount=3
)
handler.setLevel(app.config["LOGGING_LEVEL"])
formatter = logging.Formatter(app.config["LOGGING_FORMAT"])
handler.setFormatter(formatter)
app.logger.setLevel(app.config["LOGGING_LEVEL"])
app.logger.addHandler(handler)
app.logger.info("Started app")

# Configure caching
cache = Cache(app, config={"CACHE_TYPE": "simple"})
cache.init_app(app)

# Register blueprints
from newsration.views import home
from newsration.views import settings

app.register_blueprint(home.mod)
app.register_blueprint(settings.mod)


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error("Page not found: %s", (request.path, error))
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error("Server Error: %s", error)
    return render_template("errors/500.html"), 500


@app.errorhandler(werkzeug.exceptions.HTTPException)
def unhandled_exception(ex):
    app.logger.error("Unhandled Exception: %s", ex)
    return render_template("errors/500.html"), 500


@app.before_first_request
def initialize():
    app.pool = ThreadPool(4)


@app.after_request
def after(response):
    if response.status_code < 200 or response.status_code >= 300:
        app.logger.error("response status: " + response.status)
    else:
        response.headers["Vary"] = "Accept-Encoding"
        return gzip_response(response)

    return response


def gzip_response(response):
    mimetypes = [
        "text/html",
        "text/css",
        "text/xml",
        "application/json",
        "application/javascript",
    ]
    if (
        response.mimetype not in mimetypes
        or "gzip" not in request.headers.get("Accept-Encoding", "").lower()
        or "Content-Encoding" in response.headers
        or response.direct_passthrough
    ):
        return response

    response.data = gzip.compress(response.get_data(), compresslevel=6)
    response.headers["Content-Encoding"] = "gzip"
    response.headers["Content-Length"] = len(response.data)

    return response

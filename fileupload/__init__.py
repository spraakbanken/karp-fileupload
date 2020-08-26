"""Initialise Flask application."""

import logging
import os
import sys
import time

import flask_reverse_proxy
from flask import Flask

log = logging.getLogger("fileupload" + __name__)


def create_app():
    """Instanciate app."""
    app = Flask(__name__)

    # Read config
    if os.path.exists(app.config.root_path + "/../config.py") is False:
        print("copy config_default.py to config.py and add your settings")
        app.config.from_pyfile(app.config.root_path + "/../config_default.py")
    else:
        app.config.from_pyfile(app.config.root_path + "/../config.py")

    app.secret_key = app.config["SECRET_KEY"]

    # Configure logger
    logfmt = "%(asctime)-15s - %(levelname)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    if app.config.get("DEBUG"):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                            format=logfmt, datefmt=datefmt)
    else:
        today = time.strftime("%Y-%m-%d")
        logdir = app.config.get("LOG_DIR")
        logfile = os.path.join(logdir, f"{today}.log")
        # Create log dir if it does not exist
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        logging.basicConfig(filename=logfile, level=logging.INFO,
                            format=logfmt, datefmt=datefmt)

    log.info("Application restarted")

    # Fix proxy chaos
    app.wsgi_app = flask_reverse_proxy.ReverseProxied(app.wsgi_app)
    app.wsgi_app = FixScriptName(app.wsgi_app, app.config)

    from . import views
    app.register_blueprint(views.general)

    return app


class FixScriptName(object):
    """Set the environment SCRIPT_NAME."""
    def __init__(self, app, config):
        self.app = app
        self.config = config

    def __call__(self, environ, start_response):
        script_name = self.config["APPLICATION_ROOT"]
        if script_name:
            environ["SCRIPT_NAME"] = script_name

        # log.debug("CONFIG:")
        # log.debug(self.config)
        # log.debug("ENVIRON:")
        # log.debug(environ)
        return self.app(environ, start_response)

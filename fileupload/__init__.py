"""Initialise Flask application."""

import logging
import os
import sys
import time

from flask import Flask
from flask_cors import CORS


def create_app():
    """Instanciate app."""
    app = Flask(__name__)

    # Read config
    if os.path.exists(app.config.root_path + '/../config.py') is False:
        print("copy config_default.py to config.py and add your settings")
        app.config.from_pyfile(app.config.root_path + '/../config_default.py')
    else:
        app.config.from_pyfile(app.config.root_path + '/../config.py')

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

    from . import views
    app.register_blueprint(views.general)

    return app

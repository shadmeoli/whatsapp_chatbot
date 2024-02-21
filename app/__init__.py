from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint


def create_app():
    app = Flask(__name__)
    load_configurations(app)
    configure_logging()

    app.register_blueprint(webhook_blueprint)

    return app 

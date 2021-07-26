from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman

from .config import config_by_name
from flask.app import Flask

db = SQLAlchemy()
flask_bcrypt = Bcrypt()

# Swagger CSP needs to have 'unsafe-inline' in the script-src and style-src fields
SWAGGER_CSP = {
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"]
    }


def create_app(config_name: str) -> Flask:
    app = Flask(__name__)
    Talisman(app, content_security_policy=SWAGGER_CSP)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    flask_bcrypt.init_app(app)

    return app

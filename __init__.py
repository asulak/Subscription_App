"""
__init__.py File Purpose:
1) Defines create_app() function that creates, configures, and returns a Flask app instance.
2) Initializes extensions
3) Registers blueprints, making it easy to add or remove different parts of the app

Emphasis: does not execute the app! Just defines how to create and configure it
"""

# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Initialize extensions without binding to an app instance yet
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class='config.Config'):
    """Application factory function to create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)  # Load configuration settings

    # Initialize extensions with the app instance
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Import and register blueprints
    from auth.routes import auth
    from billing.billing import billing
    app.register_blueprint(auth)
    app.register_blueprint(billing)

    return app

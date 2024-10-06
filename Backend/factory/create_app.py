from flask import Flask
from Backend.api.routes import register_routes
from Backend.factory.create_applications import create_application
from Backend.factory.create_services import create_services
from flask_cors import CORS  # Import CORS


def create_app():
    """Application Factory: Create the Flask app and inject dependencies."""

    app = Flask(__name__)
    CORS(app)
    services = create_services()

    applications = create_application(services)

    register_routes(app, applications)

    return app

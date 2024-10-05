from flask import Flask
from api.handlers.get_demo_ppt import generate_ppt_handler
from factory.create_applications import create_application
from factory.create_services import create_services


def create_app():
    """Application Factory: Create the Flask app and inject dependencies."""

    app = Flask(__name__)

    services = create_services()

    issue_tracker_app = create_application(services)

    app.add_url_rule(
        '/api/ppt',
        'generate_ppt',
        lambda: generate_ppt_handler(issue_tracker_app),
        methods=['GET']
    )

    return app

from flask import Blueprint
from api.handlers.get_demo_ppt import generate_demo_ppt

api = Blueprint('api', __name__)


def register_routes(api, application):
    """Register routes and inject services into handlers."""
    api.add_url_rule(
        '/api/ppt',
        'generate_ppt',
        lambda: generate_demo_ppt(application['ppt_application']),
        methods=['GET']
    )

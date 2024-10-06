from flask import Blueprint
from backend.api.handlers.get_demo_ppt import generate_ppt_handler
from backend.api.handlers.list_all_sprints_of_board import list_sprints_for_board_handler
from backend.api.handlers.list_boards import list_all_boards_handler

api = Blueprint('api', __name__)


def register_routes(api, application):
    """Register routes and inject services into handlers."""

    api.add_url_rule(
        '/api/ppt/<int:sprint_id>',
        'generate_ppt',
        lambda sprint_id: generate_ppt_handler(application['issue_tracker_application'], sprint_id),
        methods=['GET']
    )

    api.add_url_rule(
        '/api/boards',
        'list_all_boards',
        lambda: list_all_boards_handler(application['issue_tracker_application']),
        methods=['GET']
    )

    # List sprints for a specific board
    api.add_url_rule(
        '/api/boards/<int:board_id>/sprints',
        'list_sprints_for_board',
        lambda board_id: list_sprints_for_board_handler(application['issue_tracker_application'], board_id),
        methods=['GET']
    )

    api.add_url_rule(
        '/health/liveness',
        'liveness',
        lambda: ({"status": "OK"}, 200),
        methods=['GET']
    )

    api.add_url_rule(
        '/health/readiness',
        'readiness',
        lambda: ({"status": "OK"}, 200),
        methods=['GET']
    )

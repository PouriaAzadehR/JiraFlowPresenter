from flask import jsonify


def list_all_boards_handler(issue_tracker_app):
    """Handler to list all boards."""
    try:
        boards = issue_tracker_app.get_all_boards()
        return jsonify(boards), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

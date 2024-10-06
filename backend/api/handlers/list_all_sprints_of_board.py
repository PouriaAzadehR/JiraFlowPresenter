from flask import jsonify


def list_sprints_for_board_handler(issue_tracker_application, board_id):
    # Fetch the sprints for the given board
    sprints = issue_tracker_application.get_sprints_for_board(board_id)
    return jsonify(sprints)

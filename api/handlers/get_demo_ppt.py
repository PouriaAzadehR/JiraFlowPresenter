from flask import request, jsonify, send_file
from applications.issue_tracker_app import IssueTrackerApp
import os


def generate_ppt_handler(issue_tracker_app: IssueTrackerApp):
    """Handler to generate a PowerPoint for the active sprint issues from an issue tracker."""
    board_id = request.args.get("board_id")
    exception_statuses = request.args.getlist("exception_statuses")

    try:
        # Generate the PowerPoint file via the applications layer
        ppt_file = issue_tracker_app.generate_active_sprint_ppt(board_id, exception_statuses)

        # Path to the generated file
        file_path = os.path.join('templates', ppt_file)

        # Send the generated file as a download
        return send_file(file_path, as_attachment=True, download_name=ppt_file)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

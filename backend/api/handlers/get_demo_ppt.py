from flask import request, jsonify, send_file
from Backend.applications.issue_tracker_app import IssueTrackerApp
import os


def generate_ppt_handler(issue_tracker_app: IssueTrackerApp, sprint_id: int):
    """Handler to generate a PowerPoint for the selected sprint issues from an issue tracker."""

    try:
        # Generate the PowerPoint file via the applications layer using sprint_id
        ppt_file = issue_tracker_app.generate_sprint_ppt(sprint_id)

        current_directory = os.path.dirname(os.path.abspath(__file__))
        ppt_directory = os.path.join(current_directory,"../../", 'ppt_files')
        print(ppt_directory)

        file_path = os.path.join(ppt_directory, ppt_file)

        # Send the generated file as a download
        return send_file(file_path, as_attachment=True, download_name=ppt_file)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

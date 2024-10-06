import os

from pptx import Presentation
from Backend.utils.ppt_helpers.ppt_helpers import create_squad_slide, create_summary_slide, create_assignee_slide


class PptService:
    def __init__(self):
        pass

    def create_ppt(self, issues_details):
        """Create PowerPoint from the issues details."""
        prs = Presentation()

        create_squad_slide(prs, title="InStore Squad")
        last_assignee = None

        for details in issues_details:
            if details['assignee'] != last_assignee:
                create_assignee_slide(prs, assignee_name=details['assignee'])
                last_assignee = details['assignee']

            create_summary_slide(
                prs,
                title=details['title'],
                assignee=details['assignee'],
                deadline=details['deadline'],
                krs=details['krs'],
                stakeholder=details['stakeholder'],
                accomplishments=details['accomplishments'],
                challenges=details['challenges'],
                status=details['status'],
                start=details['start'],
                estimate=details['estimate'],
                scope_changed=details['scope_changed'],
                progress_statuses_dates=details['progress_statuses_dates'],
            )

            # Determine the absolute path to the ppt_files directory
        current_directory = os.path.dirname(os.path.abspath(__file__))
        ppt_directory = os.path.join(current_directory, 'ppt_files')


        file_name = "active_sprint_summary.pptx"
        file_path = os.path.join(ppt_directory, file_name)

        # Save the PowerPoint to the file_path
        prs.save(file_path)

        return file_name

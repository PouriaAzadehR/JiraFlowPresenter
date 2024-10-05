from pptx import Presentation
from utils.ppt_helpers.ppt_helpers import create_squad_slide, create_summary_slide, create_assignee_slide


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
                gann_chart_path=details['gantt_chart_image_path']
            )

        file_name = "active_sprint_summary.pptx"
        prs.save(f"templates/{file_name}")
        return file_name

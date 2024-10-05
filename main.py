import glob

from dotenv import load_dotenv
from jira import JIRA
from jira.exceptions import JIRAError
from pptx import Presentation
from enum import Enum

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
import os

import slideCreator

PARTICIPANT_EMAIL_MAP = {
    "Ali Farhoudi": "a.farhoudi@snappgrocery.com",
    "Ali Mokhtari": "a.mokhtari@snappgrocery.com",
    "Amir Mohsen Jalili": "am.jalili@snappgrocery.com",
    "Azar Yadegari": "a.yadegari@snappgrocery.com",
    "Erfan Pouya Fard": "e.pouyafard@snappgrocery.com",
    "Farnaz Tashakor": "f.tashakor@snappgrocery.com",
    "Farnoosh Rad": "f.rad@snappgrocery.com",
    "Mahnaz Shabihi": "m.shabihi@snappgrocery.com",
    "Masoud MohammadHashem": "m.mohammadhashem@snappgrocery.com",
    "Mohammad Yaldayi": "m.yaldayi@snappgrocery.com",
    "Pouria Azadeh": "p.azadeh@snappgrocery.com",
}


# Define an Enum for Board Statuses
class BoardStatus(Enum):
    IN_PROGRESS = "InProgress"
    READY_FOR_TEST = "Ready for Test (Stage)"
    QA = "QA"
    DONE = "Done"
    BLOCKED = "Blocked"

    @classmethod
    def map_status(cls, status_name):
        if status_name == cls.READY_FOR_TEST.value:
            return cls.QA.value
        return status_name


def initialize_jira_connection(jira_url, username, password):
    """
    Initializes a connection to JIRA.

    :param jira_url: The base URL of the JIRA instance.
    :param username: The JIRA username.
    :param password: The JIRA password.
    :return: An authenticated JIRA instance.
    """
    return JIRA(server=jira_url, auth=(username, password))


def fetch_issues_from_sprint(jira_instance, sprint_id, exception_statuses):
    """
    Fetches issues from a specified sprint in JIRA and prints their sprint, ID, and summary.

    :param jira_instance: An authenticated JIRA instance.
    :param sprint_id: The ID of the sprint.
    :param exception_statuses: A list of statuses to exclude from the results.
    :return: A list of issues in the sprint that are not in the exception statuses.
    """
    try:
        # Create a string from the exception statuses to exclude them in the JQL query
        exception_statuses_jql = ','.join([f'"{status}"' for status in exception_statuses])
        # Modify the JQL query to search using the custom field for sprints and exclude exception statuses
        jql = f"'Sprint' = {sprint_id} AND status NOT IN ({exception_statuses_jql})"
        issues = jira_instance.search_issues(jql, expand='changelog', maxResults=1000)

        for issue in issues:
            # Get the sprint field, ID, and summary (name) of the issue
            issue_sprints = getattr(issue.fields, 'customfield_10106', None)  # Sprint field ID is customfield_10106
            issue_id = issue.key
            issue_name = issue.fields.summary

            # print(f"Issue Key: {issue_id}, Summary: {issue_name}")

            # Parse the sprint details if they exist
            if issue_sprints:
                sprint_names = []
                sprint_in_target = False

                for sprint in issue_sprints:
                    # Extract sprint name using regex (assuming name is within `name=...`)
                    match = re.search(r'name=([^,]+)', sprint)
                    if match:
                        sprint_name = match.group(1)
                        sprint_names.append(sprint_name)
                        if f'={sprint_id}' in sprint:
                            sprint_in_target = True

            #     # Print the issue only if it's in the specified sprint and has been in previous sprints
            #     if sprint_in_target and len(sprint_names) > 1:
            #         print(f"Issue ID: {issue_id}, Name: {issue_name}, Sprints: {', '.join(sprint_names)}")
            #     else:
            #         print(f"Issue ID: {issue_id}, Name: {issue_name}, Sprints: None")
            # else:
            #     print(f"Issue ID: {issue_id}, Name: {issue_name}, Sprints: None")

        return issues
    except JIRAError as e:
        print(f"Failed to fetch issues from JIRA: {e}")
        return []


def extract_issue_details(jira_instance, issue):
    """
    Extracts necessary details from a JIRA issue.

    :param issue: A JIRA issue object.
    :return: A dictionary of extracted issue details.
    """
    details = {
        "title": issue.fields.summary,
        "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
        "deadline": format_date(issue.fields.customfield_10703) if hasattr(issue.fields,
                                                                           'customfield_10703') and issue.fields.customfield_10703 else " ",
        "krs": issue.fields.customfield_10704 if hasattr(issue.fields,
                                                         'customfield_10704') and issue.fields.customfield_10704 else " ",
        "stakeholder": issue.fields.customfield_10707 if hasattr(issue.fields,
                                                                 'customfield_10707') and issue.fields.customfield_10707 else " ",
        "accomplishments": issue.fields.customfield_10706 if hasattr(issue.fields,
                                                                     'customfield_10706') and issue.fields.customfield_10706 else " ",
        "challenges": issue.fields.customfield_10705 if hasattr(issue.fields,
                                                                'customfield_10705') and issue.fields.customfield_10705 else " ",
        "status": BoardStatus.map_status(issue.fields.status.name),
        "estimate": f"{issue.fields.customfield_10107} Hours" if hasattr(issue.fields,
                                                                         'customfield_10107') and issue.fields.customfield_10107 else " ",
        "scope_changed": "Yes" if hasattr(issue.fields,
                                          'customfield_10030') and issue.fields.customfield_10030 else " "
    }

    # Determine the start date as the date when the issue first transitioned to "In Progress"
    changelog = issue.changelog
    start = None
    for history in changelog.histories:
        for item in history.items:
            if item.field == "status" and BoardStatus.map_status(item.toString) == BoardStatus.IN_PROGRESS.value:
                start = history.created.split('T')[0]
                break
        if start:
            break

    details["start"] = format_date(start) if start else "Not Started"

    # Fetch the last three status changes
    status_changes = []
    for history in reversed(changelog.histories):
        for item in history.items:
            if item.field == "status":
                mapped_status = BoardStatus.map_status(item.toString)
                date_formatted = format_date(history.created.split('T')[0])
                status_changes.append((mapped_status, date_formatted))
        if len(status_changes) == 4:
            break

    details["progress_statuses_dates"] = status_changes[::-1] if status_changes else [("No Status", "N/A")]

    # # Print all details
    # print("Issue Details:")
    # for key, value in details.items():
    #     print(f"{key.capitalize()}: {value}")

    # Define the path to save the Gantt chart image
    gantt_chart_image_path = f"{issue.key}_gantt_chart.png"

    # Draw and save the Gantt chart for the selected issue
    draw_gantt_chart_for_issue(jira_instance, issue.key, gantt_chart_image_path)
    details["gantt_chart_image_path"] = gantt_chart_image_path
    return details


def format_date(date_str):
    """
    Formats a date string in the format YYYY-MM-DD to 'Month Day' (e.g., 'July 4').

    :param date_str: The date string in 'YYYY-MM-DD' format.
    :return: The formatted date string.
    """
    if not date_str:
        return "No Date"
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%B %d').replace(' 0', ' ')  # Removes leading zero from the day


def create_summary_presentation(prs, issues_details):
    """
    Creates a PowerPoint presentation with slides for each issue and an assignee slide when slides of an assignee start.

    :param prs: A PowerPoint Presentation object.
    :param issues_details: A list of dictionaries containing issue details.
    """
    slideCreator.create_squad_slide(prs, title="InStore Squad")

    last_assignee = None

    for details in issues_details:
        stakeholder_value = details['stakeholder']
        if isinstance(stakeholder_value, list):
            stakeholder_value = ', '.join(map(str, stakeholder_value))
        stakeholder_value = stakeholder_value.strip("[]").replace("'", "")
        details['stakeholder'] = stakeholder_value

        # Check if the assignee has changed
        if details['assignee'] != last_assignee:
            # Create a new assignee slide
            slideCreator.create_assignee_slide(
                prs,
                assignee_name=details['assignee'],
            )
            last_assignee = details['assignee']

        slideCreator.create_summary_slide(
            prs,
            title=f"{details['title']}",
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
            gann_chart_path=details['gantt_chart_image_path'],
        )
        slideCreator.insert_gantt_chart_to_slide(prs, details['gantt_chart_image_path'])


def save_presentation(prs, filename):
    """
    Saves the PowerPoint presentation.

    :param prs: A PowerPoint Presentation object.
    :param filename: The filename to save the presentation as.
    """
    prs.save(filename)
    print(f"Presentation saved as '{filename}'")


def main(jira_url, username, password, exception_statuses):
    """
    Main function to fetch JIRA issues from a sprint and create a PowerPoint presentation.

    :param exception_statuses:
    :param jira_url: The base URL of the JIRA instance.
    :param username: The JIRA username.
    :param password: The JIRA password.
    :param sprint_id: The ID of the sprint to fetch issues from.
    :param output_filename: The filename to save the presentation as.
    """
    # Initialize JIRA connection
    jiraInstance = initialize_jira_connection(jira_url, username, password)

    # list_all_boards(jiraInstance)
    # return
    # print_sprint_title_and_issue_id(jiraInstance,"WS-838")
    # return
    activeSprint = get_active_sprint(jiraInstance, BOARD_ID)

    # notify_incomplete_tasks(jiraInstance, activeSprint.id)

    # Fetch issues from the specified sprint
    issues_in_sprint = fetch_issues_from_sprint(jiraInstance, activeSprint.id, exception_statuses)

    # Extract details from each issue
    issues_details = [extract_issue_details(jiraInstance, issue) for issue in issues_in_sprint]

    # def custom_sort_key(issue_detail):
    #     assignee = issue_detail['assignee']
    #     return (assignee != "Pouria Azadeh", assignee)

    # sorted_issues_details = sorted(issues_details, key=custom_sort_key)

    # Initialize a PowerPoint presentation
    prs = Presentation()

    # Create the presentation slides
    create_summary_presentation(prs, issues_details)

    # Save the presentation
    save_presentation(prs, f"{activeSprint.name}.pptx")
    delete_gantt_chart_images()


def list_all_custom_fields(jira_instance):
    """
    Lists all custom fields available in the Jira instance.

    :param jira_instance: An authenticated JIRA instance.
    :return: A list of custom fields with their names and IDs.
    """
    try:
        # Fetch all custom fields
        custom_fields = jira_instance.fields()

        # Print custom fields
        for field in custom_fields:
            print(f"Name: {field['name']}, ID: {field['id']}")

    except JIRAError as e:
        print(f"Failed to fetch custom fields from JIRA: {e}")
        return []


def list_tasks_with_missing_fields(jira_instance, sprint_id):
    """
    Lists tasks that are missing at least one of the specified fields along with their issue number, assignee, reporter, and unfilled fields.

    :param jira_instance: An authenticated JIRA instance.
    :return: A list of dictionaries containing task details with missing fields.
    """
    try:
        # Define JQL query to find issues in the specified sprint
        jql_query = f'sprint = {sprint_id} AND (issuetype = "Task" OR issuetype = "Bug")'

        issues = jira_instance.search_issues(jql_query)
        print(f"Found {len(issues)} issues.")

        tasks_with_missing_fields = []
        for issue in issues:
            missing_fields = []

            if not issue.fields.summary:
                missing_fields.append("title")

            if not issue.fields.assignee:
                missing_fields.append("assignee")

            if not (hasattr(issue.fields, 'customfield_10703') and issue.fields.customfield_10703):
                missing_fields.append("deadline")

            if not (hasattr(issue.fields, 'customfield_10704') and issue.fields.customfield_10704):
                missing_fields.append("krs")

            if not (hasattr(issue.fields, 'customfield_10707') and issue.fields.customfield_10707):
                missing_fields.append("stakeholder")

            # if not (hasattr(issue.fields, 'customfield_10706') and issue.fields.customfield_10706):
            #     missing_fields.append("accomplishments")
            #
            # if not (hasattr(issue.fields, 'customfield_10705') and issue.fields.customfield_10705):
            #     missing_fields.append("challenges")

            if not (hasattr(issue.fields, 'customfield_10107') and issue.fields.customfield_10107):
                missing_fields.append("estimate")

            if missing_fields:
                task_info = {
                    "issue_number": issue.key,
                    "summary": issue.fields.summary,
                    "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                    "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "Unreported",
                    "missing_fields": missing_fields,
                    'issue_link': f"{jira_instance.server_url}/browse/{issue.key}",  # URL to the issue

                }
                tasks_with_missing_fields.append(task_info)

                # # Print the relevant details for each task
                # print(f"Issue Number: {issue.key}, Summary: {task_info['summary']}, Assignee: {task_info['assignee']}, "
                #       f"Reporter: {task_info['reporter']}, Missing Fields: {', '.join(missing_fields)}")

        print(f"Total tasks with missing fields: {len(tasks_with_missing_fields)}")
        return tasks_with_missing_fields

    except JIRAError as e:
        print(f"Failed to fetch tasks from JIRA: {e}")
        return []


def notify_incomplete_tasks(jira_instance, sprint_id):
    """
    Notifies assignees about tasks with missing fields in a specific sprint.

    :param jira_instance: The JIRA instance object.
    :param sprint_id: The ID of the sprint to notify about.
    """
    tasks_with_missing_fields = list_tasks_with_missing_fields(jira_instance, sprint_id)

    # Initialize the dictionary to map assignees to their tasks
    tasks_by_assignee = {}

    for task in tasks_with_missing_fields:
        assignee = task['assignee']
        email = PARTICIPANT_EMAIL_MAP.get(assignee)

        # Initialize the list for new assignees
        if assignee not in tasks_by_assignee:
            tasks_by_assignee[assignee] = []

        # Append the task to the assignee's list
        if email:
            tasks_by_assignee[assignee].append(task)

    # Send emails to each assignee with their incomplete tasks
    for assignee, tasks in tasks_by_assignee.items():
        email = PARTICIPANT_EMAIL_MAP.get(assignee)
        if not email:
            continue

        subject = "Tasks with Missing Fields Assigned to You"

        # Build the body content
        body_lines = [
            f"Dear {assignee},",
            "",
            "Here are the tasks assigned to you with missing fields:",
            ""
        ]

        # Append task details
        for task in tasks:
            task_line = f"Issue Number: {task['issue_number']}, Summary: {task['summary']}, Missing Fields: {', '.join(task['missing_fields'])}\nIssue Link: {task['issue_link']}\n"
            body_lines.append(task_line)

        # Add closing lines
        body_lines.extend([
            "",
            "Please review and update these tasks accordingly.",
            "",
            "Best regards,",
            "Your Jira Bot\n\n"
        ])

        # Join all lines into the final body
        body = "\n".join(body_lines)
        print(body)


def list_sprint_participants(jira_instance, sprint_id):
    """
    Lists all participants (assignees, reporters, and watchers) in a sprint.

    :param jira_instance: An authenticated JIRA instance.
    :param sprint_id: The ID of the sprint.
    :return: A set of participant names involved in the sprint.
    """
    participants = set()

    try:
        # JQL to fetch all issues in the specified sprint
        jql = f"sprint = {sprint_id}"
        issues = jira_instance.search_issues(jql, expand='names')

        for issue in issues:
            # Add assignee to participants
            if issue.fields.assignee:
                participants.add(issue.fields.assignee.displayName)

            # Add reporter to participants
            if issue.fields.reporter:
                participants.add(issue.fields.reporter.displayName)

        # Print or return the list of participants
        participants_list = sorted(participants)
        for participant in participants_list:
            print(participant)

        return participants_list

    except JIRAError as e:
        print(f"Failed to fetch participants from JIRA: {e}")
        return []


def print_all_sprints(jira_instance, board_id):
    """
    Fetches and prints all sprints from a specific JIRA board.

    :param jira_server_url: The base URL of your JIRA instance (e.g., "https://yourdomain.atlassian.net").
    :param board_id: The ID of the JIRA board to fetch sprints from.
    :param username: The username for JIRA API authentication.
    :param api_token: The API token for JIRA API authentication.
    """
    try:

        # Get all sprints for the specified board
        sprints = jira_instance.sprints(board_id)

        if not sprints:
            print("No sprints found for this board.")
        else:
            print("Sprints for the board:")
            for sprint in sprints:
                print(f"ID: {sprint.id}, Name: {sprint.name}, State: {sprint.state}")
    except:
        print("error")


def get_active_sprint(jira_instance, board_id):
    """
    Fetches and returns the active sprint from a specific JIRA board.

    :param jira_instance: The JIRA instance object used to interact with the JIRA API.
    :param board_id: The ID of the JIRA board to fetch the active sprint from.
    :return: The active sprint as a dictionary if found, otherwise None.
    """
    try:
        # Get all sprints for the specified board
        sprints = jira_instance.sprints(board_id)

        if not sprints:
            print("No sprints found for this board.")
            return None

        # Find and return the active sprint
        for sprint in sprints:
            if sprint.state.lower() == "active":
                return sprint

        print("No active sprint found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


import re


def print_sprint_title_and_issue_id(jira_instance, issue_key):
    """
    Fetches and prints the sprint title and issue ID for a specific JIRA task (issue).

    :param jira_instance: An authenticated JIRA instance.
    :param issue_key: The key of the JIRA issue (e.g., "PROJ-123").
    """
    try:
        # Fetch the issue from JIRA
        issue = jira_instance.issue(issue_key)

        # Get the sprint field (using custom field ID customfield_10106)
        issue_sprints = getattr(issue.fields, 'customfield_10106', None)
        issue_id = issue.key

        if issue_sprints:
            for sprint in issue_sprints:
                # Extract sprint title using regex (assuming name is within `name=...`)
                match = re.search(r'name=([^,]+)', sprint)
                if match:
                    sprint_title = match.group(1)
                    print(f"Sprint Title: {sprint_title}, Issue ID: {issue_id}")
                else:
                    print(f"No sprint title found for issue ID: {issue_id}")
        else:
            print(f"No sprint associated with issue ID: {issue_id}")

    except Exception as e:
        print(f"An error occurred while fetching the sprint and issue ID: {e}")


def draw_gantt_chart_for_issue(jira_instance, issue_id, output_image_path):
    """
    Draws a Gantt chart for a specific JIRA issue based on its status transitions
    and saves it as an image to be used in the PowerPoint presentation.

    :param jira_instance: An authenticated JIRA instance.
    :param issue_id: The ID of the JIRA issue.
    :param output_image_path: The file path to save the Gantt chart image.
    """
    # Fetch the issue with its changelog
    issue = jira_instance.issue(issue_id, expand='changelog')
    changelog = issue.changelog

    # Initialize status_durations and add the initial "To Do" period
    status_durations = []
    creation_date = datetime.strptime(issue.fields.created.split('T')[0], '%Y-%m-%d')
    previous_status = "To Do"  # Assume the issue started in "To Do"
    previous_time = creation_date

    # Loop through the changelog to track status transitions
    for history in changelog.histories:
        for item in history.items:
            if item.field == 'status':
                current_time = datetime.strptime(history.created.split('T')[0], '%Y-%m-%d')
                current_status = item.toString

                # Append the status duration
                status_durations.append({
                    'status': previous_status,
                    'start_date': previous_time,
                    'end_date': current_time,
                    'duration_days': (current_time - previous_time).days
                })

                # Update previous status and time
                previous_status = current_status
                previous_time = current_time

    # Handle the final status (currently ongoing)
    if previous_status is not None:
        current_time = datetime.now()
        status_durations.append({
            'status': previous_status,
            'start_date': previous_time,
            'end_date': current_time,
            'duration_days': (current_time - previous_time).days
        })

    # Convert the status_durations to a DataFrame
    df = pd.DataFrame(status_durations)

    # Define a consistent and unique color map for statuses
    status_colors = {
        "To Do": "blue",  # Unique color
        "InProgress": "green",  # Unique color
        "Dev": "red",  # Unique color
        "Code Review": "purple",  # Unique color
        "Ready for Test (Stage)": "orange",  # Unique color
        "Resolved": "gray",  # Unique color
        "Live Test": "yellow",  # Unique color
        "Done": "cyan"  # Unique color
    }

    # Plot the Gantt chart
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        status = row['status']
        color = status_colors.get(status, "gray")  # Default to gray if no color is found
        ax.barh(row['status'], (row['end_date'] - row['start_date']).days, left=row['start_date'], color=color)

    # Calculate the total date range and dynamically set the interval
    date_range_days = (df['end_date'].max() - df['start_date'].min()).days

    if date_range_days <= 10:
        interval = 1  # For short date ranges, show every day
    elif date_range_days <= 30:
        interval = 2  # For medium date ranges, show every 2 days
    elif date_range_days <= 60:
        interval = 5  # For slightly longer date ranges, show every 5 days
    else:
        interval = 7  # For longer date ranges, show every 7 days (1 week)

    # Format the date axis to show dynamically set dates
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    plt.xlabel('Date')
    plt.ylabel('Status')
    plt.title(f'Gantt Chart for Issue {issue_id}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the Gantt chart as an image file
    plt.savefig(output_image_path, format='png')
    plt.close(fig)  # Close the figure to release memory


def delete_gantt_chart_images(image_folder=None):
    """
    Deletes all Gantt chart image files with the pattern *_gantt_chart.png.
    If no folder is specified, it uses the current working directory.

    :param image_folder: The folder where the Gantt chart images are stored. Defaults to the current directory.
    """
    # Use the current working directory if no folder is provided
    if image_folder is None:
        image_folder = os.getcwd()

    # Define the pattern for the Gantt chart images
    pattern = os.path.join(image_folder, '*_gantt_chart.png')

    # Find all files that match the pattern
    gantt_chart_files = glob.glob(pattern)

    # Delete each file
    for file_path in gantt_chart_files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    if not gantt_chart_files:
        print("No Gantt chart files found to delete.")


def list_all_boards(jira_instance):
    """
    Lists all boards with their names and IDs in a Jira instance.

    :param jira_instance: An authenticated JIRA instance.
    :return: A list of dictionaries containing board names and IDs.
    """
    try:
        boards = jira_instance.boards()

        if not boards:
            print("No boards found.")
            return []

        boards_list = []
        for board in boards:
            board_info = {
                "id": board.id,
                "name": board.name
            }
            boards_list.append(board_info)
            print(f"Board ID: {board.id}, Name: {board.name}")

        return boards_list

    except JIRAError as e:
        print(f"Failed to fetch boards from JIRA: {e}")
        return []


if __name__ == "__main__":
    load_dotenv()

    JIRA_URL = os.getenv("JIRA_URL")
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")

    BOARD_ID = 13
    EXCEPTION_STATUSES = ["Live Test", "Done", "To Do"]

    main(JIRA_URL, USERNAME, PASSWORD, EXCEPTION_STATUSES)

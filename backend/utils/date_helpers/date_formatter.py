from datetime import datetime


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

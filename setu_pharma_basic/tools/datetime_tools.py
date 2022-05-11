from datetime import timedelta
import calendar


def get_daterange(start_date, end_date):
    """ Prepare daterange to perform iterative operations with dates. """
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


def get_list_of_months():
    """ Return list of Months """
    return [(str(i), calendar.month_name[i]) for i in range(0, len(list(calendar.month_name)))]


def get_list_of_day_name():
    """ Return list of Day Names with number """
    return [(str(i), calendar.day_name[i]) for i in range(0, len(list(calendar.day_name)))]

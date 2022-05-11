import logging

log = logging.getLogger("Math_Tools")


def calculate_percentage_value(value, percentage):
    """ Calculate Percentage Value for main value. """
    p_value = 0
    try:
        p_value = value * percentage / 100
    except ZeroDivisionError as ze:
        log.warning("Float Division By Zero Warning Raised! : %s", ze)
    finally:
        return p_value


def minus_value_on_percentage(value, percentage):
    """ Subtract percentage value to main value. """
    return value - (calculate_percentage_value(value, percentage))


def add_value_on_percentage(value, percentage):
    """ Add percentage value to main value. """
    return value + (calculate_percentage_value(value, percentage))

from ..utils import Date, DayCount, day_count_fraction
from . import domains

# Utility functions for converting a CurveDataPoint to a given domain

def time_difference(start_date, end_date, time_domain):
    if time_domain == domains.TIME_ACT_365:
        day_count = DayCount.ACT_365
    elif time_domain == domains.TIME_30_360:
        day_count = DayCount.THIRTY_360
    else:
        raise ValueError(f'Unsupported time domain: {time_domain}.')

    return day_count_fraction(start_date, end_date, day_count)

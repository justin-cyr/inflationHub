from ..utils import Date
from . import domains

# Utility functions for converting a CurveDataPoint to a given domain

def time_difference(start_date, end_date, time_domain):
    # convert to datetime.date
    start_date = Date(start_date).datetime_date()
    end_date = Date(end_date).datetime_date()

    day_diff = (end_date - start_date).days

    if time_domain == domains.TIME_ACT_365:
        one_year_in_days = 365.0
    elif time_domain == domains.TIME_30_360:
        one_year_in_days = 360.0
        raise NotImplementedError(f'{domains.TIME_30_360} time domain not yet supported.')
    else:
        raise ValueError(f'Unsupported time domain: {time_domain}.')

    return day_diff / one_year_in_days

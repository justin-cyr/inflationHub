
from enum import Enum, auto
import json
import os
from ..utils import Date

# get logger from current_app instance
from flask import current_app as app

class ObservanceRule(Enum):
    NONE = auto()                  # do not observe holidays that fall on weekends
    XSAT_SUN2MON = auto()          # do not observe holidays on Sat, observe Sun holidays on next Mon
    SAT2FRI_XSUN = auto()          # observe Sat holidays on preceding Fri, do not observe Sun holidays
    NEAREST_WEEKDAY = auto()       # observe Sat holidays on preceding Fri, observe Sun holidays on next Mon

    @classmethod
    def apply_rule(cls, holiday, rule):
        """ Apply observance rule to this holiday.
            Return None if no holiday is observed.
            pre-condition: holiday falls on a weekend.
        """
        if rule == cls.NONE:
            return None

        elif rule == cls.XSAT_SUN2MON:
            if holiday.weekday() == 5:
                return None
            else:
                return holiday.addDays(1)

        elif rule == cls.SAT2FRI_XSUN:
            if holiday.weekday() == 5:
                return holiday.addDays(-1)
            else:
                return None

        elif rule == cls.NEAREST_WEEKDAY:
            if holiday.weekday() == 5:
                return holiday.addDays(-1)
            else:
                return holiday.addDays(1)

        else:
            raise ValueError(f'ObservanceRule: unsupported rule {rule}.')


class BumpDirection(Enum):
    FORWARD = auto()
    BACKWARD = auto()


class Calendar(object):

    calendars_root = os.path.join(os.getcwd(), 'backend/utilities/calendarfiles')

    def __init__(self, name):
        self.name = name.upper()
        # read from calendar file, set min and max years
        calendar_path = os.path.join(Calendar.calendars_root, self.name + '.json')

        try:
            with open(calendar_path, 'r') as f:
                calendar_data = json.load(f)

            self.min_year = int(calendar_data['min_year'])
            self.max_year = int(calendar_data['max_year'])
            self.holidays = { Date(d) for d in calendar_data['holidays'] }

        except Exception as e:
            app.logger.error(f'Could not read calendar {name}: {e}')
            raise e

    def __repr__(self):
        return f'Calendar({self.name})'

    def is_business_day(self, date):
        """Return True if this date is a business day in the holiday calendar, False otherwise."""
        date = Date(date)
        return date.is_weekday() and (date not in self.holidays)

    def add_business_days(self, date, bump_days, direction=BumpDirection.FORWARD):
        """ Return the business day that is bump_days from date.
            If date is not already a bday, then move to the nearest bday and start counting from there.
        """
        if bump_days < 0:
            raise ValueError('Calendar.add_buisiness_days: bump_days cannot be negative. Use BumpDirection.BACKWARD.')
        
        if direction == BumpDirection.FORWARD:
            inc = 1
        elif direction == BumpDirection.BACKWARD:
            inc = -1
        else:
            raise ValueError('Calendar.add_buisiness_days: unsupported BumpDirection, must be FORWARD or BACKWARD.')
        
        # move to nearest business day
        date = Date(date)
        while (not self.is_business_day(date)):
            date = date.addDays(inc)

        bdays_added = 0
        while (bdays_added < bump_days):
            date = date.addDays(inc)
            while (not self.is_business_day(date)):
                date = date.addDays(inc)
            bdays_added += 1

        return date

    def nearest_business_day(self, date, direction=BumpDirection.FORWARD):
        """Return the nearest bday to date."""
        return self.add_business_days(date, 0, direction)
        

    @staticmethod
    def generate(name, min_year, max_year):
        """Create a new calendar file for calendar name from min_year to max_year."""
        calendar_generators = {
            'NYB': Calendar.generate_NYB
        }

        if name in calendar_generators:
            generate_cal = calendar_generators[name]
            holidays = []
            for year in range(min_year, max_year + 1):
                holidays += generate_cal(year)

            calendar_data = dict(
                min_year=min_year,
                max_year=max_year,
                holidays=[str(h) for h in holidays]
            )
            # write
            calendar_path = os.path.join(Calendar.calendars_root, name + '.json')
            with open(calendar_path, 'w') as f:
                json.dump(calendar_data, f)
        else:
            raise ValueError(f'Calendars.generate: no holiday generator for calendar {name}.')

    # Functions for returning specific holidays in a given year
    # decorator
    def apply_observance_rule(get_holiday):
        def inner(year, rule):
            holiday = get_holiday(year, rule)
            return holiday if holiday.is_weekday() else ObservanceRule.apply_rule(holiday, rule)
        return inner

    @staticmethod
    @apply_observance_rule
    def get_new_years_day(year, rule):
        return Date(f'{year}-01-01')

    @staticmethod
    @apply_observance_rule
    def get_mlk_day(year, rule):
        """3rd Monday in January"""
        # earliest is 15th, latest is 22nd
        holiday = Date(f'{year}-01-15')
        holiday = holiday.addDays(-holiday.weekday() % 7)
        return holiday

    @staticmethod
    @apply_observance_rule
    def get_presidents_day(year, rule):
        """3rd Monday in Februrary"""
        # earliest is 15th, latest is 22nd
        holiday = Date(f'{year}-02-15')
        holiday = holiday.addDays(-holiday.weekday() % 7)
        return holiday

    @staticmethod
    @apply_observance_rule
    def get_memorial_day(year, rule):
        """Last Monday in May"""
        # earliest is 25th, latest is 31st
        holiday = Date(f'{year}-05-25')
        holiday = holiday.addDays(-holiday.weekday() % 7)
        return holiday

    @staticmethod
    @apply_observance_rule
    def get_juneteenth(year, rule):
        return Date(f'{year}-06-19')

    @staticmethod
    @apply_observance_rule
    def get_july_fourth(year, rule):
        return Date(f'{year}-07-04')

    @staticmethod
    @apply_observance_rule
    def get_labor_day(year, rule):
        """First Monday in September"""
        # earliest is 1st, latest is 7th
        holiday = Date(f'{year}-09-01')
        holiday = holiday.addDays(-holiday.weekday() % 7)
        return holiday

    @staticmethod
    @apply_observance_rule
    def get_columbus_day(year, rule):
        """2nd Monday in October"""
        # earliest is 8th, latest is 14th
        holiday = Date(f'{year}-10-08')
        holiday = holiday.addDays((-holiday.weekday()) % 7)
        return holiday

    @staticmethod
    @apply_observance_rule
    def get_veterans_day(year, rule):
        return Date(f'{year}-11-11')

    @staticmethod
    @apply_observance_rule
    def get_thanksgiving_day(year, rule):
        """4th Thursday in November"""
        # earliest is 22th, latest is 28th
        holiday = Date(f'{year}-11-22')
        holiday = holiday.addDays((3 - holiday.weekday()) % 7)
        return holiday

    @staticmethod
    @apply_observance_rule
    def get_christmas_day(year, rule):
        return Date(f'{year}-12-25')


    # Generate specific calendar holidays in a given year
    # decorator
    def filter_nonobserved(generate_cal):
        def inner(year):
            holidays = generate_cal(year)
            return [h for h in holidays if h]
        return inner

    @staticmethod
    @filter_nonobserved
    def generate_NYB(year):
        rule = ObservanceRule.XSAT_SUN2MON
        return [
            Calendar.get_new_years_day(year, rule),
            Calendar.get_mlk_day(year, rule),
            Calendar.get_presidents_day(year, rule),
            Calendar.get_memorial_day(year, rule),
            Calendar.get_juneteenth(year, rule) if year >= 2021 else None,
            Calendar.get_july_fourth(year, rule),
            Calendar.get_labor_day(year, rule),
            Calendar.get_columbus_day(year, rule),
            Calendar.get_veterans_day(year, rule),
            Calendar.get_thanksgiving_day(year, rule),
            Calendar.get_christmas_day(year, rule)
        ]

        

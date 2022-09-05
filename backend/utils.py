
import datetime
from enum import Enum, auto

class Date(object):
    # wraps datetime.date but allows conversion from string types in constructor
    def __init__(self, date):

        date = str(date)

        supported_formats = [
            '%Y-%m-%d', # 2022-04-01
            '%Y%m%d',   # 20220401
            '%Y-%m',    # 2022-04
            '%Y %b'     # 2022 Apr
        ]
        date_obj = None
        for fmt in supported_formats:
            try:
                date_obj = datetime.datetime.strptime(date, fmt).date()
                break
            except ValueError as e:
                pass

        if date_obj:
            date = date_obj
        else:
            raise TypeError(f'Unsupported date format: {date}')

        self.date = date
        # datetime.date API
        self.year = date.year
        self.month = date.month
        self.day = date.day

    
    def __repr__(self):
        return str(self.date)

    def __hash__(self):
        return self.__repr__().__hash__()

    def datetime_date(self):
        return self.date

    def start_of_month(self):
        return Date(self.__repr__()[:-3] + '-01')

    # Overload binary operators
    def __lt__(self, rhs):
        rhs = Date(rhs)
        return self.datetime_date() < rhs.datetime_date()

    def __le__(self, rhs):
        rhs = Date(rhs)
        return self.datetime_date() <= rhs.datetime_date()

    def __gt__(self, rhs):
        rhs = Date(rhs)
        return self.datetime_date() > rhs.datetime_date()

    def __gt__(self, rhs):
        rhs = Date(rhs)
        return self.datetime_date() >= rhs.datetime_date()

    def __eq__(self, rhs):
        rhs = Date(rhs)
        return self.datetime_date() == rhs.datetime_date()

    def __ne__(self, rhs):
        rhs = Date(rhs)
        return self.datetime_date() != rhs.datetime_date()

    def __sub__(self, rhs):
        rhs = Date(rhs)
        return self.datetime_date() - rhs.datetime_date()

    @classmethod
    def today(cls):
        return Date(datetime.date.today())

    def weekday(self):
        return self.datetime_date().weekday()

    def is_weekday(self):
        return self.weekday() < 5

    def is_weekend(self):
        return self.weekday() >= 5

    # leap year rules
    def isLeapYear(self):
        return Date.class_isLeapYear(self.year)

    @classmethod
    def class_isLeapYear(cls, year):
        if year % 100 == 0:
            return year % 400 == 0
        else:
            return year % 4 == 0

    def isLeapDay(self):
        return (self.isLeapYear() and self.month == 2 and self.day == 29)

    def isBeforeLeapDay(self):
        return (self.isLeapYear() and self.month == 1 or (self.month == 2 and self.day < 29))

    # days in month
    def daysInMonth(self):
        return Date.class_daysInMonth(self.month, self.year)

    @classmethod
    def class_daysInMonth(cls, month, year):
        """Return the number of days in this month."""
        daysInMonth = {
            1: 31,
            2: 28,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31
        }
        if month == 2 and Date.class_isLeapYear(year):
            return 29
        else:
            return daysInMonth[month]

    # bump functions
    def addOneYear(self):
        """Return a new Date that is 1Y ahead of this date."""
        # adjust for leap day
        day = self.day if not self.isLeapDay() else 28
        return Date(datetime.date(self.year + 1, self.month, day))

    def addDays(self, days):
        """Return a new Date that is days ahead of this date."""
        return Date(self.datetime_date() + datetime.timedelta(days=days))

    def addTenor(self, tenor):
        """Return a new Date that is tenor ahead of this date."""
        tenor = Tenor(tenor)

        # Handle each tenor unit separately
        if tenor.unit == 'Y':
            num_years = tenor.size
            date = self
            while num_years > 0:
                date = date.addOneYear()
                num_years -= 1
            return date

        elif tenor.unit == 'M':
            raise NotImplementedError('Date.addTenor: monthly tenors not yet supported.')

        elif tenor.unit == 'D':
            return self.addDays(tenor.size)
        else:
            raise ValueError(f'Date.addTenor: unsupported tenor unit it {tenor}')


class DateTime(object):
    # wraps datetime.datetime but allows conversion from string types in constructor
    def __init__(self, dt):

        dt = str(dt)

        supported_formats = [
            '%Y%m%d%H%M%S',         # 20220401170435
            '%Y-%m-%d %H:%M:%S',    # 2022-04-01 17:04:35
            '%Y-%m-%d %H:%M:%S.%f', # 2022-04-01 17:04:35.987654
            # Date formats
            '%Y-%m-%d', # 2022-04-01
            '%Y%m%d',   # 20220401
            '%Y-%m',    # 2022-04
            '%Y %b'     # 2022 Apr
        ]
        date_obj = None
        for fmt in supported_formats:
            try:
                date_obj = datetime.datetime.strptime(dt, fmt)
                break
            except ValueError:
                pass

        if date_obj:
            dt = date_obj
        else:
            raise TypeError(f'Unsupported date format: {dt}')

        self.datetime = dt
        # datetime.datetime API
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.hour = dt.hour
        self.minute = dt.minute
        self.second = dt.second
        self.microsecond = dt.microsecond

    
    def __repr__(self):
        return self.datetime.strftime('%Y-%m-%d %H:%M:%S')

    # use self.datetime to access the underlying datetime.datetime

    def get_date(self):
        return Date(self.datetime.strftime('%Y-%m-%d'))


class Tenor(object):
    def __init__(self, tenor_str):
        tenor = str(tenor_str).upper()
        if not (tenor.endswith('Y') or tenor.endswith('M') or tenor.endswith('D')):
            raise ValueError(f'Tenor expected to end with Y, M, D but got {tenor_str}')

        if not tenor[:-1].isnumeric():
            raise ValueError(f'Tenor expected to start with number but got {tenor_str}')

        self.tenor = tenor
        self.unit = tenor[-1]
        self.size = int(tenor[:-1])

    def __repr__(self):
        return self.tenor


class DayCount(Enum):
    ACT_365 = auto()
    ACT_360 = auto()
    THIRTY_360 = auto()


def day_count_fraction(start_date, end_date, day_count):
    start_date = Date(start_date)
    end_date = Date(end_date)

    if day_count == DayCount.ACT_365:
        return (end_date - start_date).days / 365.0
    else:
        raise NotImplementedError(f'day_count_fraction for {day_count} is not implemented.')

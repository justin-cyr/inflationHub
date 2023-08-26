
import datetime
from enum import Enum, auto

class StrEnum(Enum):

    def to_str(self):
        return str(self).split('.')[-1].upper()

    @classmethod
    def from_str(cls, s):
        if isinstance(s, cls):
            return s

        s = str(s).upper()
        for e in cls:
            if s == e.to_str():
                return e
        raise ValueError(f'{cls}: {s} is not an enum member.')


class DayCount(StrEnum):
    ACT_365 = auto()
    ACT_360 = auto()
    THIRTY_360 = auto()
    ACT_ACT = auto()

class BumpDirection(StrEnum):
    FORWARD = auto()
    BACKWARD = auto()

class EomRule(StrEnum):
    LAST = auto()
    SAME = auto()

class DateFrequency(StrEnum):
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    QUARTERLY = auto() 
    SEMIANNUALLY = auto()
    YEARLY = auto()

    def tenor_unit_to_frequency(unit):
        unit = unit.upper()
        if unit == 'D':
            return DateFrequency.DAILY
        elif unit == 'W':
            return DateFrequency.WEEKLY
        elif unit == 'M':
            return DateFrequency.MONTHLY
        elif unit == 'Q':
            return DateFrequency.QUARTERLY
        elif unit == 'S':
            return DateFrequency.SEMIANNUALLY
        elif unit == 'Y':
            return DateFrequency.YEARLY
        else:
            raise ValueError(f'DateFrequency.tenor_unit_to_frequency: unsupported tenor unit {unit}')

    def periods_per_year(self):
        if self == DateFrequency.DAILY:
            return 365
        elif self == DateFrequency.WEEKLY:
            return 52
        elif self == DateFrequency.MONTHLY:
            return 12
        elif self == DateFrequency.QUARTERLY:
            return 4
        elif self == DateFrequency.SEMIANNUALLY:
            return 2
        elif self == DateFrequency.YEARLY:
            return 1
        else:
            raise NotImplementedError(f'DateFrequency.periods_per_year: not implemented for {self}')
        

class YieldConvention(StrEnum):
    TRUE_YIELD = auto()
    US_STREET = auto()
    US_TBILL = auto()


class Month(StrEnum):
    JAN = auto()
    FEB = auto()
    MAR = auto()
    APR = auto()
    MAY = auto()
    JUN = auto()
    JUL = auto()
    AUG = auto()
    SEP = auto()
    OCT = auto()
    NOV = auto()
    DEC = auto()

    def __repr__(self):
        return self.to_str()

    @classmethod
    def num_map(cls):
        return {
            Month.JAN: 1,
            Month.FEB: 2,
            Month.MAR: 3,
            Month.APR: 4,
            Month.MAY: 5,
            Month.JUN: 6,
            Month.JUL: 7,
            Month.AUG: 8,
            Month.SEP: 9,
            Month.OCT: 10,
            Month.NOV: 11,
            Month.DEC: 12
        }

    @classmethod
    def from_str_slice(cls, s):
        if isinstance(s, str):
            s = s[:3]
        return cls.from_str(s)

    def to_num(self):
        return Month.num_map()[self]

    @classmethod
    def from_num(cls, num):
        num = int(num)
        for k, v in Month.num_map().items():
            if v == num:
                return k
        raise ValueError(f'{cls}.{__name__}: invalid month number {num}.')


class Date(object):
    # wraps datetime.date but allows conversion from string types in constructor
    def __init__(self, date):

        if isinstance(date, Date):
            self.date = date.date
        elif isinstance(date, datetime.date):
            self.date = date
        else:
            date = str(date)

            supported_formats = [
                '%Y-%m-%d', # 2022-04-01
                '%Y%m%d',   # 20220401
                '%Y-%m',    # 2022-04
                '%Y %b',    # 2022 Apr
                '%d %b %Y', # 01 Apr 2022
                '%d-%b-%Y'  # 01-Apr-2022
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
        self.hash = self.year * 10000 + self.month * 100 + self.day

    
    def __repr__(self):
        return str(self.date)

    def __hash__(self):
        return self.hash

    def datetime_date(self):
        return self.date

    def start_of_month(self):
        return Date(self.__repr__()[:-3] + '-01')

    # Overload binary operators
    def __lt__(self, rhs):
        if not isinstance(rhs, Date):
            rhs = Date(rhs)
        return self.hash < rhs.hash

    def __le__(self, rhs):
        if not isinstance(rhs, Date):
            rhs = Date(rhs)
        return self.hash <= rhs.hash

    def __gt__(self, rhs):
        if not isinstance(rhs, Date):
            rhs = Date(rhs)
        return self.hash > rhs.hash

    def __ge__(self, rhs):
        if not isinstance(rhs, Date):
            rhs = Date(rhs)
        return self.hash >= rhs.hash

    def __eq__(self, rhs):
        # no type check to save a constructor call
        return self.hash == rhs.hash

    def __ne__(self, rhs):
        # no type check to save a constructor call
        return self.hash != rhs.hash

    def __sub__(self, rhs):
        if not isinstance(rhs, Date):
            rhs = Date(rhs)
        return self.date - rhs.date

    @classmethod
    def today(cls):
        return Date(datetime.date.today())

    def weekday(self):
        return self.date.weekday()

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

    def endOfMonth(self):
        """Return the Date that is last in this month."""
        return Date(datetime.date(self.year, self.month, self.daysInMonth()))

    # bump functions
    def addOneYear(self, sign=1):
        """Return a new Date that is 1Y ahead of this date."""
        # adjust for leap day
        if abs(sign) != 1:
            raise ValueError('Date.addOneYear: sign must be +/-1')
        day = self.day if not self.isLeapDay() else 28
        return Date(datetime.date(self.year + sign, self.month, day))

    def addMonths(self, months, eom_rule):
        """Return a new Date that is months ahead/behind this date."""
        year = self.year
        month = self.month + months

        while month > 12:
            year += 1
            month -= 12

        while month < 1:
            year -= 1
            month += 12
        
        # Use eom_rule to determine day number.
        day = min(self.day, Date.class_daysInMonth(month, year))
        if eom_rule == EomRule.LAST:
            if self.day == Date.class_daysInMonth(self.month, self.year):
                # stay at end of shifted month
                day = Date.class_daysInMonth(month, year)
        
        return Date(datetime.date(year, month, day))

    def addDays(self, days):
        """Return a new Date that is days ahead of this date."""
        return Date(self.date + datetime.timedelta(days=days))

    def addTenor(self, tenor, eom_rule=EomRule.LAST):
        """Return a new Date that is tenor ahead of this date."""
        tenor = Tenor(tenor)
        date_frequency = DateFrequency.tenor_unit_to_frequency(tenor.unit)
        direction = BumpDirection.FORWARD if tenor.size >=0 else BumpDirection.BACKWARD
        iterations = abs(tenor.size)
        shifted_date = self
        for _ in range(iterations):
            shifted_date = shifted_date.shiftDate(date_frequency, direction, eom_rule)
        return shifted_date

    def shiftDate(self, date_frequency, bump_direction, eom_rule=EomRule.LAST):
        """Return a new Date that is ahead/behind this date by the date_frequency."""
        sign = 1 if bump_direction == BumpDirection.FORWARD else -1

        if date_frequency == DateFrequency.DAILY:
            return self.addDays(sign)
        if date_frequency == DateFrequency.WEEKLY:
            return self.addDays(sign * 7)
        if date_frequency == DateFrequency.MONTHLY:
            return self.addMonths(sign, eom_rule)
        if date_frequency == DateFrequency.QUARTERLY:
            return self.addMonths(sign * 3, eom_rule)
        if date_frequency == DateFrequency.SEMIANNUALLY:
            return self.addMonths(sign * 6, eom_rule)
        if date_frequency == DateFrequency.YEARLY:
            return self.addOneYear(sign)

    def isMonthBefore(self, rhs):
        """Return True if this is in the month before the rhs, else False."""
        if not isinstance(rhs, Date):
            rhs = Date(rhs)
        return ((self.year == rhs.year) and (self.month == rhs.month - 1)) or \
                ((self.year == rhs.year - 1) and (self.month == 12) and (rhs.month == 1))

class DateTime(object):
    # wraps datetime.datetime but allows conversion from string types in constructor
    def __init__(self, dt):

        if isinstance(dt, DateTime):
            self.datetime = dt.datetime
        elif isinstance(dt, datetime.datetime):
            self.datetime = dt
        else:
            dt = str(dt)

            supported_formats = [
                '%Y%m%d%H%M%S',         # 20220401170435
                '%Y-%m-%d %H:%M:%S',    # 2022-04-01 17:04:35
                '%Y-%m-%d %H:%M:%S.%f', # 2022-04-01 17:04:35.987654
                '%H:%M:%S %d %b %Y',    # 17:04:35 01 Apr 2022
                # Date formats
                '%Y-%m-%d', # 2022-04-01
                '%Y%m%d',   # 20220401
                '%Y-%m',    # 2022-04
                '%Y %b',    # 2022 Apr
                '%d %b %Y', # 01 Apr 2022
                '%d-%b-%Y'  # 01-Apr-2022
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
        return self.datetime.strftime('%Y-%m-%dT%H:%M:%S')

    # use self.datetime to access the underlying datetime.datetime

    def get_date(self):
        return Date(self.datetime.strftime('%Y-%m-%d'))


class Tenor(object):
    def __init__(self, tenor_str):
        tenor = str(tenor_str).upper()
        if not (tenor.endswith('Y') or tenor.endswith('M') or tenor.endswith('D')):
            raise ValueError(f'Tenor expected to end with Y, M, D but got {tenor_str}')

        size = tenor[:-1]
        if not (size.isnumeric() or (size.startswith('-') and size[1:].isnumeric())):
            raise ValueError(f'Tenor expected to start with number but got {tenor_str}')

        self.tenor = tenor
        self.unit = tenor[-1]
        self.size = int(size)

    def __repr__(self):
        return self.tenor


def day_count_fraction(start_date, end_date, day_count):
    # pre-condition start_date and end_date are of type Date
    if day_count == DayCount.ACT_365:
        return (end_date - start_date).days / 365.0
    else:
        raise NotImplementedError(f'day_count_fraction for {day_count} is not implemented.')

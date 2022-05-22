
import datetime

class Date(object):
    # wraps datetime.date but allows conversion from string types in constructor
    def __init__(self, date):

        if isinstance(date, str):
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

        if not isinstance(date, datetime.date):
            raise TypeError('Input to Date is wrong type.')

        self.date = date

    
    def __repr__(self):
        return str(self.date)

    # datetime.date API
    def year(self):
        return self.date.year

    def month(self):
        return self.date.month

    def day(self):
        return self.date.day

    def datetime_date(self):
        return self.date

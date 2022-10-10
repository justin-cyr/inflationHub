
import heapq
from collections import defaultdict

from ..utils import Date, day_count_fraction

class Cashflows(object):
    def __init__(self, payment_dates, amounts):
        # default implementation is fixed amount on each payment date
        try:
            payment_dates = list(payment_dates)
            amounts = list(amounts)
        except Exception as e:
            raise ValueError(f'Cashflows: payment_dates and amounts must be list-like types, {e}')

        if len(payment_dates) != len(amounts):
            raise ValueError(f'Cashflows: len(payment_dates)={len(payment_dates)} and len(amounts)={len(amounts)} don\'t match.')
        
        try:
            payment_date_objs = [Date(d) for d in payment_dates]
        except Exception as e:
            raise ValueError(f'Cashflows: payment_dates cannot be converted to Date type, {e}')

        sorted_cashflows = sorted(zip(payment_date_objs, amounts), key=lambda pair: pair[0])
        self.payment_dates = [pair[0] for pair in sorted_cashflows]
        self.amount_map = {d: a for d, a in sorted_cashflows}

    def __repr__(self):
        return f'Cashflows({self.schedule()})'

    def schedule(self):
        """Return a list of dicts with contractual cashflow info."""
        this_schedule = []
        for d in self.payment_dates:
            record = {
                'payment_date': str(d),
                'type': 'Cashflow'
            }
            if 'amount_map' in self.__dict__:
                record['amount'] = self.amount_map[d]
            this_schedule.append(record)
        return this_schedule

    # decorator
    def check_payment_dates(init):
        def inner(self, payment_dates, *args, **kwargs):
            try:
                payment_dates = list(payment_dates)
            except Exception as e:
                raise ValueError(f'Cashflows: payment_dates must be list-like types, {e}')
            return init(self, list(payment_dates), *args, **kwargs)
        return inner

    def amount_calc(self, d):
        # override in inherited classes
        return self.amount_map.get(Date(d), 0.0)

    def amount(self, d):
        return self.amount_calc(d)


class MultiLegCashflows(Cashflows):
    # Merge multiple cashflow objects together
    def __init__(self, cashflows_list):
        self.legs = cashflows_list

        payment_dates, merged_schedule = self.merge_legs()
        self.payment_dates = [Date(d) for d in payment_dates]
        self.merged_schedule = merged_schedule

        self.nonzero_leg_map = defaultdict(list)
        for record in self.merged_schedule:
            self.nonzero_leg_map[record['payment_date']].append(record['leg_index'])

    def __repr__(self):
        return f'MergedCashflows({self.schedule()})'

    def schedule(self):
        return self.merged_schedule
    
    def merge_legs(self):
        """Merge schedules and payment dates of legs."""
        schedules = [cf.schedule() for cf in self.legs]
        for i, sched in enumerate(schedules):
            for record in sched:
                record['leg_index'] = i

        merged_schedule = list(heapq.merge(*schedules, key=lambda r: r['payment_date']))
        payment_dates = [merged_schedule[0]['payment_date']] if merged_schedule else []
        for record in merged_schedule[1:]:
            if record['payment_date'] > payment_dates[-1]:
                payment_dates.append(record['payment_date'])
        
        return payment_dates, merged_schedule

    def amount(self, d):
        raise NotImplementedError('MultiLegCashflows do not implement an incomplete amount function.')


class PrincipalCashflows(Cashflows):
    def __init__(self, last_payment_date, principal_amount):
        super().__init__([last_payment_date], [principal_amount])
    
    def __repr__(self):
        return f'PrincipalCashflows({self.schedule()})'

    def schedule(self):
        base_schedule = super().schedule()
        this_schedule = []
        for record in base_schedule:
            record['type'] = 'PrincipalCashflow'
            this_schedule.append(record)
        return this_schedule


class CouponCashflows(Cashflows):
    @Cashflows.check_payment_dates
    def __init__(self, payment_dates, notional, dcfs=None, period_dates=None, day_count=None):
        if not dcfs:
            # calculate day count fractions from period start and end dates
            if not (period_dates and day_count):
                raise ValueError('CouponCashflow: period start/end dates and day count must be provided if day count fractions are not provided.')

            # expect period_dates to be a list of pairs [(start_date, end_date)]
            if not isinstance(period_dates, list):
                raise ValueError('CouponCashflows: period_dates must be list type.')

            dcfs = []
            for start_date, end_date in period_dates:
                dcf = day_count_fraction(start_date, end_date, day_count)
                if dcf < 0.0:
                    raise ValueError(f'CouponCashflows: invalid period_dates, start date={start_date} exceeds end date={end_date}.')
                dcfs.append(dcf)

            self.day_count = day_count

        if len(dcfs) != len(payment_dates):
            raise ValueError(f'CouponCashflows: len(dcfs)={len(dcfs) } must equal len(payment_dates)={len(payment_dates)}.')
        
        try:
            payment_date_objs = [Date(d) for d in payment_dates]
        except Exception as e:
            raise ValueError(f'CouponCashflows: payment_dates cannot be converted to Date type, {e}')

        if period_dates:
            sorted_schedule = sorted(zip(payment_date_objs, dcfs, period_dates), key=lambda pair: pair[0])
            period_dates = [pair[2] for pair in sorted_schedule]
            self.period_dates = period_dates
        else:
            sorted_schedule = sorted(zip(payment_date_objs, dcfs), key=lambda pair: pair[0])
        self.payment_dates = [pair[0] for pair in sorted_schedule]
        self.dcf_map = {pair[0]: pair[1] for pair in sorted_schedule}
        self.notional = notional

    def __repr__(self):
        return f'CouponCashflows({self.schedule()})'

    def schedule(self):
        base_schedule = super().schedule()
        this_schedule = []
        for i, record in enumerate(base_schedule):
            record['type'] = 'CouponCashflow'
            record['notional'] = self.notional
            record['day_count_fraction'] = self.dcf_map[record['payment_date']]
            if 'day_count' in self.__dict__:
                record['day_count'] = str(self.day_count)
            if 'period_dates' in self.__dict__:
                record['start_date'] = str(self.period_dates[i][0])
                record['end_date'] = str(self.period_dates[i][1])
            this_schedule.append(record)
        return this_schedule

    def amount_calc(self, dcf, rate):
        return rate * dcf * self.notional

    def amount(self, d, rate):
        if d not in self.dcf_map:
            return 0.0
        else:
            return self.amount_calc(self.dcf_map[d], rate)


class FixedCouponCashflows(CouponCashflows):
    def __init__(self, payment_dates, notional, rate, dcfs=None, period_dates=None, day_count=None):
        super().__init__(payment_dates, notional, dcfs, period_dates, day_count)
        self.rate = rate

    def __repr__(self):
        return f'FixedCouponCashflows({self.schedule()})'

    def schedule(self):
        base_schedule = super().schedule()
        this_schedule = []
        for record in base_schedule:
            record['type'] = 'FixedCouponCashflow'
            record['rate'] = self.rate
            record['amount'] = self.amount(record['payment_date'])
            this_schedule.append(record)
        return this_schedule

    def amount(self, d):
        return super().amount(d, self.rate)

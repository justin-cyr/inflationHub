
from .calendar import CalendarUtil
from ..utils import Date, BumpDirection, DateFrequency, DayCount, day_count_fraction

# A CouponSchedule is a collection of lists of ascending coupon and payment Dates generated using some rule.
class CouponSchedule(object):
    def __init__(self,
                unadj_start_date,
                unadj_end_date,
                payment_frequency,
                direction=BumpDirection.BACKWARD,
                coupon_calendars=[],
                payment_days=0,
                payment_calendars=[],
                pay_dates_relative_to_adj=False,
                force_start_and_end=False
            ):
        # start of first coupon period and end of last coupon period
        self.unadj_start_date = Date(unadj_start_date)
        self.unadj_end_date = Date(unadj_end_date)

        self.coupon_calendars = coupon_calendars
        self.payment_days = payment_days
        self.payment_calendars = payment_calendars

        self.payment_frequency = DateFrequency.from_str(payment_frequency)
        self.direction = BumpDirection.from_str(direction)
        self.pay_dates_relative_to_adj = pay_dates_relative_to_adj
        self.force_start_and_end = force_start_and_end

        self.unadj_start_dates = []
        self.unadj_end_dates = []
        self.adj_start_dates = []
        self.adj_end_dates = []
        self.payment_dates = []

        # Generate unadjusted dates using frequency, no calendars
        if self.direction == BumpDirection.FORWARD:
            s_date = self.unadj_start_date
            e_date = s_date.shiftDate(self.payment_frequency, self.direction)

            # Use inputs if shift is too large
            if e_date > self.unadj_end_date:
                self.unadj_start_dates.append(s_date)
                self.unadj_end_dates.append(self.unadj_end_date)

            while e_date <= self.unadj_end_date:
                self.unadj_start_dates.append(s_date)
                self.unadj_end_dates.append(e_date)
                s_date = e_date
                e_date = s_date.shiftDate(self.payment_frequency, self.direction)

            # Force end date
            if self.force_start_and_end:
                self.unadj_end_dates[-1] = self.unadj_end_date

        elif self.direction == BumpDirection.BACKWARD:
            e_date = self.unadj_end_date
            s_date = e_date.shiftDate(self.payment_frequency, self.direction)

            # Use inputs if shift is too large
            if s_date < self.unadj_start_date:
                self.unadj_end_dates.append(e_date)
                self.unadj_start_dates.append(self.unadj_start_date)

            while s_date >= self.unadj_start_date:
                self.unadj_end_dates.append(e_date)
                self.unadj_start_dates.append(s_date)
                e_date = s_date
                s_date = e_date.shiftDate(self.payment_frequency, self.direction)

            # Force end date
            if self.force_start_and_end:
                self.unadj_start_dates[0] = self.unadj_start_date

            # reverse order from backward generation
            self.unadj_start_dates.reverse()
            self.unadj_end_dates.reverse()
        else:
            raise ValueError(f'CouponSchedule: unsupported bump direction {self.direction}.')

        # Adjust dates using coupon calendar
        self.adj_start_dates.append(CalendarUtil.nearest_business_day(
                                                self.coupon_calendars,
                                                self.unadj_start_dates[0]
                                            ))
        self.adj_end_dates.append(CalendarUtil.nearest_business_day(
                                                self.coupon_calendars,
                                                self.unadj_end_dates[0]
                                            ))
        for i, e_date in enumerate(self.unadj_end_dates[1:]):
            adj_e_date = CalendarUtil.nearest_business_day(
                                                self.coupon_calendars,
                                                e_date
                                            )
            # i is index of e_date minus 1
            self.adj_start_dates.append(self.adj_end_dates[i])
            self.adj_end_dates.append(adj_e_date)

        # Generate payment dates
        end_dates = self.adj_end_dates if pay_dates_relative_to_adj else self.unadj_end_dates
        for e_date in end_dates:
            pay_date = CalendarUtil.add_business_days(
                                        self.payment_calendars,
                                        e_date,
                                        self.payment_days
                                    )
            self.payment_dates.append(pay_date)

        
    def __repr__(self):
        return f'CouponSchedule({self.__dict__})'

    def get_period_dates(self):
        """Return adj start and end dates as a list of tuples."""
        return list(zip(self.adj_start_dates, self.adj_end_dates))

    def get_dcfs(self, day_count):
        return [day_count_fraction(s_date, e_date, day_count) for s_date, e_date in self.get_period_dates()]

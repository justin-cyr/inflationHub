
from ast import Yield
from backend.products.cashflows import Cashflows, FixedCouponCashflows, MultiLegCashflows, PrincipalCashflows
from backend.products.projectedcashflows import ProjectedCashflows
from ..utils import BumpDirection, Date, DateFrequency, DayCount, StrEnum, YieldConvention
from ..utilities.calendar import CalendarUtil
from ..utilities.couponschedule import CouponSchedule

from enum import auto
import os
import pandas as pd

# Read Bonds.csv
BOND_CONFIG = pd.read_csv(
                os.path.join(os.getcwd(), 'backend/products/ProductConventions/Bonds.csv'),
                index_col='Convention',
                keep_default_na=False
            ).to_dict(orient='index')

class CouponConvention(StrEnum):
        UNIFORM = auto()
        ADJ_DATE_DCF = auto()

        @classmethod
        def uniform_weight(cls, date_frequency):
            uniform_weights = {
                DateFrequency.YEARLY:       1.0,
                DateFrequency.SEMIANNUALLY: 0.50,
                DateFrequency.QUARTERLY:    0.25,
                DateFrequency.MONTHLY:      1.0 / 12.0,
                DateFrequency.WEEKLY:       1.0 / 52.0,
                DateFrequency.DAILY:        1.0 / 365.0
            }
            if date_frequency not in uniform_weights:
                raise ValueError(f'CouponConvention.uniform_weight: unsupported date frequency {date_frequency}.')
            return uniform_weights[date_frequency]

class Bond(object):
    def __init__(self,
            notional,
            maturity_date,
            settlement_days=0,
            settlement_calendars=[],
            payment_days=0,
            payment_calendars=[]
        ):
        CalendarUtil.check_calendar_names(settlement_calendars)
        CalendarUtil.check_calendar_names(payment_calendars)

        self.bond_type = self.__class__.__name__
        self.notional = float(notional)
        self.settlement_days = int(settlement_days)
        self.maturity_date = Date(maturity_date)
        self.settlement_calendars = list(settlement_calendars)
        self.payment_days = int(payment_days)
        self.payment_calendars = list(payment_calendars)
        self.last_payment_date = CalendarUtil.add_business_days(self.payment_calendars, self.maturity_date, self.payment_days)
        self.principal_flows = PrincipalCashflows(self.last_payment_date, self.notional)

        # defined in derived classes
        self.is_fixed = None
        self.coupon_flows = None
        self.cashflows = None

    
    @staticmethod
    def create_bond(**kwargs):
        """Construct a Bond object from a data convention and parameters dictionary."""
        # universal parameters passed in kwargs
        notional = kwargs.get('notional')
        maturity_date = kwargs.get('maturity_date')

        # optional parameters passed in kwargs
        dated_date = kwargs.get('dated_date')
        rate = kwargs.get('rate')

        # optional parameters in kwargs or Bonds.csv
        if 'Convention' not in kwargs:
            # get optional parameters from kwargs
            bond_type = kwargs.get('bond_type')
            settlement_days = kwargs.get('settlement_days')
            settlement_calendars = kwargs.get('settlement_calendars')
            payment_days = kwargs.get('PaymentDays', 0)
            payment_calendars = kwargs.get('payment_calendars')
            payment_frequency = kwargs.get('payment_frequency')
            day_count = kwargs.get('day_count')
            coupon_convention = kwargs.get('coupon_convention')
            accrued_interest_day_count = kwargs.get('accrued_interest_day_count')
            yield_convention = kwargs.get('yield_convention')
        
        else:
            # get optional parameters from Bonds.csv
            name = kwargs['Convention']
            if name not in BOND_CONFIG:
                raise KeyError(f'Bond.create_bond: Convention={name} not found in Bonds.csv.')
            bond_conventions = BOND_CONFIG[name]

            bond_type = bond_conventions.get('Type')
            settlement_days = bond_conventions.get('SettlementDays', 0)
            settlement_calendars_str = bond_conventions.get('SettlementCalendars')
            settlement_calendars = CalendarUtil.split_calendars(settlement_calendars_str)
            payment_days = bond_conventions.get('PaymentDays', 0)
            payment_calendars_str = bond_conventions.get('PaymentCalendars')
            payment_calendars = CalendarUtil.split_calendars(payment_calendars_str)
            payment_frequency = bond_conventions.get('PaymentFrequency')
            day_count = bond_conventions.get('CouponDayCount')
            coupon_convention = bond_conventions.get('CouponConvention')
            accrued_interest_day_count = bond_conventions.get('AccruedInterestDayCount')
            yield_convention = bond_conventions.get('YieldConvention')

        # Convert types of optional arguments
        coupon_convention = CouponConvention.from_str(coupon_convention) if coupon_convention else None
        payment_frequency = DateFrequency.from_str(payment_frequency) if payment_frequency else None
        day_count = DayCount.from_str(day_count) if day_count else None
        accrued_interest_day_count = DayCount.from_str(accrued_interest_day_count) if accrued_interest_day_count else None
        yield_convention = YieldConvention.from_str(yield_convention)

        # Delegate to constructor based on type
        if bond_type == ZeroCouponBond.__name__:
            return ZeroCouponBond(notional, maturity_date, payment_days, payment_calendars)
        elif bond_type == FixedRateBond.__name__:
            return FixedRateBond(
                    notional,
                    maturity_date,
                    dated_date,
                    rate,
                    payment_frequency,
                    coupon_convention,
                    yield_convention,
                    accrued_interest_day_count,
                    settlement_days,
                    settlement_calendars,
                    payment_days,
                    payment_calendars,
                    day_count
                    )
        else:
            raise NotImplementedError(f'Bond.create_bond: does not support bond type {bond_type}.')


    def __repr__(self):
        return str(self.__dict__)

    def schedule(self):
        if isinstance(self.cashflows, Cashflows):
            return self.cashflows.schedule()
        else:
            return []

    def get_settlement_date(self, base_date):
        settlement_date = CalendarUtil.add_business_days(
            self.settlement_calendars,
            base_date,
            self.settlement_days
        )
        return settlement_date

    def get_projected_cashflows(self, base_date=Date.today()):
        if self.is_fixed and isinstance(self.cashflows, MultiLegCashflows):
            projection_function = [None for _ in self.cashflows.legs]
            if self.__dict__.get('yield_convention') == YieldConvention.US_STREET and isinstance(self, FixedRateBond):
                settlement_date = self.get_settlement_date(base_date)
                return ProjectedCashflows(
                        self.cashflows,
                        projection_function,
                        base_date,
                        yield_convention=self.yield_convention,
                        periods_per_year=self.periods_per_year,
                        coupon_frac=1.0 - self.next_coupon_frac(settlement_date)
                    )
            else:
                return ProjectedCashflows(
                        self.cashflows,
                        projection_function,
                        base_date
                    )
        else:
            raise NotImplementedError('Bond.get_projected_cashflows - default implementation only for fixed cashflows.')
    
    def pv_to_yield(self, pv, base_date=Date.today()):
        projected_cashflows = self.get_projected_cashflows(base_date)
        return projected_cashflows.pv_to_yield(pv)

    def accrued_interest_per_100(self, base_date=Date.today()):
        raise NotImplementedError('Bond.accured_interest - not implemented in base Bond class.')
    
    def accrued_interest(self, base_date=Date.today()):
        ai_per_100 = self.accrued_interest_per_100(base_date)
        ai = self.notional * ai_per_100 / 100.0
        return ai

    def pv_to_dirty_price(self, pv):
        return (pv / self.notional) * 100.0

    def pv_to_clean_price(self, pv):
        dirty_price = self.pv_to_dirty_price(pv)
        return self.dirty_price_to_clean_price(dirty_price)

    def clean_price_to_dirty_price(self, clean_price, base_date=Date.today()):
        ai_per_100 = self.accrued_interest_per_100(base_date)
        return clean_price + ai_per_100

    def dirty_price_to_clean_price(self, dirty_price, base_date=Date.today()):
        ai_per_100 = self.accrued_interest_per_100(base_date)
        return dirty_price - ai_per_100

    def clean_price_to_market_value(self, clean_price, base_date=Date.today()):
        dirty_price = self.clean_price_to_dirty_price(clean_price, base_date)
        market_value = self.notional * dirty_price / 100.0
        return market_value

    def clean_price_to_yield(self, clean_price, base_date=Date.today()):
        market_value = self.clean_price_to_market_value(clean_price, base_date)
        return self.pv_to_yield(market_value)

    def yield_to_pv(self, y, base_date=Date.today()):
        projected_cashflows = self.get_projected_cashflows(base_date)
        pv = projected_cashflows.yield_to_pv(y)
        return pv

    def yield_to_dirty_price(self, y, base_date=Date.today()):
        pv = self.yield_to_pv(y, base_date)
        dirty_price = self.pv_to_dirty_price(pv)
        return dirty_price

    def yield_to_clean_price(self, y, base_date=Date.today()):
        dirty_price = self.yield_to_dirty_price(y, base_date)
        return self.dirty_price_to_clean_price(dirty_price, base_date)

    # Decorator
    def require_yield_or_clean_price(calc):
        def inner(self, base_date=Date.today(), *, ytm=None, clean_price=None):
            # use yield if provided
            if isinstance(ytm, float):
                return calc(self, base_date, ytm=ytm)
            elif isinstance(clean_price, float):
                return calc(self, base_date, clean_price=clean_price)
            else:
                raise ValueError(f'Bond.{calc.__name__} requires at least one of ytm or clean_price.')
        return inner

    # Measures of price sensitivity and convexity
    def ytm_for_calc(self, base_date=Date.today(), ytm=None, clean_price=None):
        if not ytm:
            ytm = self.clean_price_to_yield(clean_price, base_date)
        return ytm

    @require_yield_or_clean_price
    def yield_dv01(self, base_date=Date.today(), *, ytm=None, clean_price=None):
        projected_cashflows = self.get_projected_cashflows(base_date)
        ytm = self.ytm_for_calc(base_date, ytm, clean_price)
        return projected_cashflows.yield_dv01(ytm)

    @require_yield_or_clean_price
    def modified_duration(self, base_date=Date.today(), *, ytm=None, clean_price=None):
        projected_cashflows = self.get_projected_cashflows(base_date)
        ytm = self.ytm_for_calc(base_date, ytm, clean_price)
        return projected_cashflows.modified_duration(ytm)
    
    @require_yield_or_clean_price
    def macauley_duration(self, base_date=Date.today(), *, ytm=None, clean_price=None):
        projected_cashflows = self.get_projected_cashflows(base_date)
        ytm = self.ytm_for_calc(base_date, ytm, clean_price)
        return projected_cashflows.macauley_duration(ytm)

    @require_yield_or_clean_price
    def convexity(self, base_date=Date.today(), *, ytm=None, clean_price=None):
        projected_cashflows = self.get_projected_cashflows(base_date)
        ytm = self.ytm_for_calc(base_date, ytm, clean_price)
        return projected_cashflows.convexity(ytm)


class ZeroCouponBond(Bond):
    def __init__(self, notional, maturity_date, payment_days=0, payment_calendars=[]):
        super().__init__(notional, maturity_date, payment_days=payment_days, payment_calendars=payment_calendars)
        self.is_fixed = True
        self.cashflows = MultiLegCashflows([self.principal_flows])
        
    def accrued_interest_per_100(self, base_date=Date.today()):
        return 0.0


class FixedRateBond(Bond):
    def __init__(self,
            notional,
            maturity_date,
            dated_date,
            rate,
            payment_frequency,
            coupon_convention,
            yield_convention,
            accrued_interest_day_count,
            settlement_days=0,
            settlement_calendars=[],
            payment_days=0,
            payment_calendars=[],
            day_count=None
        ):
        super().__init__(
            notional,
            maturity_date,
            settlement_days=settlement_days,
            settlement_calendars=settlement_calendars,
            payment_days=payment_days,
            payment_calendars=payment_calendars
        )

        required_arguments = {
            'rate': rate,
            'dated_date': dated_date,
            'coupon_convention': coupon_convention,
            'payment_frequency': payment_frequency,
            'yield_convention': yield_convention,
            'accrued_interest_day_count': accrued_interest_day_count
        }

        for name, val in required_arguments.items():
            if val is None:
                raise ValueError(f'FixedRateBond: requires argument {name}.')

        self.rate = float(rate)
        self.dated_date = Date(dated_date)
        self.coupon_convention = coupon_convention
        self.payment_frequency = payment_frequency
        self.yield_convention = yield_convention
        self.accrued_interest_day_count = accrued_interest_day_count

        # day_count is required unless coupon_convention=UNIFORM
        if day_count is None and self.coupon_convention != CouponConvention.UNIFORM:
            raise ValueError(f'FixedRateBond: requires day_count when coupon_convention is not uniform.')
        self.day_count = day_count

        if self.coupon_convention == CouponConvention.UNIFORM:
            self.periods_per_year = self.payment_frequency.periods_per_year()
        else:
            self.periods_per_year = None

        # Create coupon cashflows
        self.coupon_schedule = CouponSchedule(
            self.dated_date,
            self.maturity_date,
            self.payment_frequency,
            direction=BumpDirection.BACKWARD,
            coupon_calendars=self.payment_calendars,
            payment_days=self.payment_days,
            payment_calendars=self.payment_calendars,
            pay_dates_relative_to_adj=False,
            force_start_and_end=False
        )

        # Determine coupon day count fractions
        if self.coupon_convention == CouponConvention.UNIFORM:
            coupon_dcf = CouponConvention.uniform_weight(self.payment_frequency)
            dcfs = [coupon_dcf for _ in self.coupon_schedule.adj_start_dates] 
        elif self.coupon_convention == CouponConvention.ADJ_DATE_DCF:
            dcfs = self.coupon_schedule.get_dcfs(self.day_count)
        else:
            raise ValueError(f'FixedRateBond: unsupported coupon convention {self.coupon_convention}.')

        self.dcfs = dcfs
        self.is_fixed = True
        self.coupon_flows = FixedCouponCashflows(
            self.coupon_schedule.payment_dates,
            self.notional,
            self.rate,
            dcfs,
            self.coupon_schedule.get_period_dates(),
            day_count=self.day_count if self.coupon_convention != CouponConvention.UNIFORM else None
        )
        self.cashflows = MultiLegCashflows([self.coupon_flows, self.principal_flows])

    def next_coupon_frac(self, settlement_date):
        """Return the coupon_frac for the next coupon period."""
        settlement_date = Date(settlement_date)
        i = self.coupon_schedule.coupon_period(settlement_date)
        if i < 0 or i >= len(self.dcfs):
            return 0.0
        s_date, e_date = self.coupon_schedule.unadj_start_dates[i], self.coupon_schedule.unadj_end_dates[i]
        return self.coupon_frac(s_date, e_date, settlement_date)

    def coupon_frac(self, s_date, e_date, settlement_date):
        # Return fraction of time from start of current coupon period to end.
        s_date = Date(s_date)
        e_date = Date(e_date)
        settlement_date = Date(settlement_date)
        if self.accrued_interest_day_count == DayCount.ACT_ACT:
            return (settlement_date - s_date).days / (e_date - s_date).days
        else:
            raise NotImplementedError(f'{self.__class__.__name__}.coupon_frac: does not support AccruedInterestDayCount={self.accrued_interest_day_count}.')

    def accrued_interest_per_100(self, base_date=Date.today()):
        # find partial coupon period
        settlement_date = self.get_settlement_date(base_date)
        i = self.coupon_schedule.coupon_period(settlement_date)
        if i < 0 or i >= len(self.dcfs):
            return 0.0
        s_date, e_date = self.coupon_schedule.unadj_start_dates[i], self.coupon_schedule.unadj_end_dates[i]
        ai = 100.0 * (self.rate * self.dcfs[i]) * self.coupon_frac(s_date, e_date, settlement_date)
        
        return ai

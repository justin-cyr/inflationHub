
from backend.products.cashflows import Cashflows, MultiLegCashflows, PrincipalCashflows
from backend.products.projectedcashflows import ProjectedCashflows
from ..utils import Date
from ..utilities.calendar import CalendarUtil

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

        self.notional = float(notional)
        self.settlement_days = int(settlement_days)
        self.maturity_date = Date(maturity_date)
        self.settlement_calendars = list(settlement_calendars)
        self.last_payment_date = CalendarUtil.add_business_days(payment_calendars, self.maturity_date, payment_days)
        self.principal_flows = PrincipalCashflows(self.last_payment_date, self.notional)

        # defined in derived classes
        self.is_fixed = None
        self.coupon_flows = None
        self.cashflows = None

    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

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
            return ProjectedCashflows(self.cashflows, projection_function, base_date)
        else:
            raise NotImplementedError('Bond.get_projected_cashflows - default implementation only for fixed cashflows.')
    
    def pv_to_yield(self, pv, base_date=Date.today()):
        projected_cashflows = self.get_projected_cashflows(base_date)
        return projected_cashflows.pvToYield(pv)

    def accrued_interest_per_100(self, base_date=Date.today()):
        raise NotImplementedError('Bond.accured_interest - not implemented in base Bond class.')
    
    def accrued_interest(self, base_date=Date.today()):
        settlement_date = self.get_settlement_date(base_date)
        ai_per_100 = self.accrued_interest_per_100(settlement_date)
        ai = self.notional * ai_per_100 / 100.0
        return ai

    def pv_to_dirty_price(self, pv):
        return (pv / self.notional) * 100.0

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

    def yield_to_dirty_price(self, y, base_date=Date.today()):
        projected_cashflows = self.get_projected_cashflows(base_date)
        pv = projected_cashflows.yieldToPv(y)
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

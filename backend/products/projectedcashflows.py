
from ..utils import Date, DayCount, day_count_fraction
from .cashflows import Cashflows, MultiLegCashflows

class ProjectedCashflows(object):
    def __init__(self, cashflows, projection_function=None, base_date=Date.today(), day_count=DayCount.ACT_365):
        # projection_function can be None for cashflows with no unknown parameters.
        if not isinstance(cashflows, Cashflows):
            raise ValueError('ProjectedCashflows: cashflows must be type Cashflows.')

        if isinstance(cashflows, MultiLegCashflows):
            if not (isinstance(projection_function, list) and all([not f or callable(f) for f in projection_function])):
                raise ValueError('ProjectedCashflows: projection_function must be a list of functions for MultiLegCashflows.')
        elif projection_function and not callable(projection_function):
                raise ValueError('ProjectedCashflows: projection_function must be a function.')
        
        self.contractual_cashflows = cashflows
        self.proj = projection_function
        self.base_date = base_date
        self.day_count = day_count
        self.projected_leg_amounts = [self.projected_amounts_by_leg(d) for d in self.contractual_cashflows.payment_dates]
        self.projected_amounts = [sum(amts) for amts in self.projected_leg_amounts]
        self.payment_times = self.cashflow_times(base_date, day_count)

    def __repr__(self):
        return f'ProjectedCashflows({self.__dict__})'

    def schedule(self):
        contractual_schedule = self.contractual_cashflows.schedule()
        projected_schedule = []
        for i, record in enumerate(contractual_schedule):
            record['type'] = 'Projected' + record['type']
            record['projected_amount'] = self.projected_leg_amounts[i][record.get('leg_index', 0)]
            record['payment_time'] = self.payment_times[i]
            projected_schedule.append(record)
        return projected_schedule

    def projected_amount(self, d):
        if Date(d) < self.base_date:
            return 0.0

        try:
            if self.proj:
                res = self.contractual_cashflows.amount(d, *self.proj(d))
            else:
                res = self.contractual_cashflows.amount(d)
        except Exception as e:
                raise Exception(f'ProjectedCashflows: cannot project on date {d}, {e}.')
        
        return res

    def projected_amounts_by_leg(self, d):
        # Projected amount for each leg in a MultiLegCashflow
        if not isinstance(self.contractual_cashflows, MultiLegCashflows):
            return [self.projected_amount(d)]
        
        res = [0.0 for _ in self.contractual_cashflows.legs]
        if Date(d) < self.base_date:
            return res
        
        for j in self.contractual_cashflows.nonzero_leg_map.get(d, []):
            # just project the parameters needed on date d
            proj_j = self.proj[j]
            try:
                if proj_j:
                    res[j] = self.contractual_cashflows.legs[j].amount(d, *proj_j(d))
                else:
                    res[j] = self.contractual_cashflows.legs[j].amount(d)
            except Exception as e:
                raise Exception(f'ProjectedCashflows: cannot project on date {d} for leg {j}, {e}.')
        
        return res

    def cashflow_times(self, base_date, day_count):
        """Return list of cashflow times in years."""
        return [day_count_fraction(base_date, payment_date, day_count)
                for payment_date in self.contractual_cashflows.payment_dates]

    # decorator
    def check_payment_times_override(func):
        def inner(self, *args, **kwargs):
            payment_times = kwargs.get('payment_times')
            if payment_times:
                len_payment_times_override = len(payment_times)
                len_payment_dates = len(self.contractual_cashflows.payment_dates)
                if len_payment_times_override != len_payment_dates:
                    raise ValueError(f'ProjectedCashflows: len(payment times)={len_payment_times_override} does not match len(payment dates)={len_payment_dates}.')
            else:
                kwargs['payment_times'] = self.payment_times

            return func(self, *args, **kwargs)
        return inner    

    @check_payment_times_override
    def yieldToPv(self, y, *, payment_times=None):
        """Returns the PV of a projected cashflow for a given yield to maturity."""
        pv = sum([
            a / (1.0 + y)**t
            for a, t in zip(self.projected_amounts, payment_times)
            if t >= 0.0
        ])
        return pv

    @check_payment_times_override
    def yieldToPvPrime(self, y, *, payment_times=None):
        """Returns the 1st-order derivative of the yieldToPv function."""
        return sum([
            -t * a / (1.0 + y)**(t  + 1.0)
            for a, t in zip(self.projected_amounts, payment_times)
            if t >= 0.0
        ])

    @check_payment_times_override
    def yieldToPvPrime2(self, y, *, payment_times=None):
        """Returns the 2nd-order derivative of the yieldToPv function."""
        return sum([
            t * (t + 1.0) * a / (1.0 + y)**(t  + 2.0)
            for a, t in zip(self.projected_amounts, payment_times)
            if t >= 0.0
        ])


    def pvToYield(self, pv, *, payment_times=None):
        """Returns the yield to maturity of the projected cashflows for a given present value."""
        from scipy.optimize import root_scalar
        if pv <= 0.0:
            raise ValueError('ProjectedCashflows.pvToYield: pv must be positive.')
        
        guess = 0.0
        def target(y):
            return (self.yieldToPv(y, payment_times=payment_times) - pv,
                    self.yieldToPvPrime(y, payment_times=payment_times),
                    self.yieldToPvPrime2(y, payment_times=payment_times)
                    )

        # First, try Halley's method (fast but doesn't guarantee convergence)
        res = root_scalar(target, fprime=True, fprime2=True, x0=guess, method='halley')
        if not res.converged:
            # Second, try a fast interval method
            bracket_exp = 2
            bracket = (-1.0 + 10 ** (-bracket_exp), 10 ** bracket_exp)
            res = root_scalar(target, fprime=True, fprime2=True, bracket=bracket, x0=guess, method='toms748')
            if not res.converged:
                print(res)
                raise Exception(f'ProjectedCashflows.pvToYield: failed to converge.')

        return res.root

    
    # Measures of price sensitivity and convexity
    def yieldDV01(self, y, payment_times=None):
        """Returns the 1st order NPV sensitivity to changes in yield per 1bp, as a function of yield.
            Normalized to be positive.
        """
        return - self.yieldToPvPrime(y, payment_times=payment_times) / 10000.0

    def modified_duration(self, y, payment_times=None):
        price = self.yieldToPv(y, payment_times=payment_times)
        return - self.yieldToPvPrime(y, payment_times=payment_times) / price

    def macauley_duration(self, y, payment_times=None):
        return (1.0 + y) * self.modified_duration(y, payment_times=payment_times)

    def convexity(self, y, payment_times=None):
        price = self.yieldToPv(y, payment_times=payment_times)
        return self.yieldToPvPrime2(y, payment_times=payment_times) / price

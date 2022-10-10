
import math

from ..utils import Date, DayCount, day_count_fraction, YieldConvention
from .cashflows import Cashflows, MultiLegCashflows

class ProjectedCashflows(object):
    def __init__(self,
                cashflows,
                projection_function=None,
                base_date=Date.today(),
                day_count=DayCount.ACT_365,
                yield_convention=YieldConvention.TRUE_YIELD,
                periods_per_year=1,
                coupon_frac=0.0
                ):
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
        self.yield_convention = yield_convention
        self.periods_per_year = periods_per_year
        self.coupon_frac = coupon_frac
        self.projected_leg_amounts = [self.projected_amounts_by_leg(d) for d in self.contractual_cashflows.payment_dates]
        self.projected_amounts = [sum(amts) for amts in self.projected_leg_amounts]
        self.payment_times = self.cashflow_times(base_date, day_count)
        self.next_payment_index = min([i for i, t in enumerate(self.payment_times) if t >= 0])

        unrealized_amounts = self.projected_amounts[self.next_payment_index:]
        if self.yield_convention == YieldConvention.TRUE_YIELD:
            payment_times = self.payment_times[self.next_payment_index:]
            self.yield_calculator = TrueYieldCalculator(unrealized_amounts, payment_times)

        elif self.yield_convention == YieldConvention.US_STREET: 
            self.yield_calculator = USStreetYieldCalculator(unrealized_amounts, self.periods_per_year, self.coupon_frac)
        
        else:
            raise ValueError(f'ProjectedCashflows: unsupported YieldConvention: {yield_convention}')


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

    def projection_factor(self, projected_params):
        """Return the product of these projected parameters."""
        if isinstance(projected_params, float):
            factor = projected_params
        elif isinstance(projected_params, list):
            factor = 1.0
            for p in projected_params:
                factor *= p
        else:
            raise ValueError(f'Projection functions must be float or list valued.')
        
        return factor

    def projected_amount(self, d):
        # pre-condition: d is of type Date
        if d < self.base_date:
            return 0.0

        try:
            if self.proj:
                factor = self.projection_factor(self.proj(d))
                res = self.contractual_cashflows.amount(d) * factor
            else:
                res = self.contractual_cashflows.amount(d)
        except Exception as e:
                raise Exception(f'ProjectedCashflows: cannot project on date {d}, {e}.')
        
        return res

    def projected_amounts_by_leg(self, d):
        # Projected amount for each leg in a MultiLegCashflow
        # precondition: d is of type Date (this function is critical for calibrating models to cashflow products)
        if not isinstance(self.contractual_cashflows, MultiLegCashflows):
            return [self.projected_amount(d)]
        
        res = [0.0 for _ in self.contractual_cashflows.legs]
        if d < self.base_date:
            return res
        
        for j in self.contractual_cashflows.nonzero_leg_map.get(d, []):
            # just project the parameters needed on date d
            proj_j = self.proj[j]
            try:
                if proj_j:
                    factor = self.projection_factor(proj_j(d))
                    res[j] = self.contractual_cashflows.legs[j].amount(d) * factor
                else:
                    res[j] = self.contractual_cashflows.legs[j].amount(d)
            except Exception as e:
                raise Exception(f'ProjectedCashflows: cannot project on date {d} for leg {j}, {e}.')
        
        return res

    def sum_projected_amounts(self):
        return sum(self.projected_amounts)

    def cashflow_times(self, base_date, day_count):
        """Return list of cashflow times in years."""
        return [day_count_fraction(base_date, payment_date, day_count)
                for payment_date in self.contractual_cashflows.payment_dates]

    def yield_to_pv(self, y):
       return self.yield_calculator.yield_to_pv(y)

    def pv_to_yield(self, pv):
        """Returns the yield to maturity of the projected cashflows for a given present value."""
        return self.yield_calculator.pv_to_yield(pv)

    # Measures of price sensitivity and convexity
    def yield_dv01(self, y):
        """Returns the 1st order NPV sensitivity to changes in yield per 1bp, as a function of yield.
            Normalized to be positive.
        """
        return self.yield_calculator.yield_dv01(y)

    def modified_duration(self, y):
        return self.yield_calculator.modified_duration(y)

    def macauley_duration(self, y):
        return self.yield_calculator.macauley_duration(y)

    def convexity(self, y):
        return self.yield_calculator.convexity(y)

    def annual_yield_to_ctsly_compounded(self, y):
        return self.yield_calculator.annual_yield_to_ctsly_compounded(y)

class YieldCalculator(object):
    """An abstract class for yield calculations for various conventions."""
    def __init__(self, fast_method='halley', bracket_method='toms748'):
        self.fast_method = fast_method
        self.bracket_method = bracket_method

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'
    
    def yield_to_pv(self, y):
        raise NotImplementedError('YieldCalculator.yield_to_pv: not implemented in base class.')
    
    def yield_to_pv_prime(self, y):
        raise NotImplementedError('YieldCalculator.yield_to_pv_prime: not implemented in base class.')

    def yield_to_pv_prime2(self, y):
        raise NotImplementedError('YieldCalculator.yield_to_pv_prime2: not implemented in base class.')

    def pv_to_yield(self, pv):
        """Returns the yield to maturity of the projected cashflows for a given present value."""
        from scipy.optimize import root_scalar        
        guess = 0.0
        def target(y):
            return (self.yield_to_pv(y) - pv,
                    self.yield_to_pv_prime(y),
                    self.yield_to_pv_prime2(y)
                    )

        # First, try fast method without guaranteed convergence
        res = root_scalar(target, fprime=True, fprime2=True, x0=guess, method=self.fast_method)
        if not res.converged:
            # Second, try a fast interval method
            bracket_exp = 2
            bracket = (-1.0 + 10 ** (-bracket_exp), 10 ** bracket_exp)
            res = root_scalar(target, fprime=True, fprime2=True, bracket=bracket, x0=guess, method=self.bracket_method)
            if not res.converged:
                print(res)
                raise Exception(f'YieldCalculator.pv_to_yield: failed to converge.')

        return res.root

    # Measures of price sensitivity and convexity
    def yield_dv01(self, y, payment_times=None):
        """Returns the 1st order NPV sensitivity to changes in yield per 1bp, as a function of yield.
            Normalized to be positive.
        """
        return - self.yield_to_pv_prime(y) / 10000.0

    def modified_duration(self, y):
        price = self.yield_to_pv(y)
        return - self.yield_to_pv_prime(y) / price

    def macauley_duration(self, y):
        return (1.0 + y) * self.modified_duration(y)

    def convexity(self, y):
        price = self.yield_to_pv(y)
        return self.yield_to_pv_prime2(y) / price
    
    def annual_yield_to_ctsly_compounded(self, y):
        raise NotImplementedError('YieldCalculator.annual_yield_to_ctsly_compounded: not implemented in base class.')

class USStreetYieldCalculator(YieldCalculator):
    def __init__(self, projected_amounts, periods_per_year, coupon_frac):
        super().__init__()
        self.projected_amounts = projected_amounts
        self.periods_per_year = periods_per_year
        self.coupon_frac = coupon_frac

    def yield_to_pv(self, y):
        pv = 0.0
        df = 1.0 / (1.0 + y / self.periods_per_year)
        accum_df = 1.0 / (1.0 + y / self.periods_per_year)**self.coupon_frac
        for a in self.projected_amounts:
            pv += a * accum_df
            accum_df *= df
        return pv
    
    def yield_to_pv_prime(self, y):
        res = 0.0
        df = 1.0 / (1.0 + y / self.periods_per_year)
        accum_df = 1.0 / (1.0 + y / self.periods_per_year)**(self.coupon_frac) / df
        for i, a in enumerate(self.projected_amounts):
            res += -(i + self.coupon_frac) * a * accum_df / self.periods_per_year
            accum_df *= df
        return res

    def yield_to_pv_prime2(self, y):
        """Returns the 1st-order derivative of the yieldToPv function."""
        res = 0.0
        df = 1.0 / (1.0 + y / self.periods_per_year)
        periods_sqd = self.periods_per_year * self.periods_per_year
        accum_df = 1.0 / (1.0 + y / self.periods_per_year)**(self.coupon_frac) / (df * df)
        for i, a in enumerate(self.projected_amounts):
            res += (i + self.coupon_frac) * (i + 1.0 + self.coupon_frac) * a * accum_df / periods_sqd
            accum_df *= df
        return res

    def macauley_duration(self, y):
        return (1.0 + y / self.periods_per_year) * self.modified_duration(y)

    def annual_yield_to_ctsly_compounded(self, y):
        return self.periods_per_year * math.log(1.0 + y / self.periods_per_year)

class TrueYieldCalculator(YieldCalculator):
    def __init__(self, projected_amounts, payment_times):
        super().__init__()
        self.projected_amounts = projected_amounts
        self.payment_times = payment_times

    def yield_to_pv(self, y):
        """Returns the PV of a projected cashflow for a given yield to maturity."""
        pv = sum([
            a / (1.0 + y)**t
            for a, t in zip(self.projected_amounts, self.payment_times)
        ])
        return pv
    
    def yield_to_pv_prime(self, y):
        """Returns the 1st-order derivative of the yieldToPv function."""
        return sum([
            -t * a / (1.0 + y)**(t + 1.0)
            for a, t in zip(self.projected_amounts, self.payment_times)
        ])

    def yield_to_pv_prime2(self, y):
        """Returns the 2nd-order derivative of the yieldToPv function."""
        return sum([
            t * (t + 1.0) * a / (1.0 + y)**(t + 2.0)
            for a, t in zip(self.projected_amounts, self.payment_times)
        ])

    def annual_yield_to_ctsly_compounded(self, y):
        return math.log(1.0 + y)

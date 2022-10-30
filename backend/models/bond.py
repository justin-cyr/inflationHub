
from .model import Model
from ..buildsettings.buildsettings import BuildSettingsBondCurve
from ..curveconstruction.curvedata import BondDataPoint
from ..curveconstruction import domains
from ..curveconstruction import convertutils as cu
from .. import config as cfg
from ..utils import Date

from ..products.bonds import Bond
from ..products.cashflows import MultiLegCashflows
from ..products.projectedcashflows import ProjectedCashflows

from collections import defaultdict, deque
import math
from scipy.optimize import minimize

# get logger from current_app instance
from flask import current_app as app

class BondModel(Model):
    def __init__(self, base_date, training_data=[], build_settings=None, calibration_tolerance=cfg.calibration_tolerance_):
        # no reference model is needed
        super().__init__(base_date, training_data, build_settings)
    
        # initialization
        self.training_data = []
        self.t0_date = self.build_settings.t0_date if self.build_settings.t0_date else base_date
        self.calibration_tolerance = calibration_tolerance
        
         # Validate build settings
        if not isinstance(self.build_settings , BuildSettingsBondCurve):
            raise ValueError(f'{self.__class__.__name__}: build settings must be type BuildSettingsBondCurve but got {self.build_settings }.')

        bond_data_points = []
        for p in self.model_data:
            if isinstance(p, BondDataPoint):
                bond_data_points.append(p.to_BondPriceAndYieldDataPoint())
            else:
                raise ValueError(f'{self.__class__.__name__}: Received unsupported curve data point {p}.')
        
        bond_data_points.sort(key=lambda p: p.bond.maturity_date)
        self.bond_data_points = bond_data_points

        # Future work: allow different node times
        self.training_times = [self.curve_time(p.bond.last_payment_date) for p in self.bond_data_points]
        self.target_pvs = [p.bond.clean_price_to_market_value(p.price, self.base_date) for p in self.bond_data_points]

        if len(self.training_times) != len(self.bond_data_points):
            raise ValueError(f'{self.__class__.__name__}: must have equal number of training times and bond points, but got {len(self.training_times)} and {len(self.bond_data_points)}, respectively.')

        if any([t <= 0.0 for t in self.training_times]):
            raise ValueError(f'{self.__class__.__name__}: training times must be strictly positive.')

        # Calibrate model
        # Use a numerical minimizer to iteratively update training data, re-fit model and
        # re-price instruments until square error to target PV is minimized.
        # - Default minimization method is BFGS.
        app.logger.info(f'Calibrating {self.__class__.__name__} using method={self.build_settings.opt_method}')
        res = minimize(
                self.calibration_objective,
                self.initial_training_data_guess(),
                method=self.build_settings.opt_method
            )
        app.logger.info(f'{self.__class__.__name__} calibration result:\n{res}')
        
        # Round-trip check - also ensures model is fit to the final iteration
        square_error = self.calibration_objective(res.x)

        if square_error >= self.calibration_tolerance:
            calibration_failure_info = []
            for p, target_pv in zip(self.bond_data_points, self.target_pvs):
                model_pv = self.pv_bond(p.bond)
                diff = target_pv - model_pv
                square_diff = diff * diff
            
                calibration_failure_info.append(dict(
                    instrument=p.label,
                    target_pv=target_pv,
                    model_pv=model_pv,
                    diff=diff,
                    square_diff=square_diff
                    )
                )
            msg = f"""{self.__class__.__name__} convergence failed to reach calibration tolerance:\n
                                    \tcalibration_tolerance: {self.calibration_tolerance},
                                    \tminimization square_error: {square_error},
                                    \tfailure info: {calibration_failure_info}.
                    """
            app.logger.error(msg)
            raise RuntimeError(msg)
        else:
            app.logger.info(f'{self.__class__.__name__} calibrated within tolerance {self.calibration_tolerance}.')
    

    def calibration_objective(self, training_values):
        """Objective function for calibration: use a training guess to fit model, price bonds, minimize error to target PVs."""
        # Insert node at time 0
        q = deque(zip(self.training_times, training_values))
        q.appendleft((0.0, 0.0))
        
        self.training_data = list(q)
        self.fit()
        print('*'*100)
        print(f'training_data = {self.training_data}')
        # price instruments and calculate difference from target
        square_error = 0.0
        for p, target_pv in zip(self.bond_data_points, self.target_pvs):
            model_pv = self.pv_bond(p.bond)
            diff = target_pv - model_pv
            square_error += diff * diff
            print(f'target_pv={target_pv}, model_pv={model_pv}, diff={diff}')
        
        print(f'square_error={square_error}')
        return square_error


    @classmethod
    def build(cls, base_date, curve_data, domainX, domainY, fitting_method_str, t0_date=None, calibration_tolerance=cfg.calibration_tolerance_, opt_method=cfg.BFGS):
         # default t0_date to base_date
        if not t0_date:
            t0_date = base_date
        build_settings = BuildSettingsBondCurve(domainX, domainY, fitting_method_str, t0_date, opt_method)
        return BondModel(base_date, curve_data, build_settings, calibration_tolerance=calibration_tolerance)
    

    def curve_time(self, date):
        """Return the time in years from the curve's t=0 date to this date."""
        return cu.time_difference(self.t0_date, date, self.build_settings.domainX)

    def initial_training_data_guess(self):
        """Return initial guess for the model's training data."""
        domainY = self.build_settings.domainY
        ctsly_compounded_yields = [p.ctsly_compounded_yield() for p in self.bond_data_points]
        
        if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
            return [t * z for t, z in zip(self.training_times, ctsly_compounded_yields)]

        elif domainY == domains.ZERO_RATE:
            return ctsly_compounded_yields
        
        else:
            raise ValueError(f'{self.__class__.__name__}.{__name__}: unsupported domain {domainY}.')
    
    def predict_at_date(self, date):
        """Get fitting method's prediction at a given date."""
        time = self.curve_time(date) 
        return self.fitting_method.predict(time)
    

    def df(self, date):
        """Return the discount factor on a specific date."""
        y = self.predict_at_date(date)
        domainY = self.build_settings.domainY

        if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
            return math.exp(-y)

        elif domainY == domains.ZERO_RATE:
            time = self.curve_time(date)
            return math.exp(-time * y)
        
        else:
            raise ValueError(f'{self.__class__.__name__}.df: unsupported domain {domainY}.')
    
    def time_weighted_zero_rate(self, date):
        """Return the time-weighted zero rate on a specific date."""
        df = self.df(date)
        return -1.0 * math.log(df)

    def zero_rate(self, date):
        "Return the zero rate on a specific date."
        time = self.curve_time(date)
        if time == 0:
            return 0.0
        return self.time_weighted_zero_rate(date) / time
    
    def one_day_forward_rate(self, date):
        "Return the 1D forward rate on a specific date."
        d0 = Date(date)
        d1 = d0.addTenor('1D')
        time = cu.time_difference(d0, d1, self.build_settings.domainX)

        f0 = self.time_weighted_zero_rate(d0)
        f1 = self.time_weighted_zero_rate(d1)
        return (f1 - f0) / time
    
    def instantaneous_forward_rate(self, date):
        """Return the instantaneous forward rate on a specific date."""
        time = self.curve_time(date)
        dydt = self.fitting_method.dydx(time)
        domainY = self.build_settings.domainY

        if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
            # dy/dt is the time-weighted zero rate time derivative 
            return dydt

        y = self.predict_at_date(date)
        if domainY == domains.ZERO_RATE:
            # dy/dt is the zero rate time derivative
            return y + time * dydt
    
    def df_gradient(self, date):
        """Return the gradient of the discount factor w.r.t. training data y values."""
        time = self.curve_time(date) 
        df = self.df(date)
        domainY = self.build_settings.domainY

        if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
            scale = 1.0
        elif domainY == domains.ZERO_RATE:
            scale = time
        else:
            raise ValueError(f'{self.__class__.__name__}.df: unsupported domain {domainY}.')
        
        return [(-df * scale) * g for g in self.fitting_method.grad(time)]

    def df_hessian(self, date):
        """Return the Hessian matrix of the discount factor w.r.t. training data y values."""
        time = self.curve_time(date) 
        df = self.df(date)
        domainY = self.build_settings.domainY

        if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
            scale = 1.0
        elif domainY == domains.ZERO_RATE:
            scale = time
        else:
            raise ValueError(f'{self.__class__.__name__}.df: unsupported domain {domainY}.')
        
        grad = self.df_gradient(date)
        hessian = self.fitting_method.hess(time)

        gradTgrad = [[ gi * gj for gj in grad] for gi in grad]
        m = [[ -scale * df * (-scale * g + h)  for g, h in zip(grow, hrow)] for grow, hrow in zip(gradTgrad, hessian)]
        return m


    def get_all_results(self, **kwargs):
        """Return a dict of all BondModel output."""
        # optional arguments
        tenor = kwargs.get('tenor') or '5Y'
        start_date = Date(kwargs.get('startDate') or self.t0_date)
        end_date = kwargs.get('endDate') or start_date.addTenor(tenor)
        
        # calculate results
        res = defaultdict(list)
        results_key_to_func = {
            'df': self.df,
            'time_weighted_zero_rate': self.time_weighted_zero_rate,
            'zero_rate': self.zero_rate,
            'instantaneous_forward_rate': self.instantaneous_forward_rate
        }

        d = start_date
        while d <= end_date:
            for key, func in results_key_to_func.items():
                try:
                    value = func(d)
                    res[key].append((str(d), value))
                except Exception as e:
                    app.logger.error(f'{self.__class__.__name__}.get_all_results: failed to calculate {key} on {d} because {e}.')
            
            d = d.addTenor('1D')
        return res


    # Valuation
    def project_cashflows(self, cashflows):
        """Return ProjectedCashflows obtained by applying the model's discount factors."""
        projection_function = self.df
        if isinstance(cashflows, MultiLegCashflows):
            projection_function = [self.df for _ in cashflows.legs]

        return ProjectedCashflows(cashflows, projection_function=projection_function, base_date=self.base_date)

    def pv_cashflows(self, cashflows):
        """Return the present value of these cashflows using the model's discount factors."""
        projected_cashflows = self.project_cashflows(cashflows)
        return projected_cashflows.sum_projected_amounts()

    
    # decorator
    def check_bond_type(bond_model_valuation):
        def inner(self, bond):
            if not isinstance(bond, Bond):
                raise ValueError(f'{self.__class__.__name__}.{bond_model_valuation.__name__}: bond argument must be of type Bond.')
            return bond_model_valuation(self, bond)
        return inner


    @check_bond_type
    def pv_bond(self, bond):
        """Return the present value of this bond using the model's discount factors."""
        return self.pv_cashflows(bond.cashflows)

    @check_bond_type
    def bond_model_clean_price(self, bond):
        """Return the clean price of this bond using the model's discount factors."""
        pv = self.pv_bond(bond)
        return bond.pv_to_clean_price(pv)
    
    @check_bond_type
    def bond_model_dirty_price(self, bond):
        """Return the dirty price of this bond using the model's discount factors."""
        pv = self.pv_bond(bond)
        return bond.pv_to_dirty_price(pv)

    @check_bond_type
    def bond_model_yield(self, bond):
        """Return the yield of this bond using the model's discount factors."""
        pv = self.pv_bond(bond)
        return bond.pv_to_yield(pv)

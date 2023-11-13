from .model import Model
from ..buildsettings.buildsettings import BuildSettingsCPICurve
from ..curveconstruction.curvedata import CpiLevelDataPoint, YoYDataPoint
from ..curveconstruction import domains
from ..curveconstruction import convertutils as cu
from ..utils import Date
from .. import config as cfg

from collections import defaultdict
import math
from .seasonality import SeasonalityModel

# get logger from current_app instance
from flask import current_app as app

class CpiModel(Model):
    def __init__(self, base_date, model_data=[], build_settings=None, reference_models=[]):
        super().__init__(base_date, model_data, build_settings, reference_models)

        # initialization
        self.training_data = []
        self.t0_cpi = None
        self.seasonality_model = SeasonalityModel(self.base_date)

        # Validate build settings
        if not isinstance(self.build_settings , BuildSettingsCPICurve):
            raise ValueError(f'CpiModel: build settings must be type BuildSettingsCPICurve but got {self.build_settings }.')

        # Convert curve data
        cpi_level_points = []
        yoy_points = []

        for p in self.model_data:
            if isinstance(p, CpiLevelDataPoint):
                cpi_level_points.append(p)
            elif isinstance(p, YoYDataPoint):
                yoy_points.append(p)
            else:
                raise ValueError(f'CpiModel: Received unsupported curve data point {p}.')

        cpi_level_points.sort(key=lambda p: p.date)

        # Get CPI levels at start dates for YoY points
        for p in yoy_points:
            for q in cpi_level_points:
                if p.start_date == q.date:
                    start_cpi_level = q.value
                    break
            else:
                # Went through all CPI level points without finding the start date
                raise ValueError(f'CpiModel: No CPI level on start date for YoY point {p}.')
            
            cpi_level_points.append(p.to_CpiLevelDataPoint(start_cpi_level))

        # Re-sort CPI level points
        cpi_level_points.sort(key=lambda p: p.date)

        # Set t0_date, default to min date in training data
        self.t0_date = self.build_settings.t0_date if self.build_settings.t0_date else cpi_level_points[0].date

        # Override reference models if provided
        for ref_model in reference_models:
            if isinstance(ref_model, SeasonalityModel):
                self.seasonality_model = ref_model

        # Strip seasonality out of CPI_LEVELS
        for p in cpi_level_points:
            p.value = self.seasonality_model.strip(self.t0_date, p.date, p.value)

        # Find t0_cpi
        for q in cpi_level_points:
            if self.t0_date == q.date:
                self.t0_cpi = q.value
                break
        else:
            domainY = self.build_settings.domainY
            if domainY in [domains.ZERO_RATE, domains.TIME_WEIGHTED_ZERO_RATE]:
                raise ValueError(f'CpiModel: CPI level on t0_date={self.t0_date} required when domainY={domainY}.')

        # Set training data        
        self.training_data = [p.convert(
                                self.build_settings.domainX,
                                self.build_settings.domainY,
                                self.t0_date,
                                self.t0_cpi
                                ) 
                                for p in cpi_level_points
                            ]

        # Fit training data
        self.fit()

        # Set t0_cpi if necessary
        if not self.t0_cpi:
            self.t0_cpi = self.cpi(self.t0_date)
        

    @classmethod
    def build(cls, base_date, curve_data, domainX, domainY, fitting_method_str, t0_date=None):
        build_settings = BuildSettingsCPICurve(domainX, domainY, fitting_method_str, t0_date)
        return CpiModel(base_date, curve_data, build_settings)

    def clamped_date(self, date, clamp_date=False):
        date = Date(date)
        return date.start_of_month() if clamp_date else date


    def clamped_time(self, date, clamp_date=False):
        date = self.clamped_date(date, clamp_date)
        return cu.time_difference(self.t0_date, date, self.build_settings.domainX)


    def predict_at_date(self, date, clamp_date=False):
        """Get fitting method's prediction at a given date."""
        time = self.clamped_time(date, clamp_date)
        return self.fitting_method.predict(time)


    # decorator
    def ensure_positive(cpi):
        def inner(self, date, *args):
            return max(cpi(self, date, *args), cfg.zero_tolerance_)
        return inner


    @ensure_positive
    def cpi_trend(self, date, clamp_date=False):
        """Return the CPI level without seasonality on a specific date."""
        y = self.predict_at_date(date, clamp_date)
        domainY = self.build_settings.domainY

        if domainY == domains.CPI_LEVEL:
            return y

        else:
            # t0_cpi is required
            if not self.t0_cpi:
                raise ValueError(f'CpiModel.cpi_trend: uninitialized t0_cpi for domain {domainY}.')
            
            if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
                return self.t0_cpi * math.exp(y)

            elif domainY == domains.ZERO_RATE:
                time = self.clamped_time(date, clamp_date)
                return self.t0_cpi * math.exp(time * y)

            else:
                raise ValueError(f'CpiModel.cpi_trend: unsupported domain {domainY}.')


    @ensure_positive
    def cpi(self, date, clamp_date=False, trend=False):
        """Return the CPI level with seasonality on a specific date."""
        date = self.clamped_date(date, clamp_date) 
        cpi_sa = self.cpi_trend(date, clamp_date)
        return cpi_sa if trend else self.seasonality_model.apply(self.t0_date, date, cpi_sa)


    def time_weighted_zero_rate(self, date, clamp_date=False, trend=True):
        """Return the time-weighted zero inflation rate on a specific date."""
        cpi = self.cpi(date, clamp_date, trend)
        if cpi < 0.0:
            raise ValueError(f'CpiModel.time_weighted_forward_rate: cannot calculate due to CPI projection {cpi} < 0 on {date}.')
        if self.t0_cpi <= 0.0:
            raise ValueError(f'CpiModel.time_weighted_forward_rate: cannot calculate due to CPI {self.t0_cpi} <= 0 at t0_date {self.t0_date}.')

        return math.log(cpi / self.t0_cpi)


    def zero_rate(self, date, clamp_date=False, trend=True):
        """Return the zero rate of the forward CPI on a specific date."""
        time = self.clamped_time(date, clamp_date)
        if time == 0.0:
            return 0.0
        return self.time_weighted_zero_rate(date, clamp_date, trend) / time


    def one_day_forward_rate(self, date, clamp_date=False, trend=True):
        """Return the 1D forward rate of inflation on a specific date."""
        d0 = Date(date)
        d1 = d0.addTenor('1D')
        time = cu.time_difference(d0, d1, self.build_settings.domainX)

        f0 = self.time_weighted_zero_rate(d0, clamp_date, trend)
        f1 = self.time_weighted_zero_rate(d1, clamp_date, trend)
        return (f1 - f0) / time


    def instantaneous_forward_rate(self, date, clamp_date=False, trend=True):
        """Return the instantaneous forward rate of inflation on a specific date."""
        time = self.clamped_time(date, clamp_date)
        dydt = self.fitting_method.dydx(time)
        domainY = self.build_settings.domainY
        
        if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
            # dy/dt is the time-weighted zero rate time derivative 
            return dydt

        y = self.predict_at_date(date, clamp_date)
        if domainY == domains.ZERO_RATE:
            # dy/dt is the zero rate time derivative
            return y + time * dydt

        elif domainY == domains.CPI_LEVEL:
            # dy/dt is the CPI level time derivative
            date = self.clamped_date(date, clamp_date)
            instantaneous_seasonality = 0.0 if trend else self.seasonality_model.instantaneous_seasonality_rate(date)
            y = max(y, cfg.zero_tolerance_)
            return (dydt / y) - instantaneous_seasonality


    def cpi_gradient(self, date, clamp_date=False):
        """Return the gradient of the cpi curve w.r.t. the training data y values."""
        domainY = self.build_settings.domainY
        time = self.clamped_time(date, clamp_date)
        grad = self.fitting_method.grad(time)

        if domainY == domains.CPI_LEVEL:
            return grad
        
        c = self.cpi_trend(date, clamp_date)
        if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
            return c * grad
        
        elif domainY == domains.ZERO_RATE:
            return (c * time) * grad
        
        else:
            raise ValueError(f'CpiModel.cpi_trend: unsupported domain {domainY}.')


    def cpi_hessian(self, date, clamp_date=False):
        """Return the Hessian matrix of the cpi curve w.r.t. the training data y values."""
        domainY = self.build_settings.domainY
        time = self.clamped_time(date, clamp_date)
        hessian = self.fitting_method.hess(time)

        if domainY == domains.CPI_LEVEL:
            return hessian
        
        c = self.cpi_trend(date, clamp_date)
        grad = self.fitting_method.grad(time)

        if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
            scale = 1.0
        elif domainY == domains.ZERO_RATE:
            scale = time
        else:
            raise ValueError(f'CpiModel.cpi_trend: unsupported domain {domainY}.')

        gradTgrad = grad.reshape(grad.size, 1) * grad
        m = scale * c * (scale * gradTgrad + hessian)
        return m
        

    def get_all_results(self, **kwargs):
        """Return a dict of all CpiModel output."""        
        # calculate results
        res = defaultdict(list)
        results_key_to_func = {
            'cpi': self.cpi,
            'cpi_trend': self.cpi_trend,
            'time_weighted_zero_rate': self.time_weighted_zero_rate,
            'zero_rate': self.zero_rate,
            'instantaneous_forward_rate': self.instantaneous_forward_rate
        }

        for d in self.get_curve_result_dates():
            for key, func in results_key_to_func.items():
                try:
                    value = func(d)
                    res[key].append((str(d), value))
                except Exception as e:
                    app.logger.error(f'CpiModel.get_all_results: failed to calculate {key} on {d} because {e}.')

        return res

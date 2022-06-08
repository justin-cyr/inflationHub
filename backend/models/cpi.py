from .model import Model
from ..buildsettings.buildsettings import BuildSettingsCPICurve
from ..curveconstruction.curvedata import CpiLevelDataPoint, YoYDataPoint
from ..curveconstruction import domains
from ..curveconstruction import convertutils as cu
from ..utils import Date

import math
from .seasonality import SeasonalityModel

class CpiModel(Model):
    def __init__(self, base_date, model_data=[], build_settings=None, reference_models=[]):
        super().__init__(base_date, model_data, build_settings, reference_models)

        # initialization
        self.training_data = []
        self.t0_date = self.build_settings.t0_date if self.build_settings.t0_date else base_date
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
        self.fitting_method.fit(*zip(*self.training_data))


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
                time = self.clamped_time()
                return self.t0_cpi * math.exp(time * y)

            else:
                raise ValueError(f'CpiModel.cpi_trend: unsupported domain {domainY}.')


    def cpi(self, date, clamp_date=False):
        """Return the CPI level with seasonality on a specific date."""
        date = self.clamped_date(date, clamp_date) 
        cpi_sa = self.cpi_trend(date, clamp_date)
        return self.seasonality_model.apply(self.t0_date, date, cpi_sa)

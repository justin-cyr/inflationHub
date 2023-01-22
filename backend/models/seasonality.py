
from .model import Model
from ..config import zero_tolerance_
from ..utils import Date, Month
from ..buildsettings.buildsettings import BuildSettingsSeasonality
from ..curveconstruction.curvedata import CpiLevelDataPoint, AdditiveSeasonalityDataPoint

from collections import defaultdict
import datetime
import math

# get logger from current_app instance
from flask import current_app as app

class SeasonalityModel(Model):
    def __init__(self, base_date, training_data=[], build_settings=None):
        # no reference model is needed
        super().__init__(base_date, training_data, build_settings)

    # Default implementations are for No Seasonality model - override in derived classes
    def __repr__(self):
        return f'NoSeasonalityModel({self.base_date})'

    def strip(self, start_date, end_date, end_cpi_nsa):
        return end_cpi_nsa

    def apply(self, start_date, end_date, end_cpi_trend):
        return end_cpi_trend

    # consistency verification functions - use these default implementions in derived classes
    def expect_invertible(self, start_date, end_date, cpi):
        """Return True if apply and strip are inverses over this time period for this value, False otherwise."""
        return (self.apply(start_date, end_date, self.strip(start_date, end_date, cpi)) == cpi) and \
                (self.strip(start_date, end_date, self.apply(start_date, end_date, cpi)) == cpi)

    def expect_no_net_seasonality(self, date, cpi):
        """Return True if there is no net seasonality from date to date + 1Y, False otherwise."""
        start_date = Date(date)
        end_date = start_date.addOneYear()
        return self.apply(start_date, end_date, cpi) == cpi
    
    def instantaneous_forward_rate(self, date):
        """Return the instantaneous rate of seasonality on a specific date."""
        # Default implementation for No Seasonality
        return 0.0

    def time_weighted_zero_rate(self, date):
        """Return the time-weighted zero seasonality rate on a specific date."""
        # Default implementation for No Seasonality
        return 0.0

    def zero_rate(self, date):
        # Default implementation for No Seasonality
        return 0.0

    def get_all_results(self, **kwargs):
        """Return a dict of all SeasonalityModel output."""
        # calculate results
        res = defaultdict(list)
        results_key_to_func = {
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
                    app.logger.error(f'{__class__.__name__}.{__name__}: failed to calculate {key} on {d} because {e}.')
        return res


class AdditiveSeasonalityModel(SeasonalityModel):
    def __init__(self, base_date, training_data, build_settings=None):
        super().__init__(base_date, training_data, build_settings)
        
        num_points = len(self.model_data)
        if num_points != 12:
            raise ValueError(f'{__class__.__name__}: requires exactly 12 AdditiveSeasonalityDataPoints but got {num_points}.')

        for p in self.model_data:
            if not isinstance(p, AdditiveSeasonalityDataPoint):
                raise ValueError(f'{__class__.__name__}: only supports AdditiveSeasonalityDataPoints but got {p}.')

        self.seasonals_map = { p.get_month().to_num(): p.value for p in self.model_data }

        # validation
        if len(self.seasonals_map.keys()) != 12:
            raise ValueError(f'{__class__.__name__}: requires all 12 months but got {self.seasonals_map.keys()}.')

        seasonals_sum = sum(self.seasonals_map.values())
        if abs(seasonals_sum) > zero_tolerance_:
            raise ValueError(f'{__class__.__name__}: seasonals sum must be 0 but got {seasonals_sum}.')

    @classmethod
    def build(cls, base_date, curve_data, domainX, domainY):
        build_settings = BuildSettingsSeasonality(domainX, domainY)
        return AdditiveSeasonalityModel(base_date, curve_data, build_settings)


    def __repr__(self):
        return f'{__class__.__name__}({self.base_date})'

    def strip(self, start_date, end_date, end_cpi_nsa):
        adjustment = self.integrate(start_date, end_date)
        return end_cpi_nsa * math.exp(-adjustment)

    def apply(self, start_date, end_date, end_cpi_trend):
        adjustment = self.integrate(start_date, end_date)
        return end_cpi_trend * math.exp(adjustment)

    def instantaneous_forward_rate(self, date):
        """Return the instantaneous rate of seasonality on a specific date."""
        if not isinstance(date, Date):
            date = Date(date)
        return self.seasonals_map[date.month]

    def time_with_seasonals(self, start_date, end_date):
        """Return a vector with the time measure (mod 1 year) that is spend integrating each seasonal from start_date to end_date."""
        if not isinstance(start_date, Date):
            start_date = Date(start_date)
        if not isinstance(end_date, Date):
            end_date = Date(end_date)

        if start_date > end_date:
            raise ValueError(f'{__class__.__name__}.{__name__}: requires start_date <= end_date.')
        elif start_date == end_date:
            return [0.0] * 12

        if start_date.addOneYear() <= end_date:
            # advance to within 1 year
            if start_date.month < end_date.month:
                start_date = Date(datetime.date(end_date.year, start_date.month, start_date.day))
            elif start_date.month > end_date.month:
                start_date = Date(datetime.date(end_date.year - 1, start_date.month, start_date.day))
            else:
                # same month
                if start_date.day <= end_date.day:
                    start_date = Date(datetime.date(end_date.year, start_date.month, start_date.day))
                else:
                    start_date = Date(datetime.date(end_date.year - 1, start_date.month, start_date.day))

        times = [0.0] * 12
        one_twelth = 1.0 / 12.0
        start_date_eom = start_date.endOfMonth()
        end_date_eom = end_date.endOfMonth()

        m = start_date.month
        if (start_date.day == 1) and (end_date > start_date_eom):
            # start month is full
            times[m - 1] = one_twelth
        elif (end_date <= start_date_eom):
            # start month is partial and equals end month
            times[m - 1] = one_twelth * ((end_date.day - start_date.day) * time_measure(start_date_eom))
            return times
        else:
            # start month is partial
            times[m - 1] = one_twelth * (1.0 - start_date.day * time_measure(start_date_eom))

        m = 12 if m == 11 else (m + 1) % 12
        while m != end_date.month:
            # full months
            times[m - 1] = one_twelth
            m = 12 if m == 11 else (m + 1) % 12

        # At this point:
        #  m == end_date.month
        #  start_date <= start_date_eom < end_date
        # so, end month is partial and covers 1st day
        times[m - 1] = one_twelth * ((end_date.day - 1) * time_measure(end_date_eom))
        return times

    def integrate(self, start_date, end_date):
        """Return the integral of the seasonal curve over [start_date, end_date)."""
        times = self.time_with_seasonals(start_date, end_date)
        return sum([self.seasonals_map[m] * times[m - 1] for m in range(1, 13)])

    def time_weighted_zero_rate(self, date):
        """Return the time-weighted zero seasonality rate on a specific date."""
        return self.integrate(self.base_date, date)

    def zero_rate(self, date):
        time = sum(self.time_with_seasonals(self.base_date, date))
        if time > 0.0:
            return self.time_weighted_zero_rate(date) / time
        else:
            return 0.0


class HistoricalDeviationSeasonalityModel(AdditiveSeasonalityModel):
    def __init__(self, base_date, training_data, build_settings=None):
        SeasonalityModel.__init__(self, base_date, training_data, build_settings)

        num_points = len(self.model_data)
        if num_points < 13:
            raise ValueError(f'{__class__.__name__}: requires at least 13 CpiLevelDataPoints but got {num_points}.')
        if num_points % 12 != 1:
            raise ValueError(f'{__class__.__name__}: requires 1 (mod 12) data points but got {num_points}.')

        # check curve data consistency
        for p in self.model_data:
            if not isinstance(p, CpiLevelDataPoint):
                raise ValueError(f'{__class__.__name__}: only supports CpiLevelDataPoints but got {p}.')

        self.training_data = sorted(self.model_data, key=lambda p: p.date)

        # calculate MoM CPI growth
        growth_rates = defaultdict(list)
        for last, next in zip(self.training_data[:-1], self.training_data[1:]):
            # is consecutive?
            if not last.date.isMonthBefore(next.date):
                raise ValueError(f'{__class__.__name__}: requires consecutive months but got gap between {last.date} and {next.date}.')
            growth_rates[next.date.month].append(math.log(next.value / last.value))

        # calculate avg growth and deviations
        num_years = num_points // 12
        sum_growth_rates = []
        for m in range(1, 13):
            sum_growth_rates.append(sum(growth_rates[m]))

        long_term_avg = sum(sum_growth_rates) / (num_points - 1)
        annualized_deviations = [12.0 * (v / num_years - long_term_avg) for v in sum_growth_rates]

        # initialize as additive seasonality model
        months = [Month.from_num(m) for m in range(1, 13)]
        data_points = [AdditiveSeasonalityDataPoint(d, m).serialize() for d, m in zip(annualized_deviations, months)]
        super().__init__(self.base_date, data_points, build_settings=self.build_settings)

    @classmethod
    def build(cls, base_date, curve_data, domainX, domainY):
        build_settings = BuildSettingsSeasonality(domainX, domainY)
        return HistoricalDeviationSeasonalityModel(base_date, curve_data, build_settings)


def time_measure(date):
    """Return the seasonality time measure for a given Date."""
    if not isinstance(date, Date):
        date = Date(date)
    if (date.month == 2) and (date.isLeapYear()):
        return 1.0 / 28.0
    else:
        return 1.0 / date.daysInMonth()

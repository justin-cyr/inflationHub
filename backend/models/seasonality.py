
from .model import Model
from ..utils import Date

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
    
    def instantaneous_seasonality_rate(self, date):
        """Return the instantaneous rate of seasonality on a specific date."""
        # Default implementation for No Seasonality
        return 0.0

    def get_all_results(self, **kwargs):
        """Return a dict of all SeasonalityModel output."""
        raise NotImplementedError('SeasonalityModel.get_all_results: not yet implemented.')

def time_measure(date):
    """Return the seasonality time measure for a given Date."""
    date = Date(date)
    return 1.0 / date.daysInMonth() if not date.isLeapDay() else 0.0

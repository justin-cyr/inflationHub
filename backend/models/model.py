
from ..curveconstruction.curvedata import CurveDataPointFactory
from ..utils import Date, EomRule
from ..fittingmethods.fittingmethodfactory import FittingMethodFactory

class Model(object):
    def __init__(self, base_date, model_data=[], build_settings=None, reference_models=[]):
        self.base_date = Date(base_date)

        if not isinstance(model_data, list):
            raise TypeError('Model: training_data must be a list of serialized CurveDataPoints.')
        self.model_data = [CurveDataPointFactory.deserialize(d) for d in model_data]

        self.build_settings = build_settings

        if not isinstance(reference_models, list):
            raise TypeError('Model: reference_models must be a list of models.')
        self.reference_models = reference_models

        # Set fitting method
        if self.build_settings:
            self.fitting_method = FittingMethodFactory.create(
                self.build_settings.fitting_method_str,
                self.build_settings.domainX,
                self.build_settings.domainY
            )


    def __repr__(self):
        return f'{self.__class__.__name__}({self.base_date})'

    def fit(self):
        self.fitting_method.fit(*zip(*self.training_data))
        return

    def get_all_results(self, **kwargs):
        """Return a dict of all model output."""
        raise NotImplementedError('Model.get_all_results: not implemented in base class.')

    def get_curve_result_dates(self):
        """Return a list of Dates to evaluate model results."""
        start_date = self.base_date
        daily_end_date = start_date.addTenor('3Y')
        weekly_end_date = start_date.addTenor('10Y')
        monthly_end_date = start_date.addTenor('31Y')

        dates = []
        d = start_date
        while d <= daily_end_date:
            dates.append(d)
            d = d.addDays(1)
        
        while d <= weekly_end_date:
            dates.append(d)
            d = d.addDays(7)

        while d <= monthly_end_date:
            dates.append(d)
            d = d.addMonths(1, EomRule.LAST)

        return dates

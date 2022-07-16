
from ..curveconstruction.curvedata import CurveDataPointFactory
from ..utils import Date
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


    def get_all_results(self, **kwargs):
        """Return a dict of all model output."""
        raise NotImplementedError('Model.get_all_results: not implemented in base class.')

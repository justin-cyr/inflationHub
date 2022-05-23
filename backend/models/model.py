
from ..curveconstruction.curvedata import CurveDataPointFactory
from ..utils import Date

class Model(object):
    def __init__(self, base_date, training_data=[], build_settings={}, reference_models=[]):
        self.base_date = Date(base_date)

        if not isinstance(training_data, list):
            raise TypeError('Model: training_data must be a list of serialized CurveDataPoints.')
        self.training_data = [CurveDataPointFactory.deserialize(d) for d in training_data]

        self.build_settings = build_settings

        if not isinstance(reference_models, list):
            raise TypeError('Model: reference_models must be a list of models.')
        self.reference_models = reference_models


    


from .. import config as cfg

# Import derived model types for building
from .cpi import CpiModel
from .bond import BondModel

class ModelFactory(object):

    def build(params):
    # return a Model object built from arguments in params

        model_type = params.get('model_type')
        base_date = params.get('base_date')
        model_data = params.get('model_data')

        domainX = params.get('domainX')
        domainY = params.get('domainY')
        fitting_method_str = params.get('fitting_method_str')
        t0_date = params.get('t0_date')
        calibration_tolerance = params.get('calibration_tolerance')

        if model_type == cfg.CPI:
            return CpiModel.build(
                    base_date,
                    model_data,
                    domainX,
                    domainY,
                    fitting_method_str,
                    t0_date=t0_date
                )
        elif model_type == cfg.BONDCURVE:
            return BondModel.build(
                    base_date,
                    model_data,
                    domainX,
                    domainY,
                    fitting_method_str,
                    t0_date=t0_date,
                    calibration_tolerance=calibration_tolerance
                )
        else:
            raise ValueError(f'ModelFactory.build: unsupported model type" {model_type}.')


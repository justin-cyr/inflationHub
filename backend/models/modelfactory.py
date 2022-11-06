
from .. import config as cfg
from ..data import DataAPI
from ..tips_data import benchmark_bond_yield_data_point

# Import derived model types for building
from .cpi import CpiModel
from .bond import BondModel

class ModelFactory(object):

    def build(params):
    # return a Model object built from arguments in params

        model_type = params.get('model_type')
        base_date = params.get('base_date')
        if 'model_data' in params:
            model_data = params['model_data']
        else:
            model_data = ModelFactory.get_model_data(params)

        domainX = params.get('domainX')
        domainY = params.get('domainY')
        fitting_method_str = params.get('fitting_method_str')
        t0_date = params.get('t0_date', base_date)
        calibration_tolerance = params.get('calibration_tolerance', cfg.calibration_tolerance_)
        opt_method = params.get('opt_method', cfg.BFGS)

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
                    calibration_tolerance=calibration_tolerance,
                    opt_method=opt_method
                )
        else:
            raise ValueError(f'ModelFactory.build: unsupported model type {model_type}.')

    @staticmethod
    def get_model_data(params):
        """Get training data for this model based on model_type."""

        if 'model_type' not in params:
            raise KeyError('ModelFactory.get_model_data: params must specify a model_type.')
        model_type = params['model_type']

        if model_type == cfg.BONDCURVE:
            # only Cnbc supported currently, since those have maturity date and coupon
            quote_source = 'CNBC US Treasury Yields (intraday)'
            quotes = DataAPI(quote_source).get_and_parse_data()['data']
            benchmark_bond_quotes = [benchmark_bond_yield_data_point(**q).serialize() for q in quotes]
            return benchmark_bond_quotes
        else:
            raise ValueError(f'ModelFactory.get_model_data: unsupported model type {model_type}')

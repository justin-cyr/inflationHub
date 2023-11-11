
from .. import config as cfg
from ..data import DataAPI
from ..utils import Date
from ..curveconstruction.curvedata import BondYieldDataPoint

# Import derived model types for building
from .cpi import CpiModel
from .bond import BondModel
from .seasonality import AdditiveSeasonalityModel, HistoricalDeviationSeasonalityModel

class ModelFactory(object):

    def build(params):
    # return a Model object built from arguments in params

        model_type = params.get('model_type')
        base_date = params.get('base_date', Date.today())
        if 'model_data' in params and params['model_data']:
            model_data = params['model_data']
        else:
            model_data = ModelFactory.get_model_data(params)

        domainX = params.get('domainX')
        domainY = params.get('domainY')
        fitting_method_str = params.get('fitting_method_str')
        t0_date = params.get('t0_date')
        calibration_tolerance = float(params.get('calibration_tolerance', cfg.calibration_tolerance_))
        opt_method = params.get('opt_method', cfg.TRUST_CONSTR)
        initial_guess = params.get('initial_guess', [])
        if initial_guess:
            initial_guess = [float(x) for x in initial_guess]

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
                    opt_method=opt_method,
                    initial_guess=initial_guess
                )
        elif model_type == cfg.ADDITIVE_SEASONALITY:
            return AdditiveSeasonalityModel.build(
                base_date,
                model_data,
                domainX,
                domainY
            )
        elif model_type == cfg.HIST_DEV_SEASONALITY:
            return HistoricalDeviationSeasonalityModel.build(
                base_date,
                model_data,
                domainX,
                domainY
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
            quote_source = params.get('quote_source', 'CNBC OTR Treasuries')
            quotes = DataAPI(quote_source).get_and_parse_data()['data']
            benchmark_bond_quotes = [BondYieldDataPoint.from_bond_nvps(**q).serialize() for q in quotes]
            return benchmark_bond_quotes

        elif model_type == cfg.CPI:
            quote_source = params['quote_source']
            cpi_curve_quotes = DataAPI(quote_source).get_and_parse_data()['data']
            return cpi_curve_quotes

        else:
            raise ValueError(f'ModelFactory.get_model_data: unsupported model type {model_type}')

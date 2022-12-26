
from ...curveconstruction.curvedata import CpiLevelDataPoint
from ...curveconstruction import domains
from ...models.modelfactory import ModelFactory
from ...data import DataAPI

import pytest

# TESTS
def test_historical_calibration(app):
    with app.app_context():
        num_years = 5
        cpi_data = DataAPI('US CPI NSA').get_and_parse_data()['data']
        dates = cpi_data['Date'][-(12 * num_years + 1):]
        values = cpi_data['US CPI NSA'][-(12 * num_years + 1):]
        cpi_data_points = [CpiLevelDataPoint(v, d).serialize() for d, v in zip(dates, values)]

        build_params = {
            'model_type': 'HistDevSeasonality',
            'base_date': '2022-12-25',
            'model_data': cpi_data_points,
            'domainX': domains.MONTH,
            'domainY': domains.ADDITIVE_SEASONALITY,
            'fitting_method_str': 'PiecewiseConstantLeftCts'
        }

        seasonality_model = ModelFactory.build(build_params)
        print(seasonality_model.__dict__)

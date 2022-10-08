
from ...products.bonds import Bond
from ...curveconstruction.curvedata import BondYieldDataPoint
from ...buildsettings.buildsettings import BuildSettingsBondCurve
from ...curveconstruction import domains
from ...models.modelfactory import ModelFactory

import pytest

# FIXTURES

@pytest.fixture()
def otr_nominal_bonds():
    params = [
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04125, 'maturity_date': '2027-09-30', 'dated_date': '2022-09-30'}, # 5y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.02750, 'maturity_date': '2032-08-15', 'dated_date': '2022-08-15'}, # 10y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03000, 'maturity_date': '2052-08-15', 'dated_date': '2022-08-15'}  # 30y
    ]
    bonds = [Bond.create_bond(**p) for p in params]

    return bonds

@pytest.fixture()
def otr_nominal_yields():
    yields = [
        0.04087, # 5y
        0.03829, # 10y
        0.03781  # 30y
    ]
    return yields

@pytest.fixture()
def bond_data_points(otr_nominal_bonds, otr_nominal_yields):
    return [BondYieldDataPoint(y, b).serialize() for b, y in zip(otr_nominal_bonds, otr_nominal_yields)]

@pytest.fixture()
def default_build_params(bond_data_points):
    model_build_params = {
        'model_type': 'BondCurve',
        'base_date': '2022-10-01',
        'model_data': bond_data_points,
        'domainX': domains.TIME_ACT_365,
        'domainY': domains.TIME_WEIGHTED_ZERO_RATE,
        'fitting_method_str': 'PiecewiseLinear',
        't0_date': '2022-10-01',
        'calibration_tolerance': 1E-8,
        'opt_method': 'BFGS'
        }
    return model_build_params


# DECORATORS

def run_with_profiler(test_fun):
    import cProfile
    import pstats
    import io

    def inner(app, default_build_params, *args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        print(args)
        print(kwargs)
        test_fun(app, default_build_params, *args, **kwargs)
        pr.disable()

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats()
        print(s.getvalue())

    return inner

# TESTS

def test_fixtures(otr_nominal_bonds):
    assert all([isinstance(b, Bond) for b in otr_nominal_bonds])

@run_with_profiler
def test_BFGS_calibration(app, default_build_params):
    build_params = default_build_params
    build_params['opt_method'] = 'BFGS'

    with app.app_context():
        bond_model = ModelFactory.build(build_params)

@run_with_profiler
def test_CG_calibration(app, default_build_params):
    build_params = default_build_params
    build_params['opt_method'] = 'CG'

    with app.app_context():
        bond_model = ModelFactory.build(build_params)

@run_with_profiler
def test_trust_constr_calibration(app, default_build_params):
    build_params = default_build_params
    build_params['opt_method'] = 'BFGS'

    with app.app_context():
        bond_model = ModelFactory.build(build_params)

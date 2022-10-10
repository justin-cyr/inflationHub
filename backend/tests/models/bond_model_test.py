
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
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2022-11-08'}, # 1M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-01-05'}, # 3M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-04-06'}, # 6M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-10-05'}, # 1Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04250, 'maturity_date': '2024-09-30', 'dated_date': '2022-09-30'}, # 2Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03500, 'maturity_date': '2025-09-30', 'dated_date': '2022-09-15'}, # 3Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04125, 'maturity_date': '2027-09-30', 'dated_date': '2022-09-30'}, # 5Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03875, 'maturity_date': '2029-09-30', 'dated_date': '2022-09-30'}, # 7Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.02750, 'maturity_date': '2032-08-15', 'dated_date': '2022-08-15'}, # 10Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03375, 'maturity_date': '2042-08-15', 'dated_date': '2022-08-15'}, # 20Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03000, 'maturity_date': '2052-08-15', 'dated_date': '2022-08-15'}  # 30Y
    ]
    bonds = [Bond.create_bond(**p) for p in params]

    return bonds

@pytest.fixture()
def otr_nominal_yields():
    yields = [
        0.02967, # 1M
        0.03378, # 3M
        0.04089, # 6M
        0.04181, # 1Y
        0.04312, # 2Y
        0.04349, # 3Y
        0.04149, # 5Y
        0.04037, # 7Y
        0.03888, # 10Y
        0.04148, # 20Y
        0.03848  # 30Y
    ]
    return yields

@pytest.fixture()
def bond_data_points(otr_nominal_bonds, otr_nominal_yields):
    return [BondYieldDataPoint(y, b).serialize() for b, y in zip(otr_nominal_bonds, otr_nominal_yields)]

@pytest.fixture()
def default_build_params(bond_data_points):
    model_build_params = {
        'model_type': 'BondCurve',
        'base_date': '2022-10-10',
        'model_data': bond_data_points,
        'domainX': domains.TIME_ACT_365,
        'domainY': domains.TIME_WEIGHTED_ZERO_RATE,
        'fitting_method_str': 'PiecewiseLinear',
        't0_date': '2022-10-10',
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

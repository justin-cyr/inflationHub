
from ...products.bonds import Bond
from ...curveconstruction.curvedata import BondYieldDataPoint
from ...curveconstruction import domains
from ...models.modelfactory import ModelFactory
from ...data import DataAPI
from ...tips_data import benchmark_bond_yield_data_point

import pytest

# FIXTURES

@pytest.fixture()
def otr_nominal_bonds():
    params = [
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2022-11-08'}, # 1M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-01-05'}, # 3M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-04-06'}, # 6M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-10-05'}, # 1Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04250, 'maturity_date': '2024-09-30', 'tenor': '2Y'}, # 2Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03500, 'maturity_date': '2025-09-30', 'tenor': '3Y'}, # 3Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04125, 'maturity_date': '2027-09-30', 'tenor': '5Y'}, # 5Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03875, 'maturity_date': '2029-09-30', 'tenor': '7Y'}, # 7Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.02750, 'maturity_date': '2032-08-15', 'tenor': '10Y'}, # 10Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03375, 'maturity_date': '2042-08-15', 'tenor': '20Y'}, # 20Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03000, 'maturity_date': '2052-08-15', 'tenor': '30Y'}  # 30Y
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
        'opt_method': 'CG'
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

def test_otr_bond_schedules():
    params = [
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2022-12-06'}, # 1M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-02-09'}, # 3M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-05-11'}, # 6M
        {'Convention': 'USTBill', 'notional': 100, 'maturity_date': '2023-11-02'}, # 1Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04375, 'maturity_date': '2024-10-31', 'tenor': '2Y'}, # 2Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04500, 'maturity_date': '2025-11-15', 'tenor': '3Y'}, # 3Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04125, 'maturity_date': '2027-10-31', 'tenor': '5Y'}, # 5Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04000, 'maturity_date': '2029-10-31', 'tenor': '7Y'}, # 7Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.04125, 'maturity_date': '2032-11-15', 'tenor': '10Y'}, # 10Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03375, 'maturity_date': '2042-08-15', 'tenor': '20Y'}, # 20Y
        {'Convention': 'USTBond', 'notional': 100, 'rate': 0.03000, 'maturity_date': '2052-08-15', 'tenor': '30Y'}  # 30Y
    ]
    bonds = [Bond.create_bond(**p) for p in params]

    # ZeroCouponBonds
    assert str(bonds[0].maturity_date) == '2022-12-06'
    assert str(bonds[1].maturity_date) == '2023-02-09'
    assert str(bonds[2].maturity_date) == '2023-05-11'
    assert str(bonds[3].maturity_date) == '2023-11-02'

    # FixedRateBonds
    assert [str(d) for d in bonds[4].coupon_schedule.unadj_start_dates] == [
        '2022-10-31', '2023-04-30',
        '2023-10-31', '2024-04-30'
        ]
    assert [str(d) for d in bonds[5].coupon_schedule.unadj_start_dates] == [
        '2022-11-15', '2023-05-15',
        '2023-11-15', '2024-05-15',
        '2024-11-15', '2025-05-15'
        ]
    assert [str(d) for d in bonds[10].coupon_schedule.unadj_start_dates[:2]] == [
        '2022-08-15', '2023-02-15',
    ]

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

@run_with_profiler
def test_standard_nominal_calibration(app, default_build_params):
    # volatile test: quotes can change on each test run
    build_params = default_build_params

    with app.app_context(): 
        quotes = DataAPI('CNBC US Treasury Yields (intraday)').get_and_parse_data()['data']
        benchmark_bond_quotes = [benchmark_bond_yield_data_point(**q).serialize() for q in quotes]
        build_params['model_data'] = benchmark_bond_quotes

        bond_model = ModelFactory.build(build_params)

    print(quotes)


from ...data import DataAPI

import pytest

def get_and_parse_test(app, name):
    with app.app_context():
        d = DataAPI(name)
        res = d.get_and_parse_data()
        print(res)
        assert isinstance(res, dict)
        assert 'data' in res
        assert res['data'] is not None
        assert res['data'] != []
        assert res['data'] != {}


treasuries_monitor = [
    'CNBC US Treasury Yields with 2M, 4M bills (intraday)',
    'WSJ US Treasury Yields (intraday)',
    'MW US Treasury Yields (intraday)',
    'CME US Treasury Prices (intraday)',
    'CNBC TIPS Yields (intraday)'
]

@pytest.mark.parametrize('name', treasuries_monitor, ids=treasuries_monitor)
def test_treasuries_monitor(app, name):
    get_and_parse_test(app, name)


bond_futures_monitor = [
    'CME 2Y UST Futures (intraday)',
    'CME 3Y UST Futures (intraday)',
    'CME 5Y UST Futures (intraday)',
    'CME 10Y UST Futures (intraday)',
    'CME 20Y UST Futures (intraday)',
    'CME 30Y UST Futures (intraday)',
    'CME Ultra-10Y UST Futures (intraday)',
    'CME Ultra-30Y UST Futures (intraday)',
    'CME 2Y Micro-yield Futures (intraday)',
    'CME 5Y Micro-yield Futures (intraday)',
    'CME 10Y Micro-yield Futures (intraday)',
    'CME 30Y Micro-yield Futures (intraday)',
    'QuikStrike CTD-OTR Table'
]

@pytest.mark.parametrize('name', bond_futures_monitor, ids=bond_futures_monitor)
def test_bond_futures_monitor(app, name):
    get_and_parse_test(app, name)


ir_futures_monitor = [
    'CME 3M SOFR Futures (intraday)',
    'CME 1M SOFR Futures (intraday)',
    'CME 30D FF Futures (intraday)',
    'Eris Swap Futures (intraday)'
]

@pytest.mark.parametrize('name', ir_futures_monitor, ids=ir_futures_monitor)
def test_ir_futures_monitor(app, name):
    get_and_parse_test(app, name)


composite_getters = [
    'CNBC OTR Treasuries',
    'CME CTD Forward Yields'
]

@pytest.mark.parametrize('name', composite_getters, ids=composite_getters)
def test_composite_getters(app, name):
    get_and_parse_test(app, name)

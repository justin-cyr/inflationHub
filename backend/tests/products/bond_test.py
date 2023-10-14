
from ...products.bonds import Bond

import pytest

# FIXTURES

@pytest.fixture()
def bond_with_settlement_date():
    params = {
        'Convention': 'USTBond',
        'notional': 100,
        'rate': 0.05,
        'maturity_date': '2025-09-30',
        'settlement_date': '2024-01-04'
    }
    return Bond.create_bond(**params)

# TESTS

def test_get_settlement_date(bond_with_settlement_date):
    bond = bond_with_settlement_date
    print(bond)
    print(bond.settlement_date)
    assert str(bond.get_settlement_date()) == '2024-01-04'

def test_fwd_yield(bond_with_settlement_date):
    bond = bond_with_settlement_date
    price = 99.63316016
    y = bond.clean_price_to_yield(price)
    assert abs(y - 0.05219) < 5E-5

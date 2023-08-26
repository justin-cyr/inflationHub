
from app import app as flask_app

import pytest

# USAGE:
#   pytest must be run from the root directory in order for file paths to be found
#
#   Run all tests:
#   pytest
#
#   Useful flags:
#   -s show console output
#   -v verbose output
#
#   Run tests in a directory:
#   pytest backend/tests/models/
#
#   Run tests in a specific module:
#   pytest backend/tests/models/bond_model_test.py
#
#   Run a specific test:
#   pytest backend/tests/models/bond_model_test.py::test_CG_calibration
#


@pytest.fixture()
def app():
    flask_app.config.update({
        'TESTING': True
    })

    # more setup

    yield flask_app

    # tear down

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def pytest_addoption(parser):
    parser.addoption('--opt_method', action='store', default='BFGS')

@pytest.fixture()
def opt_method(request):
    return request.config.getoption('--opt_method')


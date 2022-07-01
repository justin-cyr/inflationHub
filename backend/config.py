
import os
import json

# String symbols
APP_AUTHOR = 'APP_AUTHOR'
APP_NAME = 'APP_NAME'
APP_VERSION = 'APP_VERSION'
IS_PROD = 'IS_PROD'
CHROMEDRIVER_PATH = 'CHROMEDRIVER_PATH'
GOOGLE_CHROME_BIN = 'GOOGLE_CHROME_BIN'

# Model names
CPI = 'CPI'
SEASONALITY = 'Seasonality'

# get logger from current_app instance
from flask import current_app as app

# Set app configuration fron environment
if IS_PROD in os.environ:
    # Check settings
    env_vars_to_set = [
        CHROMEDRIVER_PATH,
        GOOGLE_CHROME_BIN
    ]
    for var in env_vars_to_set:
        if var not in os.environ:
            msg = f'Environment variable {var} is not set.'
            app.logger.error(msg)
            raise KeyError(msg)
else:
    # development settings
    from webdriver_manager.chrome import ChromeDriverManager
    os.environ[CHROMEDRIVER_PATH] = ChromeDriverManager().install()

    os.environ['PATH'] += os.pathsep + os.environ[CHROMEDRIVER_PATH]


def get_app_info():
    """Returns a dictionary of app info data."""
    frontend_path = os.path.abspath('frontend')
    package_dot_json_path = os.path.join(frontend_path, 'package.json')

    with open(package_dot_json_path, 'r') as f:
        package_dot_json = json.load(f)

    return dict(
        APP_AUTHOR = package_dot_json['author'],
        APP_NAME = package_dot_json['name'],
        APP_VERSION = package_dot_json['version']
    )

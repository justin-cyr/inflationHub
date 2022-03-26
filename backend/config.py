
import os
import json

# String symbols
APP_AUTHOR = 'APP_AUTHOR'
APP_NAME = 'APP_NAME'
APP_VERSION = 'APP_VERSION'

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

from flask import Flask, send_from_directory
import logging

# Backend API
from backend import config as cfg
from backend import data

app = Flask(__name__, static_url_path='', static_folder='frontend/build')

# configure logger
app.logger.setLevel(logging.DEBUG)

@app.route('/')
def serve():
    return send_from_directory(app.static_folder,'index.html')

@app.route('/app_info')
def get_app_info():
    return cfg.get_app_info()

@app.route('/all_data_names')
def get_all_data_names():
    return dict(names=sorted(data.DATA_CONFIG.keys()))

@app.route('/data/<name>')
def get_data(name):
    try:
        app.logger.info('Request get_data(\'' + name + '\')')
        data_api = data.DataAPI(name)
        app.logger.debug('DataAPI(\''+ name + '\') returned ' + str(data_api))
        return data_api.get_and_parse_data()
    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/tips_cusips')
def get_tips_cusips():
    try:
        from backend.tips_data import get_tips_cusips
        cusips = get_tips_cusips()
        return dict(cusips=cusips)

    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/tips_reference_data/<cusip>')
def get_tips_reference_data(cusip):
    try:
        from backend.tips_data import get_treasury_reference_data
        reference_data = get_treasury_reference_data(cusip)
        return dict(referenceData=reference_data)

    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/tips_yield_data/<cusip>')
def get_tips_yield_data(cusip):
    try:
        from backend.tips_data import get_tips_yield_data_by_cusip
        return get_tips_yield_data_by_cusip(cusip)
    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))


@app.route('/tips_prices')
def get_tips_prices():
    try:
        from backend.tips_data import get_tips_prices_wsj as get_prices
        price_data = get_prices()
        return dict(priceData=price_data)

    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

from flask import Flask, send_from_directory, request
from flask_caching import Cache
import logging

# Backend API
from backend import config as cfg
from backend import data

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

# configure logger
app.logger.setLevel(logging.DEBUG)

def process_form_data(form, json_str_keys):
    """Convert the Flask request.form to a dict and convert keys in json_str_keys to dicts."""
    from json import loads
    form_data = form.to_dict()
    for key in json_str_keys:
        if key in form_data:
            form_data[key] = loads(form_data[key])
    return form_data

def get_model(handle):
    """Return a Model object from the cache given a cache handle."""
    model = cache.get(handle)
    return model

@app.route('/')
def serve():
    return send_from_directory(app.static_folder,'index.html')

@app.route('/app_info')
def get_app_info():
    return cfg.get_app_info()

@app.route('/all_data_names')
def get_all_data_names():
    return dict(names=sorted([k for k in data.DATA_CONFIG.keys() if data.DATA_CONFIG[k]['DataViewer']]))

@app.route('/data/<name>')
# do not cache data, since same route is used for intraday
def get_data(name):
    try:
        app.logger.info('Request get_data(\'' + name + '\')')
        data_api = data.DataAPI(name)
        app.logger.debug('DataAPI(\''+ name + '\') returned ' + str(data_api))
        if data_api.cache:
            return get_cached_data(data_api)
        else:
            return get_uncached_data(data_api)
    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@cache.cached(timeout=3600)
def get_cached_data(data_api):
    return data_api.get_and_parse_data()

def get_uncached_data(data_api):
    return data_api.get_and_parse_data()

@app.route('/tips_cusips')
@cache.cached(timeout=1800)
def get_tips_cusips():
    try:
        from backend.tips_data import get_tips_cusips
        cusips = get_tips_cusips()
        return dict(cusips=cusips)

    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/all_tsy_reference_data')
@cache.cached(timeout=1800)
def get_all_tsy_reference_data():
    try:
        from backend.tips_data import get_all_tsy_reference_data
        ref_data = get_all_tsy_reference_data()
        bonds = {r['cusip']: r for r in ref_data}
        cusips = list(bonds.keys())
        return dict(referenceData=dict(cusips=cusips, bonds=bonds))
        
    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/tips_reference_data/<cusip>')
@cache.cached(timeout=1800)
def get_tips_reference_data(cusip):
    try:
        from backend.tips_data import get_treasury_reference_data
        reference_data = get_treasury_reference_data(cusip)
        return dict(referenceData=reference_data)

    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/tips_yield_data/<cusip>')
@cache.cached(timeout=1800)
def get_tips_yield_data(cusip):
    try:
        from backend.tips_data import get_tips_yield_data_by_cusip
        return get_tips_yield_data_by_cusip(cusip)
    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))


@app.route('/tips_prices')
@cache.cached(timeout=1800)
def get_tips_prices():
    try:
        from backend.tips_data import get_tips_prices_wsj as get_prices
        price_data = get_prices()
        return dict(priceData=price_data)

    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/build_model', methods=['POST'])
def build_model():
    try:
        from backend.models.modelfactory import ModelFactory
        params = process_form_data(request.form, ['model_data'])
        handle = params.get('handle', 'TempModel')
        model = ModelFactory.build(params)
        app.logger.info(f'Built model {handle}: {model}')

        # cache model
        is_set = cache.set(handle, model)
        if not is_set:
            raise RuntimeError(f'ModelFactory.build_and_cache: failed to set {model} in cache.')

        # gather results
        results_options = params.get('results_options') or {}
        results = model.get_all_results(**results_options)
        return dict(results=results)
    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))


@app.route('/supported_curve_data_point_types/<curve_type>')
def get_supproted_curve_data_point_types(curve_type):
    try:
        from backend.curveconstruction.curvedata import supported_curve_data_point_types
        supported_types = supported_curve_data_point_types(curve_type)
        return dict(choices=supported_types)

    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/get_build_settings_usage/<curve_type>')
def get_build_settings_usage(curve_type):
    try:
        from backend.buildsettings.buildsettings import get_usage_by_model
        usage = get_usage_by_model(curve_type)
        return dict(usage=usage)

    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

@app.route('/get_curve_templates')
def get_curve_templates():
    try:
        import os
        curve_template_folder = os.path.join(app.root_path, 'backend/curveconstruction/curve_templates/')
        curve_templates = [f[:-5] for f in os.listdir(curve_template_folder) 
                            if (os.path.isfile(os.path.join(curve_template_folder, f)) and f.endswith('.json'))]
        return dict(curve_templates=curve_templates)
    
    except Exception as e:
        app.logger.error(str(e))
        return dict(errors=str(e))

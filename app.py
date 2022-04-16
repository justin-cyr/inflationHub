from flask import Flask, send_from_directory

# Backend API
from backend import config as cfg
from backend import data

app = Flask(__name__, static_url_path='', static_folder='frontend/build')

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
        data_api = data.DataAPI(name)
        print(data_api)
        print(data_api.url_query())
        return data_api.get_and_parse_data()
    except Exception as e:
        return dict(errors=str(e))

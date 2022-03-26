from flask import Flask, send_from_directory

# Backend API
from backend import config as cfg

app = Flask(__name__, static_url_path='', static_folder='frontend/build')

@app.route('/')
def serve():
    return send_from_directory(app.static_folder,'index.html')

@app.route('/app_info')
def get_app_info():
    return cfg.get_app_info()

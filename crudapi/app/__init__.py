from flask import Flask
from .resources import api_bp
from . import urls
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['DEBUG'] = True
app.register_blueprint(api_bp, url_prefix='/api')

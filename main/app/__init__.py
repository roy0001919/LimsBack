from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['DEBUG'] = True

from .webhook import app_chatbot as api_chatbot_Blueprint
app.register_blueprint(api_chatbot_Blueprint)

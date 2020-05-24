from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
database = SQLAlchemy(app)
login_manager = LoginManager(app)


from app import routes


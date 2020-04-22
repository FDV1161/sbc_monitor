from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
database = SQLAlchemy(app)


from app import routes


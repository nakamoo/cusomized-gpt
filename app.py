import os

from flask import Flask

from flask_login import (
    LoginManager,
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"sqlite:///{os.path.join(basedir, os.environ.get('SQLITE_DB_PATH'))}"
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

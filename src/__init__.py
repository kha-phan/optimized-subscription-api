from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from src.models import User
from dotenv import load_dotenv
import os

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = db.session.query(User).filter_by(username=username).first()
    if not user:
        return None
    if check_password_hash(user.password, password):
        return user
    return None


@auth.error_handler
def auth_error():
    return {'message': 'Invalid credentials'}, 401

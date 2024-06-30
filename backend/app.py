import os

from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

basedir = os.path.abspath(os.path.dirname(__file__))
app = None
db = SQLAlchemy()
application = None

login_manager = LoginManager()
login_manager.session_protection = 'strong'
@login_manager.user_loader
def load_user(patient_id):
  from models import Patient
  return Patient.query.get(int(patient_id))

def create_app():
  global app
  global db
  global application
  app = Flask(__name__)

  app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  app.config["SESSION_COOKIE_SECURE"] = True
  app.config["SESSION_COOKIE_SAMESITE"] = 'None'

  cors = CORS(app, origins=[os.getenv("FRONTEND_ORIGIN")], supports_credentials=True)
  db = SQLAlchemy(app)
  migrate = Migrate(app, db)

  login_manager.init_app(app)
  application = app
  db.create_all()

  # Fixes CORS issue to allow for credentials to be sent from front end
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', os.getenv("FRONTEND_ORIGIN"))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

  from routes import sign_out, login, sign_up
  return app
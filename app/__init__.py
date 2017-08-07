import os
from flask import Flask, g
from config import basedir
from flask_login import LoginManager
from flask_mail import Mail
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)

mail = Mail(app)

login_manager = LoginManager()
login_manager.login_view
login_manager.init_app(app)
login_manager.login_view = "login"

from app import views

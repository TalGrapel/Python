from flask import Flask
from flask_sqlalchemy import SQLAlchemy

flask_app = Flask(__name__) #name of mudole

flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tal:1234@localhost/ecommerce'
flask_app.config['SECRET_KEY'] = 'talistheking'

db = SQLAlchemy(flask_app)

from app import routes

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('edu_db_string')
db = SQLAlchemy(app)

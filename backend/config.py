from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Read DATABASE_URL from the environment if provided; otherwise use local Postgres
database_url = os.environ.get("DATABASE_URL", "postgresql://gabriel@localhost:5432/contact_manager")

# Normalize legacy scheme if necessary
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
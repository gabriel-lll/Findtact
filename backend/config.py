from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)

# CORS configuration - allow both development and production origins
# In production with nginx proxy, requests come from same origin so CORS isn't strictly needed,
# but we keep it for flexibility and local development.
cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
).split(",")

CORS(
    app,
    origins=cors_origins,
    supports_credentials=False,
)

# Read DATABASE_URL from the environment if provided; otherwise use local Postgres
database_url = os.environ.get("DATABASE_URL", "postgresql://gabriel@localhost:5432/contact_manager")

# Normalize legacy scheme if necessary
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

# Specify the template and static folders relative to this file.
# __init__.py is in /app/, so "../templates" and "../static" point to /app/templates and /app/static.
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import modules so that routes, models, helpers, and workout are registered.
from app import routes, helpers, models  # add workout if you have one
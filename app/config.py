import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        # Log the environment variables for debugging (remove in production!)
        print("Current environment variables:", os.environ)
        raise ValueError("No DATABASE_URL set for Flask application")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
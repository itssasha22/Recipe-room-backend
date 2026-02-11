import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///recipe_room.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    PAYD_API_URL = "https://api.payd.money"
    PAYD_USERNAME = os.environ.get('PAYD_USERNAME')
    PAYD_PASSWORD = os.environ.get('PAYD_PASSWORD')
    PAYD_API_SECRET = os.environ.get('PAYD_API_SECRET')
    PAYD_ACCOUNT_USERNAME = os.environ.get('PAYD_ACCOUNT_USERNAME')
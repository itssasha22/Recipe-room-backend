from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

from models import db
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

from routes.auth import auth_bp
from routes.payments import payment_bp
from routes.search import search_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(payment_bp, url_prefix='/api/payments')
app.register_blueprint(search_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
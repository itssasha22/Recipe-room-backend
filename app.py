from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from dotenv import load_dotenv
from models import db

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    from routes.auth import auth_bp
    from routes.search import search_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(search_bp, url_prefix='/api')
    
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
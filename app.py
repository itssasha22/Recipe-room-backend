from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)
    CORS(app)
    
    from routes.auth import auth_bp
    from routes.search import search_bp
    from routes.recipes import recipe_bp
    from routes.groups import group_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(recipe_bp)  # /api/recipes prefix
    app.register_blueprint(group_bp)   # /api/groups prefix
    
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)


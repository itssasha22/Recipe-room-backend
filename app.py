from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from database import db
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://recipe-room-frontend.vercel.app"
]}})

from models import User, Recipe, Group, Bookmark, Rating, Comment, GroupInvitation

from routes.auth import auth_bp
from routes.payments import payment_bp
from routes.groups import groups_bp
from routes.recipes import recipes_bp
from routes.comments import comments_bp
from routes.ratings import ratings_bp
from routes.bookmarks import bookmarks_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(payment_bp, url_prefix='/api/payments')
app.register_blueprint(groups_bp, url_prefix='/api/groups')
app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
app.register_blueprint(comments_bp, url_prefix='/api/comments')
app.register_blueprint(ratings_bp, url_prefix='/api/ratings')
app.register_blueprint(bookmarks_bp, url_prefix='/api/bookmarks')

# Auto-initialize database on startup
with app.app_context():
    db.create_all()
    print("Database tables created successfully")

if __name__ == '__main__':
    app.run(debug=True)
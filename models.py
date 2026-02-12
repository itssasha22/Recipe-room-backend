from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat()
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payd_transaction_id = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='payments')

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    prep_time = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    servings = db.Column(db.Integer)
    country = db.Column(db.String(100))
    is_premium = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='recipes')
    group = db.relationship('Group', backref='recipes')
    comments = db.relationship('Comment', backref='recipe', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='recipe', lazy=True, cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='recipe', lazy=True, cascade='all, delete-orphan')
    
    def get_avg_rating(self):
        if not self.ratings:
            return 0
        return sum(r.rating for r in self.ratings) / len(self.ratings)
    
    def to_dict(self, include_stats=True):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'image_url': self.image_url,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'country': self.country,
            'is_premium': self.is_premium,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'created_at': self.created_at.isoformat(),
            'author': self.user.username if self.user else None
        }
        if include_stats:
            data['avg_rating'] = round(self.get_avg_rating(), 1)
            data['rating_count'] = len(self.ratings)
            data['comment_count'] = len(self.comments)
        return data

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    creator = db.relationship('User', backref='created_groups')
    members = db.relationship('GroupMember', backref='group', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'member_count': len(self.members)
        }

class GroupMember(db.Model):
    __tablename__ = 'group_members'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # 'owner', 'admin', 'member'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='group_memberships')
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'role': self.role,
            'joined_at': self.joined_at.isoformat()
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'recipe_id': self.recipe_id,
            'user_id': self.user_id,
            'author': self.user.username if self.user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='ratings')
    
    # Unique constraint: one rating per user per recipe
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_rating'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'recipe_id': self.recipe_id,
            'user_id': self.user_id,
            'author': self.user.username if self.user else None,
            'created_at': self.created_at.isoformat()
        }

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='bookmarks')
    
    # Unique constraint: one bookmark per user per recipe
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_bookmark'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }

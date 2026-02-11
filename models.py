from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True)  # Alias for compatibility
    username = db.Column(db.String(80), unique=True, nullable=False)
    user_username = db.Column(db.String(80))  # Alias for compatibility
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255))
    user_profile_image = db.Column(db.String(255))  # Alias for compatibility
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Keep user_id in sync with id
        self.user_id = self.id
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.id,
            'username': self.username,
            'email': self.email,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat()
        }

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    people_served = db.Column(db.Integer)
    country = db.Column(db.String(100), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='payments')


# ============================================================================
# RECIPE MODELS - Alex Maingi's Recipes CRUD & Group Recipes
# ============================================================================

# Association table: Recipe <-> RecipeGroup (which recipes belong to which groups)
recipe_group_members = db.Table('recipe_group_members',
    db.Column('rgm_id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('rgm_recipe_id', db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False),
    db.Column('rgm_group_id', db.Integer, db.ForeignKey('recipe_groups.group_id'), nullable=False),
    db.Column('rgm_added_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('rgm_added_by', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.UniqueConstraint('rgm_recipe_id', 'rgm_group_id', name='unique_recipe_group')
)

# Association table: User <-> RecipeGroup (which users belong to which groups)
group_memberships = db.Table('group_memberships',
    db.Column('gm_id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('gm_user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('gm_group_id', db.Integer, db.ForeignKey('recipe_groups.group_id'), nullable=False),
    db.Column('gm_joined_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('gm_role', db.String(50), default='member', nullable=False),  # 'owner', 'admin', 'member'
    db.UniqueConstraint('gm_user_id', 'gm_group_id', name='unique_user_group')
)


class Recipe(db.Model):
    """
    Main recipe model storing individual recipes.
    Prefix: recipe_ for all fields to avoid collisions
    """
    __tablename__ = 'recipes'
    
    # Primary key
    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Basic recipe information
    recipe_title = db.Column(db.String(200), nullable=False, index=True)
    recipe_description = db.Column(db.Text, nullable=True)
    recipe_country = db.Column(db.String(100), nullable=True, index=True)
    
    # Ingredients and procedure (stored as JSON for flexibility)
    recipe_ingredients = db.Column(db.JSON, nullable=False)  # List of ingredient objects
    recipe_procedure = db.Column(db.JSON, nullable=False)    # List of step objects
    
    # Servings and time metadata
    recipe_people_served = db.Column(db.Integer, nullable=False, index=True)
    recipe_prep_time = db.Column(db.Integer, nullable=True)  # In minutes
    recipe_cook_time = db.Column(db.Integer, nullable=True)  # In minutes
    
    # Image storage (Cloudinary URL)
    recipe_image_url = db.Column(db.String(500), nullable=True)
    recipe_image_public_id = db.Column(db.String(200), nullable=True)  # For Cloudinary deletion
    
    # Ownership and timestamps
    recipe_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    recipe_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete flag
    recipe_is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    recipe_owner = db.relationship('User', backref=db.backref('user_recipes', lazy='dynamic'))
    
    # Relationship to group recipes (many-to-many through association table)
    recipe_groups = db.relationship('RecipeGroup', secondary='recipe_group_members', 
                                   back_populates='group_recipes', lazy='dynamic')
    
    # Relationship to bookmarks (Joy's responsibility)
    recipe_bookmarks = db.relationship('Bookmark', backref='bookmarked_recipe', 
                                      lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Bookmark.recipe_id')
    
    # Relationship to ratings (Joy's responsibility)
    recipe_ratings = db.relationship('Rating', backref='rated_recipe', 
                                    lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Rating.recipe_id')
    
    # Relationship to comments (Derrick's responsibility)
    recipe_comments = db.relationship('Comment', backref='commented_recipe', 
                                     lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Comment.recipe_id')
    
    def __repr__(self):
        return f'<Recipe {self.recipe_id}: {self.recipe_title}>'
    
    def to_dict(self, include_owner=True, include_stats=True):
        """Convert recipe object to dictionary for JSON serialization."""
        recipe_data = {
            'recipe_id': self.recipe_id,
            'title': self.recipe_title,
            'description': self.recipe_description,
            'country': self.recipe_country,
            'ingredients': self.recipe_ingredients,
            'procedure': self.recipe_procedure,
            'people_served': self.recipe_people_served,
            'prep_time': self.recipe_prep_time,
            'cook_time': self.recipe_cook_time,
            'image_url': self.recipe_image_url,
            'created_at': self.recipe_created_at.isoformat() if self.recipe_created_at else None,
            'updated_at': self.recipe_updated_at.isoformat() if self.recipe_updated_at else None,
        }
        
        if include_owner and self.recipe_owner:
            recipe_data['owner'] = {
                'user_id': self.recipe_owner.id,
                'username': self.recipe_owner.username,
                'profile_image': getattr(self.recipe_owner, 'profile_image', None)
            }
        else:
            recipe_data['owner_id'] = self.recipe_owner_id
        
        if include_stats:
            recipe_data['stats'] = {
                'bookmarks_count': self.recipe_bookmarks.count() if hasattr(self, 'recipe_bookmarks') else 0,
                'comments_count': self.recipe_comments.count() if hasattr(self, 'recipe_comments') else 0,
                'average_rating': self._calculate_average_rating()
            }
        
        return recipe_data
    
    def _calculate_average_rating(self):
        """Calculate average rating for this recipe"""
        if not hasattr(self, 'recipe_ratings'):
            return 0.0
        ratings = self.recipe_ratings.all()
        if not ratings:
            return 0.0
        return round(sum(r.rating_value for r in ratings) / len(ratings), 2)


class RecipeGroup(db.Model):
    """
    Model for group recipe collaboration (WhatsApp-like feature).
    Allows multiple users to collaboratively create/edit recipes.
    """
    __tablename__ = 'recipe_groups'
    
    # Primary key
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Group metadata
    group_name = db.Column(db.String(200), nullable=False)
    group_description = db.Column(db.Text, nullable=True)
    group_image_url = db.Column(db.String(500), nullable=True)  # Optional group avatar
    
    # Ownership
    group_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    group_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Group settings
    group_is_active = db.Column(db.Boolean, default=True, nullable=False)
    group_max_members = db.Column(db.Integer, default=10, nullable=False)  # Limit group size
    
    # Relationships
    group_owner = db.relationship('User', backref=db.backref('owned_groups', lazy='dynamic'), foreign_keys=[group_owner_id])
    
    # Many-to-many relationship with recipes
    group_recipes = db.relationship('Recipe', secondary='recipe_group_members', 
                                   back_populates='recipe_groups', lazy='dynamic')
    
    # Many-to-many relationship with users (group members)
    group_members = db.relationship('User', secondary='group_memberships', 
                                   backref=db.backref('joined_groups', lazy='dynamic'))
    
    def __repr__(self):
        return f'<RecipeGroup {self.group_id}: {self.group_name}>'
    
    def to_dict(self, include_members=False, include_recipes=False):
        """Convert group to dictionary with optional related data"""
        group_data = {
            'group_id': self.group_id,
            'name': self.group_name,
            'description': self.group_description,
            'image_url': self.group_image_url,
            'owner_id': self.group_owner_id,
            'created_at': self.group_created_at.isoformat(),
            'updated_at': self.group_updated_at.isoformat(),
            'is_active': self.group_is_active,
            'max_members': self.group_max_members,
            'members_count': len(self.group_members)
        }
        
        if include_members:
            group_data['members'] = [
                {
                    'user_id': member.id,
                    'username': member.username,
                    'profile_image': getattr(member, 'profile_image', None)
                }
                for member in self.group_members
            ]
        
        if include_recipes:
            group_data['recipes'] = [
                recipe.to_dict(include_owner=False, include_stats=False) 
                for recipe in self.group_recipes.all()
            ]
        
        return group_data
    
    def is_member(self, user_id):
        """Check if a user is a member of this group"""
        return any(member.id == user_id for member in self.group_members)
    
    def is_owner(self, user_id):
        """Check if a user is the owner of this group"""
        return self.group_owner_id == user_id
    
    def can_add_members(self):
        """Check if group can accept more members"""
        return len(self.group_members) < self.group_max_members


class RecipeEditHistory(db.Model):
    """
    Track edit history for group recipes.
    Allows us to show who edited what and when.
    """
    __tablename__ = 'recipe_edit_history'
    
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    history_recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    history_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    history_action = db.Column(db.String(50), nullable=False)  # 'created', 'updated', 'deleted'
    history_changes = db.Column(db.JSON, nullable=True)  # What fields were changed
    history_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    history_recipe = db.relationship('Recipe', backref=db.backref('edit_history', lazy='dynamic'))
    history_user = db.relationship('User', backref=db.backref('recipe_edits', lazy='dynamic'))
    
    def __repr__(self):
        return f'<RecipeEditHistory {self.history_id}: {self.history_action} by User {self.history_user_id}>'
    
    def to_dict(self):
        return {
            'history_id': self.history_id,
            'recipe_id': self.history_recipe_id,
            'user_id': self.history_user_id,
            'action': self.history_action,
            'changes': self.history_changes,
            'timestamp': self.history_timestamp.isoformat()
        }


# Placeholder classes for forward references (to be defined by team members)
class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating_value = db.Column(db.Integer, nullable=False)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from models import db, User, Recipe, Comment
from routes.comments import comments_bp
import json

@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    db.init_app(app)
    app.register_blueprint(comments_bp, url_prefix='/api/comments')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_recipe(app, test_user):
    """Create a test recipe"""
    with app.app_context():
        recipe = Recipe(
            title='Test Recipe',
            description='A test recipe',
            ingredients='Ingredient 1, Ingredient 2',
            instructions='Step 1, Step 2',
            servings=4,
            user_id=test_user.id
        )
        db.session.add(recipe)
        db.session.commit()
        return recipe

@pytest.fixture
def auth_headers(app, test_user):
    """Create authentication headers"""
    with app.app_context():
        access_token = create_access_token(identity=test_user.id)
        return {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

class TestCommentEndpoints:
    """Test suite for comment endpoints"""
    
    def test_get_comments_empty(self, client, test_recipe):
        """Test getting comments when none exist"""
        response = client.get(f'/api/comments/{test_recipe.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['total'] == 0
        assert len(data['data']['items']) == 0
    
    def test_create_comment_success(self, client, test_recipe, auth_headers):
        """Test creating a comment successfully"""
        response = client.post(
            f'/api/comments/{test_recipe.id}',
            data=json.dumps({'content': 'Great recipe!'}),
            headers=auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['content'] == 'Great recipe!'
        assert data['message'] == 'Comment created successfully'
    
    def test_create_comment_without_auth(self, client, test_recipe):
        """Test creating a comment without authentication"""
        response = client.post(
            f'/api/comments/{test_recipe.id}',
            data=json.dumps({'content': 'Great recipe!'}),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 401
    
    def test_create_comment_empty_content(self, client, test_recipe, auth_headers):
        """Test creating a comment with empty content"""
        response = client.post(
            f'/api/comments/{test_recipe.id}',
            data=json.dumps({'content': ''}),
            headers=auth_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'required' in data['error'].lower()
    
    def test_create_comment_too_long(self, client, test_recipe, auth_headers):
        """Test creating a comment that exceeds max length"""
        long_content = 'A' * 1001
        response = client.post(
            f'/api/comments/{test_recipe.id}',
            data=json.dumps({'content': long_content}),
            headers=auth_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '1000' in data['error']
    
    def test_create_comment_xss_protection(self, client, test_recipe, auth_headers):
        """Test that XSS attacks are prevented"""
        malicious_content = '<script>alert("XSS")</script>Safe content'
        response = client.post(
            f'/api/comments/{test_recipe.id}',
            data=json.dumps({'content': malicious_content}),
            headers=auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert '<script>' not in data['data']['content']
        assert 'Safe content' in data['data']['content']
    
    def test_get_comments_with_pagination(self, client, app, test_recipe, test_user, auth_headers):
        """Test getting comments with pagination"""
        # Create multiple comments
        with app.app_context():
            for i in range(25):
                comment = Comment(
                    content=f'Comment {i}',
                    user_id=test_user.id,
                    recipe_id=test_recipe.id
                )
                db.session.add(comment)
            db.session.commit()
        
        # Test first page
        response = client.get(f'/api/comments/{test_recipe.id}?page=1&per_page=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']['items']) == 10
        assert data['data']['total'] == 25
        assert data['data']['pages'] == 3
        assert data['data']['has_next'] is True
        
        # Test second page
        response = client.get(f'/api/comments/{test_recipe.id}?page=2&per_page=10')
        data = json.loads(response.data)
        assert len(data['data']['items']) == 10
        assert data['data']['has_prev'] is True
    
    def test_update_comment_success(self, client, app, test_recipe, test_user, auth_headers):
        """Test updating own comment"""
        # Create comment
        with app.app_context():
            comment = Comment(
                content='Original content',
                user_id=test_user.id,
                recipe_id=test_recipe.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # Update comment
        response = client.put(
            f'/api/comments/{comment_id}',
            data=json.dumps({'content': 'Updated content'}),
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['content'] == 'Updated content'
    
    def test_update_comment_unauthorized(self, client, app, test_recipe, auth_headers):
        """Test updating someone else's comment"""
        # Create another user and their comment
        with app.app_context():
            other_user = User(username='otheruser', email='other@example.com')
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()
            
            comment = Comment(
                content='Other user comment',
                user_id=other_user.id,
                recipe_id=test_recipe.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # Try to update
        response = client.put(
            f'/api/comments/{comment_id}',
            data=json.dumps({'content': 'Hacked content'}),
            headers=auth_headers
        )
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Unauthorized' in data['error']
    
    def test_delete_comment_success(self, client, app, test_recipe, test_user, auth_headers):
        """Test deleting own comment"""
        # Create comment
        with app.app_context():
            comment = Comment(
                content='To be deleted',
                user_id=test_user.id,
                recipe_id=test_recipe.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # Delete comment
        response = client.delete(
            f'/api/comments/{comment_id}',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'deleted' in data['message'].lower()
    
    def test_delete_comment_unauthorized(self, client, app, test_recipe, auth_headers):
        """Test deleting someone else's comment"""
        # Create another user and their comment
        with app.app_context():
            other_user = User(username='otheruser2', email='other2@example.com')
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()
            
            comment = Comment(
                content='Other user comment',
                user_id=other_user.id,
                recipe_id=test_recipe.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # Try to delete
        response = client.delete(
            f'/api/comments/{comment_id}',
            headers=auth_headers
        )
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Unauthorized' in data['error']
    
    def test_comment_nonexistent_recipe(self, client, auth_headers):
        """Test commenting on non-existent recipe"""
        response = client.post(
            '/api/comments/99999',
            data=json.dumps({'content': 'Comment on nothing'}),
            headers=auth_headers
        )
        assert response.status_code == 404

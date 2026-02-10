import pytest
from utils import (
    sanitize_html,
    validate_comment_content,
    paginate_results,
    standardize_error,
    standardize_response
)
from flask import Flask
from models import db, User, Comment, Recipe

class TestUtilityFunctions:
    """Test suite for utility functions"""
    
    def test_sanitize_html_removes_scripts(self):
        """Test that script tags are removed"""
        dirty = '<script>alert("XSS")</script>Hello'
        clean = sanitize_html(dirty)
        assert '<script>' not in clean
        assert 'Hello' in clean
    
    def test_sanitize_html_allows_basic_tags(self):
        """Test that basic formatting tags are allowed"""
        text = '<b>Bold</b> <i>Italic</i> <em>Emphasis</em>'
        clean = sanitize_html(text)
        assert '<b>Bold</b>' in clean
        assert '<i>Italic</i>' in clean
        assert '<em>Emphasis</em>' in clean
    
    def test_sanitize_html_removes_dangerous_tags(self):
        """Test that dangerous tags are removed"""
        dangerous = '<script>bad()</script><iframe>bad</iframe><object>bad</object>Safe'
        clean = sanitize_html(dangerous)
        assert '<script>' not in clean
        assert '<iframe>' not in clean
        assert '<object>' not in clean
        assert 'Safe' in clean
    
    def test_sanitize_html_handles_none(self):
        """Test handling of None input"""
        assert sanitize_html(None) is None
    
    def test_validate_comment_content_success(self):
        """Test validating valid comment content"""
        is_valid, result = validate_comment_content('This is a valid comment')
        assert is_valid is True
        assert result == 'This is a valid comment'
    
    def test_validate_comment_content_strips_whitespace(self):
        """Test that whitespace is stripped"""
        is_valid, result = validate_comment_content('  Hello  ')
        assert is_valid is True
        assert result == 'Hello'
    
    def test_validate_comment_content_empty(self):
        """Test validation of empty content"""
        is_valid, error = validate_comment_content('')
        assert is_valid is False
        assert 'required' in error.lower()
    
    def test_validate_comment_content_none(self):
        """Test validation of None content"""
        is_valid, error = validate_comment_content(None)
        assert is_valid is False
        assert 'required' in error.lower()
    
    def test_validate_comment_content_whitespace_only(self):
        """Test validation of whitespace-only content"""
        is_valid, error = validate_comment_content('   ')
        assert is_valid is False
        assert 'required' in error.lower()
    
    def test_validate_comment_content_too_long(self):
        """Test validation of content exceeding max length"""
        long_content = 'A' * 1001
        is_valid, error = validate_comment_content(long_content)
        assert is_valid is False
        assert '1000' in error
    
    def test_validate_comment_content_max_length(self):
        """Test validation at exactly max length"""
        max_content = 'A' * 1000
        is_valid, result = validate_comment_content(max_content)
        assert is_valid is True
        assert len(result) == 1000
    
    def test_standardize_error_format(self):
        """Test error response standardization"""
        response, status = standardize_error('Test error', 400)
        data = response.get_json()
        
        assert status == 400
        assert data['success'] is False
        assert data['error'] == 'Test error'
        assert data['status_code'] == 400
    
    def test_standardize_error_with_details(self):
        """Test error response with additional details"""
        errors = {'field1': 'error1', 'field2': 'error2'}
        response, status = standardize_error('Validation failed', 422, errors)
        data = response.get_json()
        
        assert data['success'] is False
        assert data['errors'] == errors
    
    def test_standardize_response_success(self):
        """Test success response standardization"""
        test_data = {'id': 1, 'name': 'Test'}
        response, status = standardize_response(test_data, 'Success message', 200)
        data = response.get_json()
        
        assert status == 200
        assert data['success'] is True
        assert data['data'] == test_data
        assert data['message'] == 'Success message'
    
    def test_standardize_response_without_message(self):
        """Test success response without message"""
        test_data = {'id': 1}
        response, status = standardize_response(test_data)
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data'] == test_data
        assert 'message' not in data


@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestPaginationUtility:
    """Test pagination utility function"""
    
    def test_paginate_results_first_page(self, app):
        """Test pagination on first page"""
        with app.app_context():
            # Create test data
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            recipe = Recipe(
                title='Test Recipe',
                ingredients='Test',
                instructions='Test',
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()
            
            # Create 25 comments
            for i in range(25):
                comment = Comment(
                    content=f'Comment {i}',
                    user_id=user.id,
                    recipe_id=recipe.id
                )
                db.session.add(comment)
            db.session.commit()
            
            # Test pagination
            query = Comment.query.order_by(Comment.id)
            result = paginate_results(query, page=1, per_page=10)
            
            assert result is not None
            assert len(result['items']) == 10
            assert result['total'] == 25
            assert result['page'] == 1
            assert result['per_page'] == 10
            assert result['pages'] == 3
            assert result['has_next'] is True
            assert result['has_prev'] is False
    
    def test_paginate_results_last_page(self, app):
        """Test pagination on last page"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            recipe = Recipe(
                title='Test Recipe',
                ingredients='Test',
                instructions='Test',
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()
            
            for i in range(25):
                comment = Comment(
                    content=f'Comment {i}',
                    user_id=user.id,
                    recipe_id=recipe.id
                )
                db.session.add(comment)
            db.session.commit()
            
            query = Comment.query.order_by(Comment.id)
            result = paginate_results(query, page=3, per_page=10)
            
            assert len(result['items']) == 5
            assert result['has_next'] is False
            assert result['has_prev'] is True
    
    def test_paginate_results_invalid_page(self, app):
        """Test pagination with invalid page number"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            recipe = Recipe(
                title='Test Recipe',
                ingredients='Test',
                instructions='Test',
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()
            
            query = Comment.query.order_by(Comment.id)
            result = paginate_results(query, page='invalid', per_page=10)
            
            assert result is None
    
    def test_paginate_results_enforces_limits(self, app):
        """Test that pagination enforces reasonable limits"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            recipe = Recipe(
                title='Test Recipe',
                ingredients='Test',
                instructions='Test',
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()
            
            # Test max per_page limit
            query = Comment.query.order_by(Comment.id)
            result = paginate_results(query, page=1, per_page=200)
            
            assert result['per_page'] == 100  # Should be clamped to max

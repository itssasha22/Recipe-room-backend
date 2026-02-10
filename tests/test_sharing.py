import pytest
from flask import Flask
from models import db, User, Recipe
from routes.recipes import recipes_bp
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
    app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    
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
            title='Delicious Pasta',
            description='A wonderful Italian pasta dish that everyone loves',
            ingredients='Pasta, Tomato Sauce, Cheese',
            instructions='Boil pasta, Add sauce, Sprinkle cheese',
            image_url='https://example.com/pasta.jpg',
            prep_time=15,
            cook_time=30,
            servings=4,
            difficulty='medium',
            user_id=test_user.id
        )
        db.session.add(recipe)
        db.session.commit()
        return recipe

class TestSharingMetadata:
    """Test suite for social sharing metadata endpoint"""
    
    def test_get_share_metadata_success(self, client, test_recipe):
        """Test getting share metadata for a recipe"""
        response = client.get(f'/api/recipes/{test_recipe.id}/share-metadata')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['title'] == 'Delicious Pasta'
        assert 'Italian pasta' in data['description']
        assert data['image'] == 'https://example.com/pasta.jpg'
        assert data['type'] == 'recipe'
        assert data['prep_time'] == 15
        assert data['cook_time'] == 30
        assert data['servings'] == 4
        assert data['difficulty'] == 'medium'
        assert data['author'] == 'testuser'
    
    def test_share_metadata_has_og_tags(self, client, test_recipe):
        """Test that Open Graph tags are included"""
        response = client.get(f'/api/recipes/{test_recipe.id}/share-metadata')
        data = json.loads(response.data)
        
        assert 'og' in data
        assert data['og']['og:title'] == 'Delicious Pasta'
        assert data['og']['og:type'] == 'article'
        assert data['og']['og:site_name'] == 'Recipe Room'
        assert 'og:image' in data['og']
        assert 'og:url' in data['og']
    
    def test_share_metadata_has_twitter_tags(self, client, test_recipe):
        """Test that Twitter Card tags are included"""
        response = client.get(f'/api/recipes/{test_recipe.id}/share-metadata')
        data = json.loads(response.data)
        
        assert 'twitter' in data
        assert data['twitter']['twitter:card'] == 'summary_large_image'
        assert data['twitter']['twitter:title'] == 'Delicious Pasta'
        assert 'twitter:image' in data['twitter']
    
    def test_share_metadata_has_structured_data(self, client, test_recipe):
        """Test that structured data (schema.org) is included"""
        response = client.get(f'/api/recipes/{test_recipe.id}/share-metadata')
        data = json.loads(response.data)
        
        assert 'structured_data' in data
        sd = data['structured_data']
        assert sd['@type'] == 'Recipe'
        assert sd['name'] == 'Delicious Pasta'
        assert sd['prepTime'] == 'PT15M'
        assert sd['cookTime'] == 'PT30M'
        assert sd['recipeYield'] == '4'
        assert sd['author']['@type'] == 'Person'
        assert sd['author']['name'] == 'testuser'
    
    def test_share_metadata_truncates_long_description(self, client, app, test_user):
        """Test that long descriptions are truncated"""
        with app.app_context():
            long_recipe = Recipe(
                title='Test Recipe',
                description='A' * 250,  # Very long description
                ingredients='Test',
                instructions='Test',
                user_id=test_user.id
            )
            db.session.add(long_recipe)
            db.session.commit()
            recipe_id = long_recipe.id
        
        response = client.get(f'/api/recipes/{recipe_id}/share-metadata')
        data = json.loads(response.data)
        
        assert len(data['description']) <= 200
        assert data['description'].endswith('...')
    
    def test_share_metadata_handles_missing_fields(self, client, app, test_user):
        """Test metadata generation with minimal recipe data"""
        with app.app_context():
            minimal_recipe = Recipe(
                title='Minimal Recipe',
                ingredients='Test',
                instructions='Test',
                user_id=test_user.id
            )
            db.session.add(minimal_recipe)
            db.session.commit()
            recipe_id = minimal_recipe.id
        
        response = client.get(f'/api/recipes/{recipe_id}/share-metadata')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['title'] == 'Minimal Recipe'
        assert 'recipe' in data['description'].lower()
        assert data['prep_time'] is None
        assert data['cook_time'] is None
    
    def test_share_metadata_nonexistent_recipe(self, client):
        """Test getting metadata for non-existent recipe"""
        response = client.get('/api/recipes/99999/share-metadata')
        assert response.status_code == 404

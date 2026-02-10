from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Recipe, User
import cloudinary.uploader

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return jsonify([recipe.to_dict() for recipe in recipes])

@recipes_bp.route('/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return jsonify(recipe.to_dict())

@recipes_bp.route('/<int:recipe_id>/share-metadata', methods=['GET'])
def get_share_metadata(recipe_id):
    """Get rich metadata for social sharing (Open Graph, Twitter Cards)"""
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Build sharing URL
    sharing_url = f"{request.host_url}recipes/{recipe_id}"
    
    # Create description
    description = recipe.description or f"Check out this {recipe.difficulty or 'delicious'} recipe!"
    if len(description) > 200:
        description = description[:197] + '...'
    
    # Build metadata for multiple platforms
    metadata = {
        # Basic info
        'title': recipe.title,
        'description': description,
        'image': recipe.image_url,
        'url': sharing_url,
        'type': 'recipe',
        
        # Recipe details
        'prep_time': recipe.prep_time,
        'cook_time': recipe.cook_time,
        'servings': recipe.servings,
        'difficulty': recipe.difficulty,
        'author': recipe.user.username if recipe.user else 'Anonymous',
        
        # Open Graph tags
        'og': {
            'og:title': recipe.title,
            'og:description': description,
            'og:image': recipe.image_url,
            'og:url': sharing_url,
            'og:type': 'article',
            'og:site_name': 'Recipe Room',
        },
        
        # Twitter Card tags
        'twitter': {
            'twitter:card': 'summary_large_image',
            'twitter:title': recipe.title,
            'twitter:description': description,
            'twitter:image': recipe.image_url,
        },
        
        # Structured data for sharing
        'structured_data': {
            '@context': 'https://schema.org',
            '@type': 'Recipe',
            'name': recipe.title,
            'description': description,
            'image': recipe.image_url,
            'prepTime': f"PT{recipe.prep_time}M" if recipe.prep_time else None,
            'cookTime': f"PT{recipe.cook_time}M" if recipe.cook_time else None,
            'recipeYield': str(recipe.servings) if recipe.servings else None,
            'author': {
                '@type': 'Person',
                'name': recipe.user.username if recipe.user else 'Anonymous'
            }
        }
    }
    
    return jsonify(metadata)

@recipes_bp.route('', methods=['POST'])
@jwt_required()
def create_recipe():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['title', 'ingredients', 'instructions']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    recipe = Recipe(
        title=data['title'],
        description=data.get('description'),
        ingredients=data['ingredients'],
        instructions=data['instructions'],
        image_url=data.get('image_url'),
        prep_time=data.get('prep_time'),
        cook_time=data.get('cook_time'),
        servings=data.get('servings'),
        difficulty=data.get('difficulty'),
        is_premium=data.get('is_premium', False),
        user_id=user_id
    )
    
    db.session.add(recipe)
    db.session.commit()
    
    return jsonify(recipe.to_dict()), 201

@recipes_bp.route('/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id):
    user_id = get_jwt_identity()
    recipe = Recipe.query.get_or_404(recipe_id)
    
    if recipe.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    for field in ['title', 'description', 'ingredients', 'instructions', 'image_url', 'prep_time', 'cook_time', 'servings', 'difficulty', 'is_premium']:
        if field in data:
            setattr(recipe, field, data[field])
    
    db.session.commit()
    return jsonify(recipe.to_dict())

@recipes_bp.route('/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    user_id = get_jwt_identity()
    recipe = Recipe.query.get_or_404(recipe_id)
    
    if recipe.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(recipe)
    db.session.commit()
    
    return jsonify({'message': 'Recipe deleted'}), 200
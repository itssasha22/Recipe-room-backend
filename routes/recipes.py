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
    recipe = Recipe.query.get_or_404(recipe_id)
    
    metadata = {
        'title': recipe.title,
        'description': recipe.description or f"Check out this {recipe.difficulty or 'delicious'} recipe!",
        'image': recipe.image_url,
        'url': f"{request.host_url}recipes/{recipe_id}",
        'type': 'recipe',
        'prep_time': recipe.prep_time,
        'cook_time': recipe.cook_time,
        'servings': recipe.servings,
        'author': recipe.user.username if recipe.user else 'Anonymous'
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
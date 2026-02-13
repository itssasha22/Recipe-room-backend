from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Recipe, User
from sqlalchemy import or_, and_, func

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('', methods=['GET'])
def get_recipes():
    search = request.args.get('search', '').strip()
    country = request.args.get('country', '').strip()
    min_rating = request.args.get('min_rating', type=float)
    max_servings = request.args.get('max_servings', type=int)
    ingredient = request.args.get('ingredient', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    
    query = Recipe.query
    
    if search:
        query = query.filter(Recipe.title.ilike(f'%{search}%'))
    
    if country:
        query = query.filter(Recipe.country.ilike(f'%{country}%'))
    
    if max_servings:
        query = query.filter(Recipe.servings <= max_servings)
    
    if ingredient:
        query = query.filter(Recipe.ingredients.ilike(f'%{ingredient}%'))
    
    recipes = query.all()
    recipes_data = [recipe.to_dict(include_stats=True) for recipe in recipes]
    
    if min_rating:
        recipes_data = [r for r in recipes_data if r['avg_rating'] >= min_rating]
    
    if sort_by == 'rating':
        recipes_data.sort(key=lambda x: x['avg_rating'], reverse=True)
    elif sort_by == 'title':
        recipes_data.sort(key=lambda x: x['title'])
    else:
        recipes_data.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(recipes_data), 200

@recipes_bp.route('', methods=['POST'])
@jwt_required()
def create_recipe():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        recipe = Recipe(
            title=data['title'],
            description=data.get('description', ''),
            ingredients=data['ingredients'],
            instructions=data['instructions'],
            image_url=data.get('image_url'),
            prep_time=data.get('prep_time'),
            cook_time=data.get('cook_time'),
            servings=data.get('servings'),
            country=data.get('country'),
            is_premium=data.get('is_premium', False),
            group_id=data.get('group_id'),
            user_id=user_id
        )
        
        db.session.add(recipe)
        db.session.commit()
        
        return jsonify(recipe.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        return jsonify(recipe.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id):
    try:
        user_id = int(get_jwt_identity())
        recipe = Recipe.query.get_or_404(recipe_id)
        
        if recipe.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        if 'title' in data:
            recipe.title = data['title']
        if 'description' in data:
            recipe.description = data['description']
        if 'ingredients' in data:
            recipe.ingredients = data['ingredients']
        if 'instructions' in data:
            recipe.instructions = data['instructions']
        if 'image_url' in data:
            recipe.image_url = data['image_url']
        if 'prep_time' in data:
            recipe.prep_time = data['prep_time']
        if 'cook_time' in data:
            recipe.cook_time = data['cook_time']
        if 'servings' in data:
            recipe.servings = data['servings']
        if 'country' in data:
            recipe.country = data['country']
        if 'is_premium' in data:
            recipe.is_premium = data['is_premium']
        
        db.session.commit()
        return jsonify(recipe.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    try:
        user_id = int(get_jwt_identity())
        recipe = Recipe.query.get_or_404(recipe_id)
        
        if recipe.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({'message': 'Recipe deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_recipes(user_id):
    try:
        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return jsonify([recipe.to_dict() for recipe in recipes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

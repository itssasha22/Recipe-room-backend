from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models import db, Recipe, Rating, Bookmark

search_bp = Blueprint('search', __name__)

@search_bp.route('/recipes/discover', methods=['GET'])
def discover_recipes():
    query = Recipe.query
    
    if name := request.args.get('name'):
        query = query.filter(Recipe.name.ilike(f'%{name}%'))
    
    if ingredient := request.args.get('ingredient'):
        query = query.filter(Recipe.ingredients.ilike(f'%{ingredient}%'))
    
    if people := request.args.get('people_served'):
        query = query.filter(Recipe.people_served == int(people))
    
    if country := request.args.get('country'):
        query = query.filter(Recipe.country == country)
    
    if rating := request.args.get('rating'):
        query = query.join(Rating).group_by(Recipe.id).having(func.avg(Rating.value) >= float(rating))
    
    recipes = query.all()
    return jsonify([{'id': r.id, 'name': r.name, 'country': r.country, 'people_served': r.people_served} for r in recipes]), 200


@search_bp.route('/recipes/<int:recipe_id>/rate', methods=['POST'])
@jwt_required()
def rate_recipe(recipe_id):
    user_id = get_jwt_identity()
    value = request.json.get('value')
    
    if value not in range(1, 6):
        return {'error': 'Rating must be 1-5'}, 400
    
    rating = Rating.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if rating:
        rating.value = value
    else:
        db.session.add(Rating(user_id=user_id, recipe_id=recipe_id, value=value))
    
    db.session.commit()
    return {'message': 'Rating saved'}, 200


@search_bp.route('/recipes/<int:recipe_id>/rating', methods=['GET'])
def get_rating(recipe_id):
    avg = db.session.query(func.avg(Rating.value)).filter(Rating.recipe_id == recipe_id).scalar()
    count = Rating.query.filter_by(recipe_id=recipe_id).count()
    return {'average': round(avg or 0, 1), 'count': count}, 200


@search_bp.route('/recipes/<int:recipe_id>/bookmark', methods=['POST'])
@jwt_required()
def bookmark_recipe(recipe_id):
    user_id = get_jwt_identity()
    
    if Bookmark.query.filter_by(user_id=user_id, recipe_id=recipe_id).first():
        return {'message': 'Already bookmarked'}, 200
    
    db.session.add(Bookmark(user_id=user_id, recipe_id=recipe_id))
    db.session.commit()
    return {'message': 'Bookmarked'}, 201


@search_bp.route('/recipes/<int:recipe_id>/bookmark', methods=['DELETE'])
@jwt_required()
def remove_bookmark(recipe_id):
    Bookmark.query.filter_by(user_id=get_jwt_identity(), recipe_id=recipe_id).delete()
    db.session.commit()
    return {'message': 'Bookmark removed'}, 200

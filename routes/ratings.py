from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Rating, Recipe

ratings_bp = Blueprint('ratings', __name__)

@ratings_bp.route('/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe_ratings(recipe_id):
    """Get all ratings for a specific recipe"""
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        ratings = Rating.query.filter_by(recipe_id=recipe_id).all()
        
        avg_rating = recipe.get_avg_rating()
        rating_count = len(ratings)
        
        return jsonify({
            'avg_rating': round(avg_rating, 1),
            'rating_count': rating_count,
            'ratings': [rating.to_dict() for rating in ratings]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ratings_bp.route('', methods=['POST'])
@jwt_required()
def create_or_update_rating():
    """Create or update a rating for a recipe"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data.get('recipe_id') or not data.get('rating'):
            return jsonify({'error': 'recipe_id and rating are required'}), 400
        
        rating_value = data['rating']
        if not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
            return jsonify({'error': 'rating must be an integer between 1 and 5'}), 400
        
        # Verify recipe exists
        recipe = Recipe.query.get_or_404(data['recipe_id'])
        
        # Check if user already rated this recipe
        existing_rating = Rating.query.filter_by(
            user_id=user_id,
            recipe_id=data['recipe_id']
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            db.session.commit()
            return jsonify(existing_rating.to_dict()), 200
        else:
            # Create new rating
            rating = Rating(
                rating=rating_value,
                recipe_id=data['recipe_id'],
                user_id=user_id
            )
            db.session.add(rating)
            db.session.commit()
            return jsonify(rating.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ratings_bp.route('/<int:rating_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(rating_id):
    """Delete a rating (only by the rating author)"""
    try:
        user_id = int(get_jwt_identity())
        rating = Rating.query.get_or_404(rating_id)
        
        if rating.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(rating)
        db.session.commit()
        return jsonify({'message': 'Rating deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ratings_bp.route('/user/<int:recipe_id>', methods=['GET'])
@jwt_required()
def get_user_rating(recipe_id):
    """Get the current user's rating for a specific recipe"""
    try:
        user_id = int(get_jwt_identity())
        rating = Rating.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        
        if rating:
            return jsonify(rating.to_dict()), 200
        else:
            return jsonify({'rating': None}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

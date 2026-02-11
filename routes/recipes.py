"""
Recipe-Room Backend - Recipe Routes
Author: Alex Maingi
Role: Recipes CRUD & Group Recipes

Flask Blueprint for all recipe-related API endpoints.
Prefix: /api/recipes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Import models
from models import Recipe, RecipeGroup, RecipeEditHistory, recipe_group_members, group_memberships
from database import db
from utils import validate_recipe_data, upload_image_to_cloudinary, delete_image_from_cloudinary
#setting up the blueprint
recipe_bp = Blueprint('recipes', __name__, url_prefix='/api/recipes')
#recipe endpoints
@recipe_bp.route('/', methods=['GET'])
def get_all_recipes():
    """
    Get all recipes with optional pagination.
    Query params: page (default 1), per_page (default 20)
    Public endpoint - no authentication required
    """
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Ensure reasonable limits
        per_page = min(per_page, 100)  # Max 100 items per page
        
        # Query non-deleted recipes, ordered by creation date (newest first)
        recipes_query = Recipe.query.filter_by(recipe_is_deleted=False).order_by(
            Recipe.recipe_created_at.desc()
        )
        
        # Paginate results
        paginated_recipes = recipes_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Convert to dict
        recipes_list = [
            recipe.to_dict(include_owner=True, include_stats=True) 
            for recipe in paginated_recipes.items
        ]
        
        return jsonify({
            'success': True,
            'recipes': recipes_list,
            'pagination': {
                'current_page': paginated_recipes.page,
                'total_pages': paginated_recipes.pages,
                'total_items': paginated_recipes.total,
                'per_page': per_page,
                'has_next': paginated_recipes.has_next,
                'has_prev': paginated_recipes.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve recipes',
            'message': str(e)
        }), 500
@recipe_bp.route('/<int:recipe_id>', methods=['GET'])
def get_recipe_by_id(recipe_id):
    """
    Get a single recipe by ID.
    Public endpoint - no authentication required
    """
    try:
        # Find recipe
        recipe = Recipe.query.filter_by(
            recipe_id=recipe_id, 
            recipe_is_deleted=False
        ).first()
        
        if not recipe:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        # Return detailed recipe info
        return jsonify({
            'success': True,
            'recipe': recipe.to_dict(include_owner=True, include_stats=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve recipe',
            'message': str(e)
        }), 500
@recipe_bp.route('/', methods=['POST'])
@jwt_required()
def create_recipe():
    """
    Create a new recipe.
    Requires authentication.
    """
    try:
        # Get current user ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        validation_error = validate_recipe_data(data)
        if validation_error:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'message': validation_error
            }), 400
        
        # Handle image upload to Cloudinary (if provided)
        image_url = None
        image_public_id = None
        if 'image' in data and data['image']:
            try:
                upload_result = upload_image_to_cloudinary(
                    data['image'], 
                    folder='recipe_images'
                )
                image_url = upload_result.get('secure_url')
                image_public_id = upload_result.get('public_id')
            except Exception as img_error:
                # Don't fail the whole request if image upload fails
                print(f"Image upload failed: {img_error}")
        
        # Create new recipe
        new_recipe = Recipe(
            recipe_title=data['title'],
            recipe_description=data.get('description'),
            recipe_country=data.get('country'),
            recipe_ingredients=data['ingredients'],
            recipe_procedure=data['procedure'],
            recipe_people_served=data['people_served'],
            recipe_prep_time=data.get('prep_time'),
            recipe_cook_time=data.get('cook_time'),
            recipe_image_url=image_url,
            recipe_image_public_id=image_public_id,
            recipe_owner_id=current_user_id
        )
                # Add to database
        db.session.add(new_recipe)
        db.session.commit()
        
        # Log the creation in edit history
        edit_log = RecipeEditHistory(
            history_recipe_id=new_recipe.recipe_id,
            history_user_id=current_user_id,
            history_action='created',
            history_changes={'initial_creation': True}
        )
        db.session.add(edit_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Recipe created successfully',
            'recipe': new_recipe.to_dict(include_owner=True, include_stats=False)
        }), 201
        
    except SQLAlchemyError as db_error:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': str(db_error)
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to create recipe',
            'message': str(e)
        }), 500
@recipe_bp.route('/<int:recipe_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_recipe(recipe_id):
    """
    Update an existing recipe.
    User must be the owner or a group member (if it's a group recipe).
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find recipe
        recipe = Recipe.query.filter_by(
            recipe_id=recipe_id, 
            recipe_is_deleted=False
        ).first()
        
        if not recipe:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        # Check permissions
        is_owner = recipe.recipe_owner_id == current_user_id
        is_group_member = any(
            group.is_member(current_user_id) 
            for group in recipe.recipe_groups.all()
        )
        
        if not (is_owner or is_group_member):
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'You do not have permission to edit this recipe'
            }), 403
        
        # Get update data
        data = request.get_json()
        changes = {}  # Track what was changed for edit history
        
        # Update allowed fields
        updateable_fields = {
            'title': 'recipe_title',
            'description': 'recipe_description',
            'country': 'recipe_country',
            'ingredients': 'recipe_ingredients',
            'procedure': 'recipe_procedure',
            'people_served': 'recipe_people_served',
            'prep_time': 'recipe_prep_time',
            'cook_time': 'recipe_cook_time'
        }
        
        for json_field, model_field in updateable_fields.items():
            if json_field in data:
                old_value = getattr(recipe, model_field)
                new_value = data[json_field]
                if old_value != new_value:
                    setattr(recipe, model_field, new_value)
                    changes[json_field] = {'old': old_value, 'new': new_value}
        
        # Handle image update
        if 'image' in data and data['image']:
            try:
                # Delete old image from Cloudinary if exists
                if recipe.recipe_image_public_id:
                    delete_image_from_cloudinary(recipe.recipe_image_public_id)
                
                # Upload new image
                upload_result = upload_image_to_cloudinary(
                    data['image'], 
                    folder='recipe_images'
                )
                recipe.recipe_image_url = upload_result.get('secure_url')
                recipe.recipe_image_public_id = upload_result.get('public_id')
                changes['image'] = 'updated'
            except Exception as img_error:
                print(f"Image update failed: {img_error}")
        
        # Update timestamp
        recipe.recipe_updated_at = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        
        # Log the update in edit history
        if changes:
            edit_log = RecipeEditHistory(
                history_recipe_id=recipe.recipe_id,
                history_user_id=current_user_id,
                history_action='updated',
                history_changes=changes
            )
            db.session.add(edit_log)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Recipe updated successfully',
            'recipe': recipe.to_dict(include_owner=True, include_stats=False)
        }), 200
        
    except SQLAlchemyError as db_error:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': str(db_error)
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to update recipe',
            'message': str(e)
        }), 500


@recipe_bp.route('/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    """
    Delete a recipe (soft delete).
    Only the owner can delete.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find recipe
        recipe = Recipe.query.filter_by(
            recipe_id=recipe_id, 
            recipe_is_deleted=False
        ).first()
        
        if not recipe:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        # Check if user is the owner
        if recipe.recipe_owner_id != current_user_id:
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'Only the recipe owner can delete it'
            }), 403
        
        # Soft delete (set flag instead of actually deleting)
        recipe.recipe_is_deleted = True
        recipe.recipe_updated_at = datetime.utcnow()
        
        # Log deletion
        edit_log = RecipeEditHistory(
            history_recipe_id=recipe.recipe_id,
            history_user_id=current_user_id,
            history_action='deleted',
            history_changes={'soft_delete': True}
        )
        db.session.add(edit_log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Recipe deleted successfully'
        }), 200
        
    except SQLAlchemyError as db_error:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': str(db_error)
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to delete recipe',
            'message': str(e)
        }), 500
@recipe_bp.route('/user/<int:user_id>', methods=['GET'])
def get_recipes_by_user(user_id):
    """
    Get all recipes created by a specific user.
    Public endpoint.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Query user's recipes
        recipes_query = Recipe.query.filter_by(
            recipe_owner_id=user_id,
            recipe_is_deleted=False
        ).order_by(Recipe.recipe_created_at.desc())
        
        # Paginate
        paginated_recipes = recipes_query.paginate(
            page=page, 
            per_page=min(per_page, 100), 
            error_out=False
        )
        
        recipes_list = [
            recipe.to_dict(include_owner=True, include_stats=True) 
            for recipe in paginated_recipes.items
        ]
        
        return jsonify({
            'success': True,
            'recipes': recipes_list,
            'pagination': {
                'current_page': paginated_recipes.page,
                'total_pages': paginated_recipes.pages,
                'total_items': paginated_recipes.total,
                'per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve user recipes',
            'message': str(e)
        }), 500

@recipe_bp.route('/<int:recipe_id>/history', methods=['GET'])
@jwt_required()
def get_recipe_edit_history(recipe_id):
    """
    Get edit history for a recipe.
    Useful for group recipes to see who edited what.
    Requires authentication.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if recipe exists
        recipe = Recipe.query.filter_by(
            recipe_id=recipe_id, 
            recipe_is_deleted=False
        ).first()
        
        if not recipe:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        # Check if user has access (owner or group member)
        is_owner = recipe.recipe_owner_id == current_user_id
        is_group_member = any(
            group.is_member(current_user_id) 
            for group in recipe.recipe_groups.all()
        )
        
        if not (is_owner or is_group_member):
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        # Get edit history
        history = RecipeEditHistory.query.filter_by(
            history_recipe_id=recipe_id
        ).order_by(RecipeEditHistory.history_timestamp.desc()).all()
        
        history_list = [entry.to_dict() for entry in history]
        
        return jsonify({
            'success': True,
            'history': history_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve edit history',
            'message': str(e)
        }), 500
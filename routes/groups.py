"""
Recipe-Room Backend - Group Recipe Routes
Author: Alex Maingi
Role: Recipes CRUD & Group Recipes

Flask Blueprint for group recipe collaboration (WhatsApp-like feature).
Prefix: /api/groups
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from models import RecipeGroup, Recipe, User, group_memberships, recipe_group_members
from database import db
from utils import upload_image_to_cloudinary, delete_image_from_cloudinary

#setting up the blueprint
group_bp = Blueprint('groups', __name__, url_prefix='/api/groups')
#group endpoints
@group_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_groups():
    """
    Get all groups the current user belongs to.
    Requires authentication.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get user from database
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get all groups user is a member of
        groups = user.joined_groups.filter_by(group_is_active=True).all()
        
        groups_list = [
            group.to_dict(include_members=True, include_recipes=False) 
            for group in groups
        ]
        
        return jsonify({
            'success': True,
            'groups': groups_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve groups',
            'message': str(e)
        }), 500
@group_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group_by_id(group_id):
    """
    Get detailed information about a specific group.
    User must be a member to view.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find group
        group = RecipeGroup.query.filter_by(
            group_id=group_id, 
            group_is_active=True
        ).first()
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Group not found'
            }), 404
        
        # Check if user is a member
        if not group.is_member(current_user_id):
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'You are not a member of this group'
            }), 403
        
        return jsonify({
            'success': True,
            'group': group.to_dict(include_members=True, include_recipes=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve group',
            'message': str(e)
        }), 500


@group_bp.route('/', methods=['POST'])
@jwt_required()
def create_group():
    """
    Create a new recipe group.
    Expected JSON payload:
    {
        "name": "Family Recipes",
        "description": "Our family's secret recipes",
        "max_members": 10,
        "image": "base64_or_url_optional"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'message': 'Group name is required'
            }), 400
        
        # Handle optional group image
        image_url = None
        if 'image' in data and data['image']:
            try:
                upload_result = upload_image_to_cloudinary(
                    data['image'], 
                    folder='group_images'
                )
                image_url = upload_result.get('secure_url')
            except Exception as img_error:
                print(f"Group image upload failed: {img_error}")
        
        # Create new group
        new_group = RecipeGroup(
            group_name=data['name'],
            group_description=data.get('description'),
            group_image_url=image_url,
            group_owner_id=current_user_id,
            group_max_members=data.get('max_members', 10)
        )
        
        db.session.add(new_group)
        # Then Get the group ID before committing
        db.session.flush()
        
        # Add creator as first member
        creator_user = User.query.get(current_user_id)
        new_group.group_members.append(creator_user)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Group created successfully',
            'group': new_group.to_dict(include_members=True, include_recipes=False)
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
            'error': 'Failed to create group',
            'message': str(e)
        }), 500
@group_bp.route('/<int:group_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_group(group_id):
    """
    Update group details.
    Only the owner can update group info.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find group
        group = RecipeGroup.query.filter_by(
            group_id=group_id, 
            group_is_active=True
        ).first()
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Group not found'
            }), 404
        
        # Check if user is the owner
        if not group.is_owner(current_user_id):
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'Only the group owner can update group details'
            }), 403
        
        # Get update data
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            group.group_name = data['name']
        if 'description' in data:
            group.group_description = data['description']
        if 'max_members' in data:
            group.group_max_members = data['max_members']
        
        # Handle image update
        if 'image' in data and data['image']:
            try:
                upload_result = upload_image_to_cloudinary(
                    data['image'], 
                    folder='group_images'
                )
                group.group_image_url = upload_result.get('secure_url')
            except Exception as img_error:
                print(f"Group image update failed: {img_error}")
        
        group.group_updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Group updated successfully',
            'group': group.to_dict(include_members=True, include_recipes=False)
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
            'error': 'Failed to update group',
            'message': str(e)
        }), 500


@group_bp.route('/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    """
    Delete (deactivate) a group.
    Only the owner can delete.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find group
        group = RecipeGroup.query.filter_by(
            group_id=group_id, 
            group_is_active=True
        ).first()
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Group not found'
            }), 404
        
        # Check if user is the owner
        if not group.is_owner(current_user_id):
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'Only the group owner can delete the group'
            }), 403
        
        # Soft delete
        group.group_is_active = False
        group.group_updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Group deleted successfully'
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
            'error': 'Failed to delete group',
            'message': str(e)
        }), 500

#the group members management
@group_bp.route('/<int:group_id>/members', methods=['POST'])
@jwt_required()
def add_group_member(group_id):
    """
    Add a new member to the group.
    Owner or existing members can invite.
    Expected JSON: {"user_id": 123}
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        new_member_id = data.get('user_id')
        if not new_member_id:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'message': 'user_id is required'
            }), 400
        
        # Find group
        group = RecipeGroup.query.filter_by(
            group_id=group_id, 
            group_is_active=True
        ).first()
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Group not found'
            }), 404
        
        # Check if current user is a member (has permission to add others)
        if not group.is_member(current_user_id):
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'You must be a member to add others'
            }), 403
        
        # Check if group is full
        if not group.can_add_members():
            return jsonify({
                'success': False,
                'error': 'Group is full',
                'message': f'Maximum {group.group_max_members} members allowed'
            }), 400
        
        # Check if user exists
        new_member = User.query.get(new_member_id)
        if not new_member:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Check if user is already a member
        if group.is_member(new_member_id):
            return jsonify({
                'success': False,
                'error': 'User is already a member'
            }), 400
        
        # Add member to group
        group.group_members.append(new_member)
        group.group_updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Member added successfully',
            'group': group.to_dict(include_members=True, include_recipes=False)
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
            'error': 'Failed to add member',
            'message': str(e)
        }), 500
@group_bp.route('/<int:group_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_group_member(group_id, user_id):
    """
    Remove a member from the group.
    Owner can remove anyone, members can remove themselves.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find group
        group = RecipeGroup.query.filter_by(
            group_id=group_id, 
            group_is_active=True
        ).first()
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Group not found'
            }), 404
        
        # Check permissions
        is_owner = group.is_owner(current_user_id)
        is_self_removal = (user_id == current_user_id)
        
        if not (is_owner or is_self_removal):
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'Only owner can remove others, or you can remove yourself'
            }), 403
        
        # Prevent owner from removing themselves
        if is_self_removal and is_owner:
            return jsonify({
                'success': False,
                'error': 'Operation not allowed',
                'message': 'Group owner cannot leave the group. Transfer ownership or delete the group.'
            }), 400
        
        # Find member to remove
        member_to_remove = User.query.get(user_id)
        if not member_to_remove:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Check if user is actually a member
        if not group.is_member(user_id):
            return jsonify({
                'success': False,
                'error': 'User is not a member of this group'
            }), 400
        
        # Remove member
        group.group_members.remove(member_to_remove)
        group.group_updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Member removed successfully'
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
            'error': 'Failed to remove member',
            'message': str(e)
        }), 500

#the group recipes management
@group_bp.route('/<int:group_id>/recipes', methods=['GET'])
@jwt_required()
def get_group_recipes(group_id):
    """
    Get all recipes associated with a group.
    Must be a group member.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find group
        group = RecipeGroup.query.filter_by(
            group_id=group_id, 
            group_is_active=True
        ).first()
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Group not found'
            }), 404
        
        # Check membership
        if not group.is_member(current_user_id):
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        # Get all recipes in this group
        recipes = group.group_recipes.filter_by(recipe_is_deleted=False).all()
        
        recipes_list = [
            recipe.to_dict(include_owner=True, include_stats=True) 
            for recipe in recipes
        ]
        
        return jsonify({
            'success': True,
            'recipes': recipes_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve group recipes',
            'message': str(e)
        }), 500


@group_bp.route('/<int:group_id>/recipes/<int:recipe_id>', methods=['POST'])
@jwt_required()
def add_recipe_to_group(group_id, recipe_id):
    """
    Add an existing recipe to a group.
    Recipe owner or group members can do this.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find group
        group = RecipeGroup.query.filter_by(
            group_id=group_id, 
            group_is_active=True
        ).first()
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Group not found'
            }), 404
        
        # Check if user is a group member
        if not group.is_member(current_user_id):
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'You must be a group member'
            }), 403
        
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
        
        # Check if recipe is already in group
        if group in recipe.recipe_groups.all():
            return jsonify({
                'success': False,
                'error': 'Recipe already in group'
            }), 400
        
        # Add recipe to group
        group.group_recipes.append(recipe)
        group.group_updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Recipe added to group successfully'
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
            'error': 'Failed to add recipe to group',
            'message': str(e)
        }), 500


@group_bp.route('/<int:group_id>/recipes/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def remove_recipe_from_group(group_id, recipe_id):
    """
    Remove a recipe from a group.
    Recipe owner or group owner can do this.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find group
        group = RecipeGroup.query.filter_by(
            group_id=group_id, 
            group_is_active=True
        ).first()
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Group not found'
            }), 404
        
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
        
        # Check permissions (group owner or recipe owner)
        is_group_owner = group.is_owner(current_user_id)
        is_recipe_owner = recipe.recipe_owner_id == current_user_id
        
        if not (is_group_owner or is_recipe_owner):
            return jsonify({
                'success': False,
                'error': 'Permission denied',
                'message': 'Only group owner or recipe owner can remove recipe from group'
            }), 403
        
        # Check if recipe is in group
        if group not in recipe.recipe_groups.all():
            return jsonify({
                'success': False,
                'error': 'Recipe not in group'
            }), 400
        
        # Remove recipe from group
        group.group_recipes.remove(recipe)
        group.group_updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Recipe removed from group successfully'
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
            'error': 'Failed to remove recipe from group',
            'message': str(e)
        }), 500
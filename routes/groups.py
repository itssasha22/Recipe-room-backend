from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Group, GroupMember, User, Recipe

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('', methods=['GET'])
@jwt_required()
def get_groups():
    try:
        user_id = int(get_jwt_identity())
        groups = Group.query.filter_by(created_by=user_id).all()
        return jsonify([group.to_dict() for group in groups]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('', methods=['POST'])
@jwt_required()
def create_group():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        group = Group(
            name=data['name'],
            description=data.get('description', ''),
            created_by=user_id
        )
        
        db.session.add(group)
        db.session.commit()
        
        return jsonify(group.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    try:
        group = Group.query.get_or_404(group_id)
        return jsonify(group.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    try:
        user_id = int(get_jwt_identity())
        group = Group.query.get_or_404(group_id)
        
        if group.created_by != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        if 'name' in data:
            group.name = data['name']
        if 'description' in data:
            group.description = data['description']
        
        db.session.commit()
        return jsonify(group.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    try:
        user_id = int(get_jwt_identity())
        group = Group.query.get_or_404(group_id)
        
        if group.created_by != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(group)
        db.session.commit()
        return jsonify({'message': 'Group deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Group Membership Endpoints
@groups_bp.route('/<int:group_id>/members', methods=['GET'])
@jwt_required()
def get_group_members(group_id):
    """Get all members of a group"""
    try:
        group = Group.query.get_or_404(group_id)
        members = GroupMember.query.filter_by(group_id=group_id).all()
        return jsonify([member.to_dict() for member in members]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/<int:group_id>/members', methods=['POST'])
@jwt_required()
def add_group_member(group_id):
    """Add a member to a group (only owner/admin can add)"""
    try:
        user_id = int(get_jwt_identity())
        group = Group.query.get_or_404(group_id)
        data = request.get_json()
        
        # Check if current user is owner or admin
        current_member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
        is_owner = group.created_by == user_id
        is_admin = current_member and current_member.role == 'admin'
        
        if not (is_owner or is_admin):
            return jsonify({'error': 'Only group owner or admin can add members'}), 403
        
        # Get target user
        if not data.get('user_id'):
            return jsonify({'error': 'user_id is required'}), 400
        
        target_user = User.query.get_or_404(data['user_id'])
        
        # Check if already a member
        existing_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=data['user_id']
        ).first()
        
        if existing_member:
            return jsonify({'message': 'User is already a member', 'member': existing_member.to_dict()}), 200
        
        # Add new member
        member = GroupMember(
            group_id=group_id,
            user_id=data['user_id'],
            role=data.get('role', 'member')
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify(member.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/<int:group_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_group_member(group_id, member_id):
    """Remove a member from a group"""
    try:
        user_id = int(get_jwt_identity())
        group = Group.query.get_or_404(group_id)
        
        # Check if current user is owner or admin
        current_member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
        is_owner = group.created_by == user_id
        is_admin = current_member and current_member.role == 'admin'
        
        member = GroupMember.query.get_or_404(member_id)
        
        # Users can remove themselves, or owner/admin can remove others
        if member.user_id != user_id and not (is_owner or is_admin):
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Member removed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/<int:group_id>/recipes', methods=['GET'])
@jwt_required()
def get_group_recipes(group_id):
    """Get all recipes created by this group"""
    try:
        group = Group.query.get_or_404(group_id)
        recipes = Recipe.query.filter_by(group_id=group_id).all()
        return jsonify([recipe.to_dict(include_stats=True) for recipe in recipes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@groups_bp.route('/my-groups', methods=['GET'])
@jwt_required()
def get_my_groups():
    """Get all groups the current user is a member of"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get groups user created
        created_groups = Group.query.filter_by(created_by=user_id).all()
        
        # Get groups user is a member of
        memberships = GroupMember.query.filter_by(user_id=user_id).all()
        member_groups = [Group.query.get(m.group_id) for m in memberships]
        
        # Combine and remove duplicates
        all_groups = {g.id: g.to_dict() for g in created_groups + member_groups if g}
        
        return jsonify(list(all_groups.values())), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

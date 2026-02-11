"""
Recipe-Room Backend - Recipe Utilities
Author: Alex Maingi
Role: Recipes CRUD & Group Recipes

Helper functions for recipe validation, image handling, and data processing.
These functions are designed to be imported by route handlers.
"""

import cloudinary
import cloudinary.uploader
import base64
import re
from typing import Dict, Optional, List, Any
#validation functions for recipe data
def validate_recipe_data(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate recipe data before creating/updating.
    
    Args:
        data: Dictionary containing recipe information
        
    Returns:
        Error message string if validation fails, None if valid
    """
    
    # Check required fields
    required_fields = ['title', 'ingredients', 'procedure', 'people_served']
    for field in required_fields:
        if field not in data or not data[field]:
            return f"Missing required field: {field}"
    
    # Validate title
    if not isinstance(data['title'], str):
        return "Title must be a string"
    if len(data['title']) < 3:
        return "Title must be at least 3 characters long"
    if len(data['title']) > 200:
        return "Title must be less than 200 characters"
    
    # Validate ingredients (must be a list of objects)
    if not isinstance(data['ingredients'], list):
        return "Ingredients must be a list"
    if len(data['ingredients']) == 0:
        return "At least one ingredient is required"
    
    # Validate each ingredient
    for idx, ingredient in enumerate(data['ingredients']):
        if not isinstance(ingredient, dict):
            return f"Ingredient {idx + 1} must be an object"
        if 'name' not in ingredient or not ingredient['name']:
            return f"Ingredient {idx + 1} must have a name"
        if 'quantity' not in ingredient:
            return f"Ingredient {idx + 1} must have a quantity"
    
    # Validate procedure (must be a list of step objects)
    if not isinstance(data['procedure'], list):
        return "Procedure must be a list"
    if len(data['procedure']) == 0:
        return "At least one procedure step is required"
    
    # Validate each procedure step
    for idx, step in enumerate(data['procedure']):
        if not isinstance(step, dict):
            return f"Procedure step {idx + 1} must be an object"
        if 'step' not in step or 'instruction' not in step:
            return f"Procedure step {idx + 1} must have 'step' and 'instruction' fields"
        if not isinstance(step['instruction'], str) or len(step['instruction']) < 5:
            return f"Procedure step {idx + 1} instruction must be at least 5 characters"
    
    # Validate people_served
    if not isinstance(data['people_served'], int):
        # Try to convert if it's a string number
        try:
            data['people_served'] = int(data['people_served'])
        except (ValueError, TypeError):
            return "people_served must be a number"
    
    if data['people_served'] < 1:
        return "people_served must be at least 1"
    if data['people_served'] > 1000:
        return "people_served cannot exceed 1000"
    
    # Validate optional time fields if provided
    for time_field in ['prep_time', 'cook_time']:
        if time_field in data and data[time_field] is not None:
            if not isinstance(data[time_field], int):
                try:
                    data[time_field] = int(data[time_field])
                except (ValueError, TypeError):
                    return f"{time_field} must be a number (minutes)"
            if data[time_field] < 0:
                return f"{time_field} cannot be negative"
            if data[time_field] > 10080:  # 7 days in minutes
                return f"{time_field} seems unreasonably long (max 7 days)"
    
    # Validate country if provided
    if 'country' in data and data['country']:
        if not isinstance(data['country'], str):
            return "Country must be a string"
        if len(data['country']) > 100:
            return "Country name too long (max 100 characters)"
    
    # Validate description if provided
    if 'description' in data and data['description']:
        if not isinstance(data['description'], str):
            return "Description must be a string"
        if len(data['description']) > 5000:
            return "Description too long (max 5000 characters)"
    
    # All validations passed
    return None
def sanitize_recipe_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and sanitize recipe data.
    Remove any potentially harmful content and normalize data.
    
    Args:
        data: Raw recipe data
        
    Returns:
        Sanitized recipe data
    """
    sanitized = {}
    
    # Sanitize title (remove excessive whitespace, potential XSS)
    if 'title' in data:
        sanitized['title'] = ' '.join(data['title'].strip().split())
    
    # Sanitize description
    if 'description' in data and data['description']:
        sanitized['description'] = ' '.join(data['description'].strip().split())
    else:
        sanitized['description'] = None
    
    # Sanitize country
    if 'country' in data and data['country']:
        sanitized['country'] = data['country'].strip().title()
    else:
        sanitized['country'] = None
    
    # Sanitize ingredients
    if 'ingredients' in data:
        sanitized['ingredients'] = [
            {
                'name': ing.get('name', '').strip(),
                'quantity': ing.get('quantity', '').strip(),
                'notes': ing.get('notes', '').strip() if 'notes' in ing else ''
            }
            for ing in data['ingredients']
        ]
    
    # Sanitize procedure
    if 'procedure' in data:
        sanitized['procedure'] = [
            {
                'step': step.get('step', idx + 1),
                'instruction': step.get('instruction', '').strip(),
                'notes': step.get('notes', '').strip() if 'notes' in step else ''
            }
            for idx, step in enumerate(data['procedure'])
        ]
    
    # Pass through numeric fields
    for field in ['people_served', 'prep_time', 'cook_time']:
        if field in data:
            sanitized[field] = data[field]
    
    # Pass through image
    if 'image' in data:
        sanitized['image'] = data['image']
    
    return sanitized
# cloudinary image handling
def upload_image_to_cloudinary(image_data: str, folder: str = 'recipe_images') -> Dict[str, str]:
    """
    Upload an image to Cloudinary.
    
    Args:
        image_data: Base64 encoded image or URL
        folder: Cloudinary folder to store the image
        
    Returns:
        Dictionary with secure_url and public_id
        
    Raises:
        Exception if upload fails
    """
    try:
        # Check if image_data is a URL or base64
        if image_data.startswith('http://') or image_data.startswith('https://'):
            # It's a URL, upload from URL
            result = cloudinary.uploader.upload(
                image_data,
                folder=folder,
                resource_type='image',
                transformation=[
                    {'width': 1200, 'height': 1200, 'crop': 'limit'},
                    {'quality': 'auto:good'},
                    {'fetch_format': 'auto'}
                ]
            )
        else:
            # Assume it's base64
            # Remove data URL prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # Upload base64 image
            result = cloudinary.uploader.upload(
                f"data:image/png;base64,{image_data}",
                folder=folder,
                resource_type='image',
                transformation=[
                    {'width': 1200, 'height': 1200, 'crop': 'limit'},
                    {'quality': 'auto:good'},
                    {'fetch_format': 'auto'}
                ]
            )
        
        return {
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'width': result.get('width'),
            'height': result.get('height'),
            'format': result.get('format')
        }
        
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")


def delete_image_from_cloudinary(public_id: str) -> bool:
    """
    Delete an image from Cloudinary.
    
    Args:
        public_id: Cloudinary public ID of the image to delete
        
    Returns:
        True if deletion successful, False otherwise
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Cloudinary deletion failed for {public_id}: {str(e)}")
        return False

#Recipe time calculations
def calculate_total_time(prep_time: Optional[int], cook_time: Optional[int]) -> int:
    """
    Calculate total time for a recipe.
    
    Args:
        prep_time: Preparation time in minutes
        cook_time: Cooking time in minutes
        
    Returns:
        Total time in minutes
    """
    total = 0
    if prep_time:
        total += prep_time
    if cook_time:
        total += cook_time
    return total

def format_time_display(minutes: int) -> str:
    """
    Convert minutes to human-readable time format.
    
    Args:
        minutes: Time in minutes
        
    Returns:
        Formatted time string (e.g., "1 hour 30 mins")
    """
    if minutes < 60:
        return f"{minutes} mins"
    
    hours = minutes // 60
    remaining_mins = minutes % 60
    
    if remaining_mins == 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        return f"{hours} hour{'s' if hours > 1 else ''} {remaining_mins} mins"


def extract_ingredient_names(ingredients: List[Dict[str, Any]]) -> List[str]:
    """
    Extract just the ingredient names from ingredient objects.
    Useful for search/filter functionality.
    
    Args:
        ingredients: List of ingredient dictionaries
        
    Returns:
        List of ingredient names (lowercase for comparison)
    """
    return [ing.get('name', '').lower().strip() for ing in ingredients if ing.get('name')]

def normalize_country_name(country: Optional[str]) -> Optional[str]:
    """
    Normalize country name for consistent storage.
    
    Args:
        country: Raw country name
        
    Returns:
        Normalized country name or None
    """
    if not country:
        return None
    
    # Remove extra whitespace and capitalize properly
    normalized = ' '.join(country.strip().split()).title()
    
    # Handle common variations
    country_mappings = {
        'Usa': 'United States',
        'Us': 'United States',
        'U.s.': 'United States',
        'U.s.a.': 'United States',
        'Uk': 'United Kingdom',
        'U.k.': 'United Kingdom',
        'Uae': 'United Arab Emirates',
        'U.a.e.': 'United Arab Emirates',
    }
    
    return country_mappings.get(normalized, normalized)

# permission checks for recipe operations
def can_edit_recipe(recipe, user_id: int, groups: Optional[List] = None) -> bool:
    """
    Check if a user can edit a recipe.
    
    Args:
        recipe: Recipe object
        user_id: ID of the user attempting to edit
        groups: Optional list of groups the recipe belongs to
        
    Returns:
        True if user can edit, False otherwise
    """
    # Owner can always edit
    if recipe.recipe_owner_id == user_id:
        return True
    
    # Check if user is in any group that has this recipe
    if groups is None:
        groups = recipe.recipe_groups.all()
    
    for group in groups:
        if group.is_member(user_id):
            return True
    
    return False


def can_delete_recipe(recipe, user_id: int) -> bool:
    """
    Check if a user can delete a recipe.
    Only the owner can delete.
    
    Args:
        recipe: Recipe object
        user_id: ID of the user attempting to delete
        
    Returns:
        True if user can delete, False otherwise
    """
    return recipe.recipe_owner_id == user_id

# recipe data formatting for API responses
def format_recipe_for_api(recipe, include_full_details: bool = True) -> Dict[str, Any]:
    """
    Format recipe data for API response with consistent structure.
    
    Args:
        recipe: Recipe object
        include_full_details: Whether to include all related data
        
    Returns:
        Formatted recipe dictionary
    """
    return recipe.to_dict(
        include_owner=include_full_details,
        include_stats=include_full_details
    )
def bulk_format_recipes(recipes: List, include_full_details: bool = False) -> List[Dict[str, Any]]:
    """
    Format multiple recipes for API response.
    
    Args:
        recipes: List of Recipe objects
        include_full_details: Whether to include all related data
        
    Returns:
        List of formatted recipe dictionaries
    """
    return [
        format_recipe_for_api(recipe, include_full_details)
        for recipe in recipes
    ]
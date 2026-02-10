import re
from flask import jsonify
from functools import wraps
import bleach

def sanitize_html(text):
    """Remove potentially harmful HTML/JS from user input"""
    if not text:
        return text
    # Allow basic formatting but strip scripts and other dangerous tags
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    return bleach.clean(text, tags=allowed_tags, strip=True)

def validate_comment_content(content):
    """Validate comment content"""
    if not content or not content.strip():
        return False, "Comment content is required"
    
    content = content.strip()
    if len(content) < 1:
        return False, "Comment must be at least 1 character"
    
    if len(content) > 1000:
        return False, "Comment must not exceed 1000 characters"
    
    return True, content

def paginate_results(query, page=1, per_page=20):
    """Paginate query results"""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
        
        # Ensure reasonable limits
        page = max(1, page)
        per_page = min(max(1, per_page), 100)
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': paginated.items,
            'total': paginated.total,
            'page': paginated.page,
            'per_page': paginated.per_page,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    except (ValueError, TypeError):
        return None

def standardize_error(message, status_code=400, errors=None):
    """Standardize error responses"""
    response = {
        'success': False,
        'error': message,
        'status_code': status_code
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code

def standardize_response(data, message=None, status_code=200):
    """Standardize success responses"""
    response = {
        'success': True,
        'data': data
    }
    if message:
        response['message'] = message
    return jsonify(response), status_code

def validate_request(required_fields):
    """Decorator to validate request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            data = request.get_json()
            
            if not data:
                return standardize_error('Request body is required', 400)
            
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            
            if missing_fields:
                return standardize_error(
                    'Missing required fields',
                    400,
                    {'missing_fields': missing_fields}
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

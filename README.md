# FlavorHub - Backend

Flask REST API for FlavorHub recipe sharing platform.

## Tech Stack

- Flask
- SQLAlchemy
- JWT Authentication
- SQLite
- Cloudinary
- PayD

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your keys

# Initialize database
python init_db.py

# Run server
python app.py
```

Backend runs on `http://localhost:5000`

## Project Structure

```
Recipe-room-backend/
├── routes/
│   ├── auth.py          # Authentication endpoints
│   ├── recipes.py       # Recipe CRUD
│   ├── bookmarks.py     # Bookmark management
│   ├── groups.py        # Group management
│   ├── comments.py      # Comments
│   ├── ratings.py       # Ratings
│   └── payments.py      # PayD integration
├── models.py            # Database models
├── app.py              # Flask app
├── database.py         # DB configuration
├── config.py           # App configuration
└── requirements.txt
```

## API Endpoints

### Authentication
```
POST   /api/auth/register       # Register user
POST   /api/auth/login          # Login
GET    /api/auth/profile        # Get profile (protected)
PUT    /api/auth/profile        # Update profile (protected)
POST   /api/auth/upload-image   # Upload profile image (protected)
```

### Recipes
```
GET    /api/recipes             # Get all recipes
POST   /api/recipes             # Create recipe (protected)
GET    /api/recipes/:id         # Get recipe details
PUT    /api/recipes/:id         # Update recipe (protected)
DELETE /api/recipes/:id         # Delete recipe (protected)
GET    /api/recipes/user/:id    # Get user recipes
```

### Bookmarks
```
GET    /api/bookmarks           # Get user bookmarks (protected)
POST   /api/bookmarks/:id       # Bookmark recipe (protected)
DELETE /api/bookmarks/:id       # Remove bookmark (protected)
GET    /api/bookmarks/check/:id # Check bookmark status (protected)
```

### Groups
```
GET    /api/groups              # Get user groups (protected)
POST   /api/groups              # Create group (protected)
GET    /api/groups/:id          # Get group details (protected)
POST   /api/groups/:id/join     # Join group (protected)
GET    /api/groups/:id/members  # Get group members (protected)
```

### Ratings & Comments
```
POST   /api/recipes/:id/rate    # Rate recipe (protected)
POST   /api/recipes/:id/comment # Comment on recipe (protected)
GET    /api/recipes/:id/comments # Get recipe comments
```

## Environment Variables

```bash
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///recipe_room.db
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
PAYD_SECRET_KEY=your-payd-key
```

## Database Models

### User
- id, username, email, password_hash, profile_image, created_at

### Recipe
- id, title, description, ingredients, instructions, image_url
- prep_time, cook_time, servings, country, is_premium
- user_id, group_id, created_at

### Group
- id, name, description, created_by, created_at

### Bookmark
- id, recipe_id, user_id, created_at

### Rating
- id, rating (1-5), recipe_id, user_id, created_at

### Comment
- id, content, recipe_id, user_id, created_at, updated_at

## Database Management

### Initialize Database
```bash
python init_db.py
```

### Add Sample Recipes
```bash
python add_global_recipes.py
```

### Reset Database
```bash
rm instance/recipe_room.db
python init_db.py
```

## Authentication

JWT-based authentication. Protected routes require:
```
Authorization: Bearer <token>
```

## Deployment

### Render
1. Push to GitHub
2. New Web Service
3. Connect repository
4. Set environment variables
5. Deploy

### Railway
1. Push to GitHub
2. New Project
3. Connect repository
4. Add environment variables
5. Deploy

## Author

Built by Derrick Koome

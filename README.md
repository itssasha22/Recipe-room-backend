# Recipe-room-backend

## Overview
Backend API for Recipe Room application - A platform for sharing and discovering recipes.

## Features
- User authentication (Register, Login)
- JWT-based authorization
- User profile management
- Profile image upload with Cloudinary

## Tech Stack
- **Framework**: Flask
- **Database**: SQLite
- **Authentication**: JWT (Flask-JWT-Extended)
- **Image Storage**: Cloudinary
- **ORM**: SQLAlchemy

## Quick Start

### Prerequisites
- Python 3.12+
- pip

### Installation
```bash
# Clone repository
git clone <repository-url>
cd Recipe-room-backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Run application
python3 app.py
```

## API Documentation
See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed endpoint documentation.

## Project Structure
```
Recipe-room-backend/
├── app.py              # Application entry point
├── config.py           # Configuration
├── models.py           # Database models
├── database.py         # DB initialization
├── routes/
│   └── auth.py        # Authentication routes
├── .env               # Environment variables
└── requirements.txt   # Dependencies
```

## Environment Variables
```
DATABASE_URL=sqlite:///recipe_room.db
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## API Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/upload-image` - Upload profile image

## Development
```bash
# Run in development mode
python3 app.py

# Server runs on http://localhost:8000
```

## Contributing
1. Create feature branch from `dev`
2. Make changes
3. Commit and push
4. Create pull request to `dev`

## License
MIT
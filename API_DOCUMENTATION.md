# Recipe Room Backend API Documentation

## Overview
Flask-based REST API for Recipe Room application with JWT authentication.

## Base URL
```
http://localhost:8000
```

## Technology Stack
- **Framework**: Flask
- **Database**: SQLite (development)
- **Authentication**: JWT (Flask-JWT-Extended)
- **Image Storage**: Cloudinary
- **Password Hashing**: Werkzeug

## Setup

### Installation
```bash
pip install -r requirements.txt
```

### Environment Variables
Create `.env` file:
```
DATABASE_URL=sqlite:///recipe_room.db
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Run Application
```bash
python3 app.py
```

## Authentication Endpoints

### 1. Register User
**POST** `/api/auth/register`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Success Response (201):**
```json
{
  "message": "User created successfully"
}
```

**Error Responses:**
- `400`: Missing required fields
- `400`: Email already exists
- `400`: Username already exists

---

### 2. Login
**POST** `/api/auth/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "profile_image": null,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Error Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

---

### 3. Get Profile
**GET** `/api/auth/profile`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "profile_image": "https://cloudinary.com/...",
  "created_at": "2024-01-01T00:00:00"
}
```

**Error Responses:**
- `401`: Missing or invalid token
- `404`: User not found

---

### 4. Update Profile
**PUT** `/api/auth/profile`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "username": "new_username",
  "email": "newemail@example.com"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "new_username",
  "email": "newemail@example.com",
  "profile_image": "https://cloudinary.com/...",
  "created_at": "2024-01-01T00:00:00"
}
```

**Error Responses:**
- `400`: Username already taken
- `400`: Email already taken
- `404`: User not found

---

### 5. Upload Profile Image
**POST** `/api/auth/upload-image`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
image: <file>
```

**Success Response (200):**
```json
{
  "image_url": "https://res.cloudinary.com/..."
}
```

**Error Responses:**
- `400`: No image provided
- `400`: No image selected
- `404`: User not found

---

## Database Models

### User Model
```python
{
  "id": Integer (Primary Key),
  "username": String(80) (Unique, Required),
  "email": String(120) (Unique, Required),
  "password_hash": String(255) (Required),
  "profile_image": String(255) (Optional),
  "created_at": DateTime (Auto-generated)
}
```

---

## Error Handling

All endpoints return errors in this format:
```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

---

## Security Features
- Password hashing using Werkzeug
- JWT token-based authentication
- Duplicate email/username validation
- Protected routes with @jwt_required decorator
- CORS enabled for cross-origin requests

---

## Project Structure
```
Recipe-room-backend/
├── app.py                 # Application entry point
├── config.py              # Configuration settings
├── models.py              # Database models
├── database.py            # Database initialization
├── routes/
│   └── auth.py           # Authentication routes
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

---

## Development Notes
- Database tables are created automatically on app startup
- SQLite database file: `recipe_room.db`
- Debug mode enabled for development
- Server runs on port 8000

---

## Future Enhancements
- Password reset functionality
- Email verification
- Refresh token implementation
- Rate limiting
- Input sanitization
- Password strength validation

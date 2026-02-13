from app import app, db
from models import GroupInvitation, Group

with app.app_context():
    # Add image_url column to groups table if it doesn't exist
    try:
        db.engine.execute("ALTER TABLE groups ADD COLUMN image_url VARCHAR(255)")
        print("Added image_url column to groups table")
    except Exception as e:
        print(f"image_url column might already exist: {e}")
    
    # Create group_invitations table
    try:
        db.create_all()
        print("Created group_invitations table")
    except Exception as e:
        print(f"Error creating tables: {e}")
    
    print("Migration completed!")

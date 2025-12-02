from sqlalchemy.orm import Session
from database import SessionLocal
import models
import security
from models import UserRole

def seed_users():
    db = SessionLocal()
    try:
        users = [
            {
                "username": "jen",
                "email": "jen@example.com",
                "full_name": "Jen",
                "role": UserRole.manager,
                "password": "password123"
            },
            {
                "username": "komal",
                "email": "komal@example.com",
                "full_name": "Komal",
                "role": UserRole.analyst,
                "password": "password123"
            },
            {
                "username": "parth",
                "email": "parth@example.com",
                "full_name": "Parth",
                "role": UserRole.analyst,
                "password": "password123"
            },
            {
                "username": "preerna",
                "email": "preerna@example.com",
                "full_name": "Preerna",
                "role": UserRole.analyst,
                "password": "password123"
            }
        ]

        for user_data in users:
            # Check if user exists
            existing_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
            if existing_user:
                print(f"User {user_data['username']} already exists.")
                continue

            print(f"Creating user {user_data['username']}...")
            password_hash = security.get_password_hash(user_data["password"])
            new_user = models.User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                password_hash=password_hash,
                is_active=True
            )
            db.add(new_user)
        
        db.commit()
        print("Users seeded successfully.")

    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()

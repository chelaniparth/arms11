from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import security

def create_admin():
    print(f"Connecting to: {engine.url}")
    db = SessionLocal()
    try:
        # Debug: Try raw SQL
        from sqlalchemy import text
        result = db.execute(text("SELECT count(*) FROM arms_workflow.users"))
        print(f"User count: {result.scalar()}")

        # Check again just in case
        user = db.query(models.User).filter(models.User.email == "admin@example.com").first()
        if user:
            print("User already exists.")
            return

        print("Creating admin user...")
        password_hash = security.get_password_hash("admin")
        new_user = models.User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            password_hash=password_hash,
            role="admin"
        )
        db.add(new_user)
        db.commit()
        print("Admin user created successfully.")
        print("Email: admin@example.com")
        print("Password: admin")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

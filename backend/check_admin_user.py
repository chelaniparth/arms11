from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import security

def check_admin():
    db = SessionLocal()
    try:
        user = db.query(models.User).filter((models.User.email == "admin@example.com") | (models.User.username == "admin")).first()
        if not user:
            print("User admin@example.com or username 'admin' NOT FOUND.")
        else:
            print(f"User found: ID={user.id}, Username={user.username}, Email={user.email}, Role={user.role}")
            print(f"Password Hash in DB: {user.password_hash}")
            
            # Verify password
            is_valid = security.verify_password("admin", user.password_hash)
            print(f"Password 'admin' is valid: {is_valid}")
            
            if user.email != "admin@example.com":
                print(f"Updating email from {user.email} to admin@example.com...")
                user.email = "admin@example.com"
                db.commit()
                print("Email update complete.")

            if not is_valid:
                print("Resetting password to 'admin'...")
                new_hash = security.get_password_hash("admin")
                user.password_hash = new_hash
                db.commit()
                print("Password reset complete.")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()

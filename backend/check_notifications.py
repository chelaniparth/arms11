from database import SessionLocal
import models

def check_notifications():
    db = SessionLocal()
    try:
        notifications = db.query(models.Notification).all()
        print(f"Total notifications: {len(notifications)}")
        for n in notifications:
            print(f"ID: {n.notification_id}, User: {n.user_id}, Title: {n.title}, Read: {n.is_read}")
            
        users = db.query(models.User).all()
        print("\nUsers:")
        for u in users:
            print(f"ID: {u.id}, Name: {u.full_name}, Role: {u.role}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_notifications()

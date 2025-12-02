import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def create_notifications_table():
    print("Connecting to DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Creating notification_type enum...")
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE arms_workflow.notification_type AS ENUM (
                    'info',
                    'success',
                    'warning',
                    'error'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        print("Creating notifications table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS arms_workflow.notifications (
                notification_id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES arms_workflow.users(id),
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                type arms_workflow.notification_type DEFAULT 'info',
                is_read BOOLEAN DEFAULT FALSE,
                link VARCHAR(500),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        conn.commit()
        print("Notifications table created successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_notifications_table()

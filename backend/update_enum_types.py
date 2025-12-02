import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def update_enums():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        new_types = ["Audit", "Data Entry", "Review", "Strategy", "Analysis"]
        
        for task_type in new_types:
            try:
                print(f"Adding '{task_type}' to task_type enum...")
                # Postgres doesn't support IF NOT EXISTS for ADD VALUE in all versions/contexts easily
                # So we wrap in a block or just try/except
                cur.execute(f"ALTER TYPE arms_workflow.task_type ADD VALUE '{task_type}';")
                print(f"Successfully added '{task_type}'")
            except psycopg2.errors.DuplicateObject:
                print(f"'{task_type}' already exists in enum.")
            except Exception as e:
                print(f"Error adding '{task_type}': {e}")

        cur.close()
        conn.close()
        print("Enum update process completed.")

    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    update_enums()

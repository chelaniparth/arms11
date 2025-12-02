from database import engine
from sqlalchemy import text

def update_db():
    with engine.connect() as conn:
        try:
            # Add new columns if they don't exist
            conn.execute(text("ALTER TABLE arms_workflow.tasks ADD COLUMN IF NOT EXISTS target_qty INTEGER DEFAULT 1"))
            conn.execute(text("ALTER TABLE arms_workflow.tasks ADD COLUMN IF NOT EXISTS achieved_qty INTEGER DEFAULT 0"))
            conn.execute(text("ALTER TABLE arms_workflow.tasks ADD COLUMN IF NOT EXISTS rating INTEGER"))
            conn.execute(text("ALTER TABLE arms_workflow.tasks ADD COLUMN IF NOT EXISTS remarks TEXT"))
            conn.execute(text("ALTER TABLE arms_workflow.tasks ADD COLUMN IF NOT EXISTS picked_at TIMESTAMP WITH TIME ZONE"))
            conn.execute(text("ALTER TABLE arms_workflow.tasks ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE"))
            conn.commit()
            print("Database updated successfully.")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    update_db()

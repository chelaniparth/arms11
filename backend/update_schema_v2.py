from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Starting Migration V2...")
        conn.execute(text("SET search_path TO arms_workflow, public;"))
        
        # 1. Update Enum
        new_types = [
            "Credit Application", "Trade Reference", "Liens", "Aging Tracker", 
            "QSR", "MLP", "PACA", "TNT", "CRA", "MSA", "Bond Watch", "Track Ratings"
        ]
        
        for t in new_types:
            try:
                print(f"Adding enum value: {t}")
                conn.execute(text(f"ALTER TYPE task_type ADD VALUE IF NOT EXISTS '{t}';"))
                conn.execute(text(f"ALTER TYPE workflow_type ADD VALUE IF NOT EXISTS '{t}';"))
            except Exception as e:
                print(f"Skipping {t} (might exist): {e}")
        
        # 2. Update WorkflowConfig Table
        print("Adding POC columns to workflow_configs...")
        try:
            conn.execute(text("""
                ALTER TABLE workflow_configs 
                ADD COLUMN IF NOT EXISTS primary_poc_id UUID REFERENCES users(id),
                ADD COLUMN IF NOT EXISTS secondary_poc_id UUID REFERENCES users(id),
                ADD COLUMN IF NOT EXISTS measurement_unit VARCHAR(100),
                ADD COLUMN IF NOT EXISTS monthly_target VARCHAR(100);
            """))
        except Exception as e:
            print(f"Error adding columns: {e}")

        # 3. Create WorkflowDailyVolume Table
        print("Creating workflow_daily_volumes table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workflow_daily_volumes (
                    volume_id SERIAL PRIMARY KEY,
                    workflow_type workflow_type NOT NULL,
                    date DATE NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    analyst_id UUID REFERENCES users(id),
                    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            # Add index
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_daily_volume_date ON workflow_daily_volumes(date);
            """))
        except Exception as e:
            print(f"Error creating table: {e}")

        conn.commit()
        print("Migration V2 Completed Successfully.")

if __name__ == "__main__":
    migrate()

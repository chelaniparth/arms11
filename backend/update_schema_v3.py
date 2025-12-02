from sqlalchemy import create_engine, text
from database import DATABASE_URL

def update_schema():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Add workflow_config_id column
            print("Adding workflow_config_id column to tasks table...")
            conn.execute(text("""
                ALTER TABLE arms_workflow.tasks 
                ADD COLUMN IF NOT EXISTS workflow_config_id INTEGER 
                REFERENCES arms_workflow.workflow_configs(config_id);
            """))
            
            # Add custom_workflow_name column
            print("Adding custom_workflow_name column to tasks table...")
            conn.execute(text("""
                ALTER TABLE arms_workflow.tasks 
                ADD COLUMN IF NOT EXISTS custom_workflow_name VARCHAR(255);
            """))
            
            conn.commit()
            print("Schema update completed successfully.")
        except Exception as e:
            print(f"Error updating schema: {e}")
            conn.rollback()

if __name__ == "__main__":
    update_schema()

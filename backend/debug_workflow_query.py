from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import WorkflowConfig
from database import DATABASE_URL

def debug_query():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Attempting to query WorkflowConfig with joinedload...")
        workflows = db.query(WorkflowConfig).options(
            joinedload(WorkflowConfig.primary_poc),
            joinedload(WorkflowConfig.secondary_poc)
        ).limit(5).all()
        
        print(f"SUCCESS: Retrieved {len(workflows)} workflows.")
        for w in workflows:
            p_name = w.primary_poc.full_name if w.primary_poc else "None"
            print(f" - {w.workflow_name}: Primary POC = {p_name}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_query()

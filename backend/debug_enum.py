import models
from database import SessionLocal
from sqlalchemy import func

def debug_enum():
    db = SessionLocal()
    try:
        # Fetch a workflow config
        wf = db.query(models.WorkflowConfig).first()
        if wf:
            print(f"Workflow Config: {wf.workflow_name}")
            print(f"Type: {type(wf.workflow_type)}")
            print(f"Value: {wf.workflow_type}")
            if hasattr(wf.workflow_type, 'value'):
                print(f"Enum Value: {wf.workflow_type.value}")
            if hasattr(wf.workflow_type, 'name'):
                print(f"Enum Name: {wf.workflow_type.name}")
                
            # Try to query Volume using this enum
            try:
                vol = db.query(models.WorkflowDailyVolume).filter(
                    models.WorkflowDailyVolume.workflow_type == wf.workflow_type
                ).first()
                print("Query successful")
            except Exception as e:
                print(f"Query failed: {e}")
                
    finally:
        db.close()

if __name__ == "__main__":
    debug_enum()

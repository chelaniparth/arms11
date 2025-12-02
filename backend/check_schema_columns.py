from database import engine
from sqlalchemy import inspect

def check_columns():
    inspector = inspect(engine)
    
    # Check Task table
    print("Checking 'tasks' table columns:")
    columns = [c['name'] for c in inspector.get_columns('tasks', schema='arms_workflow')]
    required_task_columns = [
        'target_qty', 'achieved_qty', 'rating', 'remarks', 
        'picked_at', 'completed_at', 'workflow_config_id', 'custom_workflow_name'
    ]
    for col in required_task_columns:
        if col in columns:
            print(f"  [OK] {col} exists")
        else:
            print(f"  [MISSING] {col}")

    # Check WorkflowConfig table
    print("\nChecking 'workflow_configs' table columns:")
    wf_columns = [c['name'] for c in inspector.get_columns('workflow_configs', schema='arms_workflow')]
    required_wf_columns = ['primary_poc_id', 'secondary_poc_id']
    for col in required_wf_columns:
        if col in wf_columns:
            print(f"  [OK] {col} exists")
        else:
            print(f"  [MISSING] {col}")

if __name__ == "__main__":
    check_columns()

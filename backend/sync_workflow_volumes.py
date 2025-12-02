import models
from database import SessionLocal
from sqlalchemy import func
from datetime import date

def sync_volumes():
    db = SessionLocal()
    try:
        print("Starting volume sync...")
        
        # 1. Get all tasks with workflow_config_id
        tasks = db.query(models.Task).filter(models.Task.workflow_config_id.isnot(None)).all()
        print(f"Found {len(tasks)} tasks with workflow config.")
        
        # 2. Group by (workflow_type, date, analyst_id)
        # We need to recalculate volumes from scratch to be accurate?
        # Or just add missing ones?
        # If we recalculate, we should clear existing volumes first?
        # But existing volumes might have been manually edited? (Unlikely)
        # Let's try to aggregate from tasks and UPDATE volumes.
        
        volume_map = {} # Key: (workflow_type, date, analyst_id) -> Quantity
        
        for task in tasks:
            wf_config = db.query(models.WorkflowConfig).filter(models.WorkflowConfig.config_id == task.workflow_config_id).first()
            if not wf_config:
                continue
                
            # Determine date: Created At (Intake) or Completed At (Output)?
            # Based on my decision to track "Intake" on Create, I should use created_at.
            # But I ALSO track "Output" on Complete.
            # This is tricky. If I sum up everything, I might double count.
            # Let's assume "Volume" = "Intake" for now as per user request for "Pending" items.
            # So I will use created_at.
            
            task_date = task.created_at.date()
            analyst_id = task.assigned_user_id # Can be None
            qty = task.target_qty if task.target_qty else 1
            # If achieved_qty is set and > 0, maybe use that?
            # But for Pending items, achieved is 0.
            if task.achieved_qty and task.achieved_qty > 0:
                qty = task.achieved_qty
            
            key = (wf_config.workflow_type, task_date, analyst_id)
            if key not in volume_map:
                volume_map[key] = 0
            volume_map[key] += qty
            
        print(f"Calculated {len(volume_map)} volume entries.")
        
        # 3. Update DB
        for (wf_type, vol_date, analyst_id), quantity in volume_map.items():
            # Find existing
            vol = db.query(models.WorkflowDailyVolume).filter(
                models.WorkflowDailyVolume.workflow_type == wf_type,
                models.WorkflowDailyVolume.date == vol_date,
                models.WorkflowDailyVolume.analyst_id == analyst_id
            ).first()
            
            if vol:
                # Update if different? 
                # Or should we ADD to it? 
                # If we are syncing from scratch, we should probably SET it.
                # But if there were other sources of volume?
                # Let's assume Task table is the source of truth.
                if vol.quantity != quantity:
                    print(f"Updating volume for {wf_type} on {vol_date}: {vol.quantity} -> {quantity}")
                    vol.quantity = quantity
            else:
                print(f"Creating volume for {wf_type} on {vol_date}: {quantity}")
                new_vol = models.WorkflowDailyVolume(
                    workflow_type=wf_type,
                    date=vol_date,
                    quantity=quantity,
                    analyst_id=analyst_id
                )
                db.add(new_vol)
        
        db.commit()
        print("Sync complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_volumes()

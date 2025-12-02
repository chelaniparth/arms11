from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, database
from . import auth
import csv
import io
from datetime import datetime, date

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def increment_workflow_volume(db: Session, workflow_config_id: int, analyst_id: Optional[str], date_obj: date, quantity: int = 1):
    """Helper to increment workflow daily volume."""
    if not workflow_config_id:
        return

    workflow_config = db.query(models.WorkflowConfig).filter(models.WorkflowConfig.config_id == workflow_config_id).first()
    if not workflow_config:
        return

    # Find or create daily volume record
    # Use .value for Enum to ensure string match in DB
    daily_volume = db.query(models.WorkflowDailyVolume).filter(
        models.WorkflowDailyVolume.workflow_type == workflow_config.workflow_type.value,
        models.WorkflowDailyVolume.date == date_obj,
        models.WorkflowDailyVolume.analyst_id == analyst_id
    ).first()
    
    if daily_volume:
        daily_volume.quantity += quantity
    else:
        new_volume = models.WorkflowDailyVolume(
            workflow_type=workflow_config.workflow_type.value,
            date=date_obj,
            quantity=quantity,
            analyst_id=analyst_id
        )
        db.add(new_volume)

@router.post("/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_task = models.Task(**task.dict())
    # Optionally assign creator if needed, or just ensure auth
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Increment Volume on Creation (Intake)
    if db_task.workflow_config_id:
        target_analyst = db_task.assigned_user_id if db_task.assigned_user_id else None
        qty = db_task.target_qty if db_task.target_qty else 1
        increment_workflow_volume(db, db_task.workflow_config_id, target_analyst, date.today(), qty)
        db.commit()

    return db_task

@router.post("/upload")
async def upload_tasks(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    try:
        if current_user.role not in [models.UserRole.admin, models.UserRole.manager]:
            raise HTTPException(status_code=403, detail="Only managers and admins can upload tasks")

        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
        
        try:
            content = await file.read()
            decoded_content = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(decoded_content))
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid file encoding. Please ensure the file is UTF-8 encoded CSV.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        success_count = 0
        errors = []
        
        for row_index, row in enumerate(csv_reader, start=1):
            try:
                # Basic validation
                required_fields = ['company_name', 'document_type', 'task_type']
                for field in required_fields:
                    if field not in row or not row[field]:
                        raise ValueError(f"Missing required field: {field}")
                
                # Validate task_type
                valid_task_types = [t.value for t in models.TaskType]
                if row['task_type'] not in valid_task_types:
                    raise ValueError(f"Invalid task_type '{row['task_type']}'. Must be one of: {', '.join(valid_task_types)}")

                # Lookup Workflow if provided
                workflow_id = None
                workflow_name = row.get('Workflow')
                if workflow_name:
                    # Try to find matching workflow config
                    wf = db.query(models.WorkflowConfig).filter(models.WorkflowConfig.workflow_name == workflow_name).first()
                    if wf:
                        workflow_id = wf.config_id

                # Parse Status
                status_val = row.get('Status', 'Pending')
                # Validate status if needed, or default to Pending if invalid
                valid_statuses = ["Pending", "In Progress", "Completed", "Under Review", "Paused"]
                if status_val not in valid_statuses:
                    status_val = "Pending"

                # Parse Qty
                try:
                    target_qty = int(row.get('Target Qty', 1))
                except:
                    target_qty = 1
                
                try:
                    achieved_qty = int(row.get('Achieved Qty', 0))
                except:
                    achieved_qty = 0

                # Create task
                task_data = schemas.TaskCreate(
                    company_name=row['company_name'],
                    document_type=row['document_type'],
                    task_type=row['task_type'],
                    priority=row.get('priority', 'Medium'),
                    description=row.get('description', ''),
                    notes=row.get('notes', ''),
                    assigned_user_id=current_user.id, # Auto-assign uploader
                    workflow_config_id=workflow_id,
                    custom_workflow_name=row.get('custom_workflow_name'),
                    target_qty=target_qty
                )
                
                db_task = models.Task(**task_data.dict())
                db_task.status = status_val
                db_task.achieved_qty = achieved_qty
                
                # If importing as Completed, set timestamps
                if status_val == "Completed":
                    db_task.completed_at = datetime.now()

                db.add(db_task)
                
                # Sync Volume for ALL imported tasks with workflow
                if workflow_id:
                    # Use achieved_qty if > 0, else target_qty
                    qty = achieved_qty if achieved_qty > 0 else target_qty
                    increment_workflow_volume(db, workflow_id, current_user.id, date.today(), qty)

                success_count += 1
                
            except Exception as e:
                print(f"Error processing row {row_index}: {e}")
                errors.append(f"Row {row_index}: {str(e)}")
                
        db.commit()
        
        return {
            "total_processed": success_count + len(errors),
            "success_count": success_count,
            "failed_count": len(errors),
            "errors": errors
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, workflow_config_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Task)
    
    if workflow_config_id:
        query = query.filter(models.Task.workflow_config_id == workflow_config_id)
        
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks

@router.get("/export", response_class=status.HTTP_200_OK)
def export_tasks(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # Only allow export for admin/manager
    if current_user.role not in [models.UserRole.admin, models.UserRole.manager]:
        raise HTTPException(status_code=403, detail="Only managers and admins can export tasks")

    tasks = db.query(models.Task).order_by(models.Task.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    headers = [
        "Task ID", "Company", "Type", "Document", "Status", 
        "Priority", "Target Qty", "Achieved Qty", "Created At", 
        "Assigned To"
    ]
    writer.writerow(headers)
    
    # Data
    for task in tasks:
        assigned_name = task.assigned_user.full_name if task.assigned_user else "Unassigned"
        writer.writerow([
            task.task_id,
            task.company_name,
            task.task_type.value if hasattr(task.task_type, 'value') else task.task_type,
            task.document_type,
            task.status.value if hasattr(task.status, 'value') else task.status,
            task.priority.value if hasattr(task.priority, 'value') else task.priority,
            task.target_qty,
            task.achieved_qty,
            task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            assigned_name
        ])
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    response = StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks_export.csv"}
    )
    return response

@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Restriction: Completed tasks can only be edited by admin/manager
    if db_task.status == models.TaskStatus.Completed:
        if current_user.role not in [models.UserRole.admin, models.UserRole.manager]:
            raise HTTPException(status_code=403, detail="Completed tasks cannot be edited by analysts")

    # Capture old status to detect completion
    old_status = db_task.status
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    try:
        # If status changed to Completed, update metrics
        if old_status != models.TaskStatus.Completed and db_task.status == models.TaskStatus.Completed:
            db_task.completed_at = models.func.now()
            
            # Update UserPerformance
            today = models.func.current_date()
            perf = db.query(models.UserPerformance).filter(
                models.UserPerformance.user_id == current_user.id,
                models.UserPerformance.metric_date == today
            ).first()
            
            if not perf:
                perf = models.UserPerformance(
                    user_id=current_user.id,
                    metric_date=today,
                    tasks_assigned=0,
                    tasks_in_progress=0,
                    tasks_completed=0
                )
                db.add(perf)
                db.flush()

            if perf.tasks_in_progress > 0:
                perf.tasks_in_progress -= 1
            perf.tasks_completed += 1

            # --- Workflow Volume Sync Logic ---
            if db_task.workflow_config_id:
                qty_to_add = db_task.achieved_qty if db_task.achieved_qty else 1
                increment_workflow_volume(db, db_task.workflow_config_id, current_user.id, date.today(), qty_to_add)

        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        print(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")

@router.get("/{task_id}/history", response_model=List[schemas.TaskHistory])
def read_task_history(task_id: int, db: Session = Depends(get_db)):
    history = db.query(models.TaskHistory).filter(models.TaskHistory.task_id == task_id).order_by(models.TaskHistory.changed_at.desc()).all()
    return history

@router.get("/{task_id}/comments", response_model=List[schemas.TaskComment])
def read_task_comments(task_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.TaskComment).filter(models.TaskComment.task_id == task_id).order_by(models.TaskComment.created_at.desc()).all()
    return comments

@router.post("/{task_id}/comments", response_model=schemas.TaskComment)
def create_task_comment(task_id: int, comment: schemas.TaskCommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db_comment = models.TaskComment(
        task_id=task_id,
        user_id=current_user.id,
        comment_text=comment.comment_text,
        is_internal=comment.is_internal
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.post("/{task_id}/pick")
def pick_task(task_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if db_task.status != "Pending":
        raise HTTPException(status_code=400, detail="Only Pending tasks can be picked up")
    
    # Assign to current user
    db_task.assigned_user_id = current_user.id
    db_task.status = "In Progress"
    db_task.assigned_at = datetime.now()
    db_task.picked_at = datetime.now()
    
    # Update UserPerformance
    today = date.today()
    perf = db.query(models.UserPerformance).filter(
        models.UserPerformance.user_id == current_user.id,
        models.UserPerformance.metric_date == today
    ).first()
    
    if not perf:
        perf = models.UserPerformance(
            user_id=current_user.id,
            metric_date=today,
            tasks_assigned=0,
            tasks_in_progress=0,
            tasks_completed=0
        )
        db.add(perf)
    
    perf.tasks_in_progress += 1
    
    db.commit()
    db.refresh(db_task)
    return {"message": "Task picked up successfully", "task": db_task}

@router.post("/{task_id}/unpick")
def unpick_task(task_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions: Only assigned user or admin/manager can unpick
    if db_task.assigned_user_id != current_user.id and current_user.role not in [models.UserRole.admin, models.UserRole.manager]:
        raise HTTPException(status_code=403, detail="You can only unpick tasks assigned to you")

    if db_task.status != "In Progress":
        raise HTTPException(status_code=400, detail="Only 'In Progress' tasks can be unpicked")
    
    # Revert to Pending
    db_task.status = "Pending"
    db_task.assigned_user_id = None
    db_task.assigned_at = None
    db_task.picked_at = None
    
    # Update UserPerformance (decrement in_progress)
    today = date.today()
    perf = db.query(models.UserPerformance).filter(
        models.UserPerformance.user_id == current_user.id,
        models.UserPerformance.metric_date == today
    ).first()
    
    if perf and perf.tasks_in_progress > 0:
        perf.tasks_in_progress -= 1
    
    db.commit()
    db.refresh(db_task)
    return {"message": "Task unpicked successfully", "task": db_task}

@router.post("/{task_id}/complete", response_model=schemas.Task)
def complete_task(task_id: int, completion_data: schemas.TaskComplete, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions: Only assigned user or admin/manager can complete
    if db_task.assigned_user_id != current_user.id and current_user.role not in [models.UserRole.admin, models.UserRole.manager]:
        raise HTTPException(status_code=403, detail="You can only complete tasks assigned to you")

    if db_task.status == "Completed":
         raise HTTPException(status_code=400, detail="Task is already completed")

    # Update Task
    db_task.status = "Completed"
    db_task.achieved_qty = completion_data.achieved_qty
    db_task.remarks = completion_data.remarks
    db_task.completed_at = datetime.now()
    
    # Update UserPerformance
    today = date.today()
    perf = db.query(models.UserPerformance).filter(
        models.UserPerformance.user_id == current_user.id,
        models.UserPerformance.metric_date == today
    ).first()
    
    if not perf:
        perf = models.UserPerformance(
            user_id=current_user.id,
            metric_date=today,
            tasks_assigned=0,
            tasks_in_progress=0,
            tasks_completed=0
        )
        db.add(perf)
    
    if perf.tasks_in_progress > 0:
        perf.tasks_in_progress -= 1
    perf.tasks_completed += 1
    
    # Workflow Volume Sync
    if db_task.workflow_config_id:
        qty_to_add = db_task.achieved_qty if db_task.achieved_qty > 0 else 1
        increment_workflow_volume(db, db_task.workflow_config_id, current_user.id, today, qty_to_add)

    db.commit()
    db.refresh(db_task)
    return db_task

def decrement_metrics(db: Session, task: models.Task):
    """Helper to decrement metrics when a task is deleted."""
    if not task.assigned_user_id:
        return

    # 1. UserPerformance
    # Decrement Assigned Count (based on assigned_at date)
    if task.assigned_at:
        perf_assigned = db.query(models.UserPerformance).filter(
            models.UserPerformance.user_id == task.assigned_user_id,
            models.UserPerformance.metric_date == task.assigned_at.date()
        ).first()
        if perf_assigned and perf_assigned.tasks_assigned > 0:
            perf_assigned.tasks_assigned -= 1

    # Decrement Completed Count (based on completed_at date)
    if task.status == "Completed" and task.completed_at:
        perf_completed = db.query(models.UserPerformance).filter(
            models.UserPerformance.user_id == task.assigned_user_id,
            models.UserPerformance.metric_date == task.completed_at.date()
        ).first()
        if perf_completed and perf_completed.tasks_completed > 0:
            perf_completed.tasks_completed -= 1
            
        # Also decrement WorkflowDailyVolume
        if task.workflow_config_id:
            wf_config = db.query(models.WorkflowConfig).filter(models.WorkflowConfig.config_id == task.workflow_config_id).first()
            if wf_config:
                vol = db.query(models.WorkflowDailyVolume).filter(
                    models.WorkflowDailyVolume.date == task.completed_at.date(),
                    models.WorkflowDailyVolume.workflow_type == wf_config.workflow_type,
                    models.WorkflowDailyVolume.analyst_id == task.assigned_user_id
                ).first()
                if vol:
                    # task.achieved_qty might be > 1. Let's check model.
                    # Model has achieved_qty. Let's use that if > 0, else 1.
                    qty_to_remove = task.achieved_qty if task.achieved_qty > 0 else 1
                    vol.quantity -= qty_to_remove
                    if vol.quantity < 0: vol.quantity = 0

    # Decrement In Progress Count (Current Day - Best Effort for Dashboard Sync)
    # Since dashboard shows 'today's' in_progress, we decrement if it matches today.
    # Or if the task is currently In Progress, we decrement today's counter if it was incremented today?
    # Logic: pick_task increments today's counter. 
    # If we delete an In Progress task, we should decrement the counter for the day it was picked.
    if task.status == "In Progress" and task.picked_at:
        perf_picked = db.query(models.UserPerformance).filter(
            models.UserPerformance.user_id == task.assigned_user_id,
            models.UserPerformance.metric_date == task.picked_at.date()
        ).first()
        if perf_picked and perf_picked.tasks_in_progress > 0:
            perf_picked.tasks_in_progress -= 1

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.role not in [models.UserRole.admin, models.UserRole.manager]:
        raise HTTPException(status_code=403, detail="Only admins and managers can delete tasks")
        
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Decrement metrics before deleting
    decrement_metrics(db, db_task)
        
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.post("/bulk-delete")
def bulk_delete_tasks(request: schemas.BulkDeleteRequest, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.role not in [models.UserRole.admin, models.UserRole.manager]:
        raise HTTPException(status_code=403, detail="Only admins and managers can delete tasks")
    
    tasks_to_delete = db.query(models.Task).filter(models.Task.task_id.in_(request.task_ids)).all()
    
    for task in tasks_to_delete:
        decrement_metrics(db, task)
    
    # Now delete
    db.query(models.Task).filter(models.Task.task_id.in_(request.task_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"Successfully deleted {len(request.task_ids)} tasks"}

@router.post("/bulk-assign")
def bulk_assign_tasks(request: schemas.BulkAssignRequest, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.role not in [models.UserRole.admin, models.UserRole.manager]:
        raise HTTPException(status_code=403, detail="Only admins and managers can assign tasks")
    
    tasks = db.query(models.Task).filter(models.Task.task_id.in_(request.task_ids)).all()
    assigned_count = 0
    
    for task in tasks:
        task.assigned_user_id = request.user_id
        task.assigned_at = datetime.now()
        if task.status == "Pending":
            # Optional: Move to In Progress or keep Pending?
            # For now, keeping as Pending but assigned.
            pass
        assigned_count += 1
        
        # Update UserPerformance (Assigned Count)
        today = date.today()
        perf = db.query(models.UserPerformance).filter(
            models.UserPerformance.user_id == request.user_id,
            models.UserPerformance.metric_date == today
        ).first()
        
        if not perf:
            perf = models.UserPerformance(
                user_id=request.user_id,
                metric_date=today,
                tasks_assigned=0,
                tasks_in_progress=0,
                tasks_completed=0
            )
            db.add(perf)
        
        perf.tasks_assigned += 1
        
    db.commit()
    return {"message": f"Successfully assigned {assigned_count} tasks"}

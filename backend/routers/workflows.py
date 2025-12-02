from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
import models, schemas, database
from . import auth
from datetime import date

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.WorkflowConfig])
def read_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    workflows = db.query(models.WorkflowConfig).options(
        joinedload(models.WorkflowConfig.primary_poc),
        joinedload(models.WorkflowConfig.secondary_poc)
    ).offset(skip).limit(limit).all()
    return workflows

@router.post("/", response_model=schemas.WorkflowConfig)
def create_workflow(workflow: schemas.WorkflowConfigCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # Check if workflow with same name exists
    existing_workflow = db.query(models.WorkflowConfig).filter(models.WorkflowConfig.workflow_name == workflow.workflow_name).first()
    if existing_workflow:
        raise HTTPException(status_code=400, detail="Workflow with this name already exists")

    db_workflow = models.WorkflowConfig(**workflow.dict())
    db_workflow.created_by = str(current_user.id)
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.put("/{config_id}", response_model=schemas.WorkflowConfig)
def update_workflow(config_id: int, workflow_update: schemas.WorkflowConfigUpdate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_workflow = db.query(models.WorkflowConfig).filter(models.WorkflowConfig.config_id == config_id).first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    update_data = workflow_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_workflow, key, value)
    
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(config_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # Only admin can delete workflows
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete workflows")

    db_workflow = db.query(models.WorkflowConfig).filter(models.WorkflowConfig.config_id == config_id).first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(db_workflow)
    db.commit()
    return None

@router.post("/volume", response_model=schemas.WorkflowVolume)
def record_daily_volume(volume: schemas.WorkflowVolumeCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # Check if volume already exists for this date/workflow/analyst
    # If analyst_id is not provided, use current user
    target_analyst_id = volume.analyst_id if volume.analyst_id else current_user.id
    
    # If user is analyst, they can only record for themselves
    if current_user.role == "analyst" and str(target_analyst_id) != str(current_user.id):
         raise HTTPException(status_code=403, detail="Analysts can only record their own volume")

    existing_volume = db.query(models.WorkflowDailyVolume).filter(
        models.WorkflowDailyVolume.workflow_type == volume.workflow_type,
        models.WorkflowDailyVolume.date == volume.date,
        models.WorkflowDailyVolume.analyst_id == target_analyst_id
    ).first()

    if existing_volume:
        # Update existing
        existing_volume.quantity = volume.quantity
        existing_volume.recorded_at = func.now()
        db.commit()
        db.refresh(existing_volume)
        return existing_volume
    else:
        # Create new
        db_volume = models.WorkflowDailyVolume(**volume.dict())
        if not db_volume.analyst_id:
            db_volume.analyst_id = target_analyst_id
        
        db.add(db_volume)
        db.commit()
        db.refresh(db_volume)
        return db_volume

@router.get("/volume", response_model=List[schemas.WorkflowVolume])
def get_daily_volumes(
    date: date = None, 
    workflow_type: str = None, 
    limit: int = 100, 
    db: Session = Depends(database.get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    query = db.query(models.WorkflowDailyVolume)
    
    if date:
        query = query.filter(models.WorkflowDailyVolume.date == date)
    
    if workflow_type:
        query = query.filter(models.WorkflowDailyVolume.workflow_type == workflow_type)
        
    # If analyst, only see own? Or see all? Requirement says "only user which are parth and all will be able to see the total workflow"
    # Assuming visibility is open for now based on "see the total workflow"
    
    return query.order_by(models.WorkflowDailyVolume.date.desc()).limit(limit).all()

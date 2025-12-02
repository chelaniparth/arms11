from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
import models, schemas, database
from . import auth
from datetime import date

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    today = date.today()
    
    # My Stats
    my_perf = db.query(models.UserPerformance).filter(
        models.UserPerformance.user_id == current_user.id,
        models.UserPerformance.metric_date == today
    ).first()
    
    my_stats = {
        "tasks_assigned_today": my_perf.tasks_assigned if my_perf else 0,
        "tasks_completed_today": my_perf.tasks_completed if my_perf else 0,
        "avg_completion_time": (my_perf.avg_completion_time_hours if my_perf and my_perf.avg_completion_time_hours is not None else 0.0),
        "tasks_in_progress": my_perf.tasks_in_progress if my_perf else 0
    }

    # System Stats (for everyone for now, or restrict to admin/manager)
    # Total Active Tasks (Pending + In Progress)
    total_active = db.query(func.count(models.Task.task_id)).filter(
        models.Task.status.in_([models.TaskStatus.Pending, models.TaskStatus.In_Progress])
    ).scalar()

    # Tasks by Status
    status_counts = db.query(models.Task.status, func.count(models.Task.task_id)).group_by(models.Task.status).all()
    status_breakdown = {status: count for status, count in status_counts}

    # Top Performers (Today) - based on completed tasks
    top_performers_query = db.query(
        models.User.full_name, 
        models.UserPerformance.tasks_completed
    ).join(models.User).filter(
        models.UserPerformance.metric_date == today
    ).order_by(desc(models.UserPerformance.tasks_completed)).limit(5).all()
    
    top_performers = [{"name": name, "completed": count} for name, count in top_performers_query]

    return {
        "my_stats": my_stats,
        "system_stats": {
            "total_active_tasks": total_active,
            "status_breakdown": status_breakdown,
            "top_performers": top_performers
        }
    }

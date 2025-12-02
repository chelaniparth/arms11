from typing import List, Optional, Any, Union
from pydantic import BaseModel
from datetime import datetime, date
from uuid import UUID
from models import TaskStatus, TaskPriority, TaskType, UserRole, WorkflowType

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole = UserRole.analyst
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class User(UserBase):
    id: Union[str, UUID]
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

# Task Schemas
class TaskBase(BaseModel):
    task_type: str
    company_name: str
    document_type: str
    priority: str = "Medium"
    description: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None
    email_reference: Optional[str] = None
    sla_hours: int = 72
    due_date: Optional[datetime] = None
    target_qty: int = 1
    workflow_config_id: Optional[int] = None
    custom_workflow_name: Optional[str] = None

class TaskCreate(TaskBase):
    assigned_user_id: Optional[Union[str, UUID]] = None

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_user_id: Optional[Union[str, UUID]] = None
    notes: Optional[str] = None
    description: Optional[str] = None
    target_qty: Optional[int] = None
    achieved_qty: Optional[int] = None
    rating: Optional[int] = None
    remarks: Optional[str] = None

class TaskComplete(BaseModel):
    achieved_qty: int
    remarks: Optional[str] = None

class BulkDeleteRequest(BaseModel):
    task_ids: List[int]

class BulkAssignRequest(BaseModel):
    task_ids: List[int]
    user_id: Union[str, UUID]

class Task(TaskBase):
    task_id: int
    status: str
    assigned_user_id: Optional[Union[str, UUID]] = None
    assigned_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    tier1_started_at: Optional[datetime] = None
    tier1_completed_at: Optional[datetime] = None
class WorkflowConfigBase(BaseModel):
    workflow_name: str
    workflow_type: str
    target_metric: Optional[str] = None
    measurement_unit: Optional[str] = None
    monthly_target: Optional[str] = None
    priority: str = "Medium"
    sla_hours: int = 72
    quality_required: bool = True
    data_points: Optional[Any] = None
    is_active: bool = True
    primary_poc_id: Optional[Union[str, UUID]] = None
    secondary_poc_id: Optional[Union[str, UUID]] = None

class WorkflowConfigCreate(WorkflowConfigBase):
    pass

class WorkflowConfigUpdate(BaseModel):
    workflow_name: Optional[str] = None
    workflow_type: Optional[str] = None
    target_metric: Optional[str] = None
    measurement_unit: Optional[str] = None
    monthly_target: Optional[str] = None
    priority: Optional[str] = None
    sla_hours: Optional[int] = None
    quality_required: Optional[bool] = None
    data_points: Optional[Any] = None
    is_active: Optional[bool] = None
    primary_poc_id: Optional[Union[str, UUID]] = None
    secondary_poc_id: Optional[Union[str, UUID]] = None

class WorkflowConfig(WorkflowConfigBase):
    config_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[Union[str, UUID]] = None
    
    primary_poc: Optional[UserBase] = None
    secondary_poc: Optional[UserBase] = None

    class Config:
        orm_mode = True

# Workflow Volume Schemas
class WorkflowVolumeCreate(BaseModel):
    workflow_type: str
    date: date
    quantity: int
    analyst_id: Optional[Union[str, UUID]] = None

class WorkflowVolume(BaseModel):
    volume_id: int
    workflow_type: str
    date: date
    quantity: int
    analyst_id: Optional[Union[str, UUID]] = None
    recorded_at: datetime
    
    analyst: Optional[UserBase] = None

    class Config:
        orm_mode = True

# Task History Schema
class TaskHistory(BaseModel):
    history_id: int
    task_id: int
    changed_by: Optional[str] = None
    changed_at: datetime
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    action: Optional[str] = None
    notes: Optional[str] = None
    user: Optional[UserBase] = None

    class Config:
        orm_mode = True

# Task Comment Schemas
class TaskCommentBase(BaseModel):
    comment_text: str
    is_internal: bool = False

class TaskCommentCreate(TaskCommentBase):
    pass

class TaskComment(TaskCommentBase):
    comment_id: int
    task_id: int
    user_id: Optional[Union[str, UUID]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Notification Schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = "info"
    link: Optional[str] = None
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    notification_id: int
    user_id: Union[str, UUID]
    created_at: datetime

    class Config:
        orm_mode = True

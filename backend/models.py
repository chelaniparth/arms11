from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text, BigInteger, JSON, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

# Enums
class TaskStatus(str, enum.Enum):
    Pending = "Pending"
    In_Progress = "In Progress"
    Completed = "Completed"
    Under_Review = "Under Review"
    Paused = "Paused"

class TaskPriority(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"

class TaskType(str, enum.Enum):
    Tier_I = "Tier I"
    Tier_II = "Tier II"
    Audit = "Audit"
    Data_Entry = "Data Entry"
    Review = "Review"
    Strategy = "Strategy"
    Analysis = "Analysis"

class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    analyst = "analyst"

class WorkflowType(str, enum.Enum):
    Pending = "Pending"
    UCC = "UCC"
    Judgements = "Judgements"
    Chapter11 = "Chapter11"
    Chapter7 = "Chapter7"
    Trade_Tapes = "Trade Tapes"
    Volume = "Volume"
    Target = "Target"
    Credit_Application = "Credit Application"
    Trade_Reference = "Trade Reference"
    Liens = "Liens"
    Aging_Tracker = "Aging Tracker"
    QSR = "QSR"
    MLP = "MLP"
    PACA = "PACA"
    TNT = "TNT"
    CRA = "CRA"
    MSA = "MSA"
    Bond_Watch = "Bond Watch"
    Track_Ratings = "Track Ratings"

# Models

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "arms_workflow"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True) # For local auth
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, schema="arms_workflow"), nullable=False, default=UserRole.analyst)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    auth_user_id = Column(String) # Supabase Auth ID

    tasks = relationship("Task", back_populates="assigned_user")
    daily_volumes = relationship("WorkflowDailyVolume", back_populates="analyst")

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {"schema": "arms_workflow"}

    task_id = Column(Integer, primary_key=True, index=True)
    task_type = Column(Enum(TaskType, name="task_type", schema="arms_workflow", values_callable=lambda x: [e.value for e in x]), nullable=False)
    company_name = Column(String(500), nullable=False)
    document_type = Column(String(100), nullable=False)
    priority = Column(Enum("Low", "Medium", "High", "Critical", name="task_priority", schema="arms_workflow"), nullable=False, default="Medium")
    status = Column(Enum("Pending", "In Progress", "Completed", "Under Review", "Paused", name="task_status", schema="arms_workflow"), nullable=False, default="Pending")
    
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"))
    assigned_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    tier1_started_at = Column(DateTime(timezone=True))
    tier1_completed_at = Column(DateTime(timezone=True))
    tier2_started_at = Column(DateTime(timezone=True))
    tier2_completed_at = Column(DateTime(timezone=True))
    
    description = Column(Text)
    notes = Column(Text)
    source = Column(String(100))
    email_reference = Column(String(255))
    
    sla_hours = Column(Integer, default=72)
    due_date = Column(DateTime(timezone=True))

    # New columns for production tracking
    target_qty = Column(Integer, default=1)
    achieved_qty = Column(Integer, default=0)
    rating = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    picked_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Workflow Integration
    workflow_config_id = Column(Integer, ForeignKey("arms_workflow.workflow_configs.config_id"), nullable=True)
    custom_workflow_name = Column(String(255), nullable=True)

    assigned_user = relationship("User", back_populates="tasks")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

class TaskAttachment(Base):
    __tablename__ = "task_attachments"
    __table_args__ = {"schema": "arms_workflow"}

    attachment_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("arms_workflow.tasks.task_id"), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size_bytes = Column(BigInteger)
    storage_path = Column(Text, nullable=False)
    uploaded_by = Column(String, ForeignKey("arms_workflow.users.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_output = Column(Boolean, default=False)
    file_category = Column(String(50))

    task = relationship("Task", back_populates="attachments")

class TaskHistory(Base):
    __tablename__ = "task_history"
    __table_args__ = {"schema": "arms_workflow"}

    history_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("arms_workflow.tasks.task_id"), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    action = Column(String(50))
    notes = Column(Text)

    task = relationship("Task", back_populates="history")
    user = relationship("User")

class TaskComment(Base):
    __tablename__ = "task_comments"
    __table_args__ = {"schema": "arms_workflow"}

    comment_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("arms_workflow.tasks.task_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"))
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_internal = Column(Boolean, default=False)

    task = relationship("Task", back_populates="comments")

class WorkflowConfig(Base):
    __tablename__ = "workflow_configs"
    __table_args__ = {"schema": "arms_workflow"}

    config_id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(255), nullable=False, unique=True)
    workflow_type = Column(Enum(WorkflowType, name="workflow_type", schema="arms_workflow", values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # POC Assignment
    primary_poc_id = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"), nullable=True)
    secondary_poc_id = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"), nullable=True)
    
    target_metric = Column(String(100))
    measurement_unit = Column(String(100))
    monthly_target = Column(String(100))
    
    priority = Column(Enum(TaskPriority, schema="arms_workflow"), default=TaskPriority.Medium)
    sla_hours = Column(Integer, default=72)
    quality_required = Column(Boolean, default=True)
    
    data_points = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"))

    primary_poc = relationship("User", foreign_keys=[primary_poc_id])
    secondary_poc = relationship("User", foreign_keys=[secondary_poc_id])

class WorkflowDailyVolume(Base):
    __tablename__ = "workflow_daily_volumes"
    __table_args__ = {"schema": "arms_workflow"}

    volume_id = Column(Integer, primary_key=True, index=True)
    workflow_type = Column(Enum(WorkflowType, schema="arms_workflow", name="workflow_type", values_callable=lambda x: [e.value for e in x]), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    analyst_id = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    analyst = relationship("User", back_populates="daily_volumes")

class EmailTrigger(Base):
    __tablename__ = "email_triggers"
    __table_args__ = {"schema": "arms_workflow"}

    trigger_id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String(255), nullable=False)
    subject_pattern = Column(String(500))
    sender_whitelist = Column(Text) # Storing array as text or use ARRAY type if using postgres specific types
    auto_create_task = Column(Boolean, default=True)
    default_task_type = Column(Enum(TaskType, schema="arms_workflow"))
    default_priority = Column(Enum(TaskPriority, schema="arms_workflow"))
    workflow_config_id = Column(Integer, ForeignKey("arms_workflow.workflow_configs.config_id"))
    auto_assign = Column(Boolean, default=False)
    assign_to_user_id = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProcessedEmail(Base):
    __tablename__ = "processed_emails"
    __table_args__ = {"schema": "arms_workflow"}

    email_id = Column(Integer, primary_key=True, index=True)
    trigger_id = Column(Integer, ForeignKey("arms_workflow.email_triggers.trigger_id"))
    email_subject = Column(String(500))
    email_from = Column(String(255))
    email_date = Column(DateTime(timezone=True))
    email_body = Column(Text)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    task_created_id = Column(Integer, ForeignKey("arms_workflow.tasks.task_id"))
    processing_status = Column(String(50))
    error_message = Column(Text)

class DailyMetric(Base):
    __tablename__ = "daily_metrics"
    __table_args__ = {"schema": "arms_workflow"}

    metric_id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(Date, nullable=False, unique=True)
    total_tasks = Column(Integer, default=0)
    pending_tasks = Column(Integer, default=0)
    in_progress_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    under_review_tasks = Column(Integer, default=0)
    avg_completion_time_hours = Column(Numeric(10, 2))
    tasks_completed_on_time = Column(Integer, default=0)
    tasks_completed_late = Column(Integer, default=0)
    user_metrics = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserPerformance(Base):
    __tablename__ = "user_performance"
    __table_args__ = {"schema": "arms_workflow"}

    performance_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"), nullable=False)
    metric_date = Column(Date, nullable=False)
    tasks_assigned = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    tasks_in_progress = Column(Integer, default=0)
    avg_completion_time_hours = Column(Numeric(10, 2))
    tasks_under_review = Column(Integer, default=0)
    tasks_rejected = Column(Integer, default=0)
    quality_score = Column(Numeric(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationType(str, enum.Enum):
    info = "info"
    success = "success"
    warning = "warning"
    error = "error"

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {"schema": "arms_workflow"}

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("arms_workflow.users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType, schema="arms_workflow"), default=NotificationType.info)
    is_read = Column(Boolean, default=False)
    link = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

# Add relationship to User model
User.notifications = relationship("Notification", back_populates="user")

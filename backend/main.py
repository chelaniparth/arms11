from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import models, database, schemas
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ARMS Workflow Management System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to ARMS Workflow Management System API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Try to connect to DB
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

from routers import tasks, auth, users, workflows
app.include_router(tasks.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(workflows.router)
from routers import dashboard, notifications
app.include_router(dashboard.router)
app.include_router(notifications.router)

# ARMS Workflow Management System - Backend

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the `backend` directory with your database connection string:
    ```
    DATABASE_URL=postgresql://postgres:yourpassword@localhost/arms_workflow
    ```

3.  **Run the Server**:
    ```bash
    uvicorn main:app --reload
    ```

4.  **API Documentation**:
    Open [http://localhost:8000/docs](http://localhost:8000/docs) to see the Swagger UI.

## Structure

-   `main.py`: Entry point.
-   `models.py`: Database models.
-   `schemas.py`: Pydantic schemas.
-   `routers/`: API endpoints.

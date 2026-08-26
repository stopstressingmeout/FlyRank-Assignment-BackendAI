import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks built with FastAPI.",
    version="1.0.0"
)

@app.get(
    "/public/info",
    tags=["Auth"],
    summary="Public information"
)
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)

        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return response.user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@app.get(
    "/protected/profile",
    tags=["Auth"],
    summary="Get authenticated user profile"
)
def get_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email
    }

def get_postgres_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=5432,
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
initial_tasks = [
    {
        "id": 1,
        "title": "Chore 1",
        "done": False
    },
    {
        "id": 2,
        "title": "Chore 2",
        "done": True
    },
    {
        "id": 3,
        "title": "Chore 3",
        "done": True
    }
]


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str
    done: bool

class AuthRequest(BaseModel):
    email: str
    password: str


@app.post(
    "/auth/signup",
    tags=["Auth"],
    status_code=status.HTTP_201_CREATED
)
def signup(request: AuthRequest):
    try:
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })

        return {
            "message": "User created successfully",
            "user": response.user
        }

    except Exception as e:
        print("SIGNUP ERROR:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post(
    "/auth/login",
    tags=["Auth"]
)
def login(request: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        return {
            "access_token": response.session.access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        print("LOGIN ERROR:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
@app.get(
    "/",
    tags=["General"],
    summary="Get API information",
    description="Returns basic information about the Task API."
)
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get(
    "/health",
    tags=["General"],
    summary="Health check",
    description="Returns the health status of the API."
)
def health_check():
    return {"status": "ok"}


@app.get(
    "/tasks",
    tags=["Tasks"],
    summary="Get filtered tasks",
    description="Returns a list of filtered tasks."
)
def get_tasks(done: bool = None, search: str = None):

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks")
            rows = cursor.fetchall()

    formatted_tasks = []

    for row in rows:
        task = {
            "id": row[0],
            "title": row[1],
            "done": bool(row[2])
        }

        formatted_tasks.append(task)

    if done is not None:
        filtered_tasks = [
            task for task in formatted_tasks
            if task["done"] == done
        ]
    else:
        filtered_tasks = formatted_tasks

    if search is not None:
        filtered_tasks = [
            task for task in filtered_tasks
            if search.lower() in task["title"].lower()
        ]

    return filtered_tasks


@app.get(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Get a task by ID",
    description="Returns a single task if it exists."
)
def get_task(task_id: int):

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM tasks WHERE id = %s",
                (task_id,)
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }


@app.post(
    "/tasks",
    tags=["Tasks"],
    summary="Create a task",
    description="Creates a new task with the provided title.",
    status_code=status.HTTP_201_CREATED
)
def create_task(task: TaskCreate):

    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required"
        )

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
                (task.title, False)
            )

            new_id = cursor.fetchone()[0]
            connection.commit()

    return {
        "id": new_id,
        "title": task.title,
        "done": False
    }


@app.put(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Update a task",
    description="Updates the title and completion status of an existing task."
)
def update_task(task_id: int, updated_task: TaskUpdate):

    if not updated_task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required"
        )

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
                (updated_task.title, updated_task.done, task_id)
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found"
                )

            connection.commit()

            cursor.execute(
                "SELECT * FROM tasks WHERE id = %s",
                (task_id,)
            )

            row = cursor.fetchone()

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }


@app.delete(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Delete a task",
    description="Deletes a task by its ID.",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(task_id: int):

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tasks WHERE id = %s",
                (task_id,)
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found"
                )

            connection.commit()

    return


@app.get(
    "/stats",
    tags=["Tasks"],
    summary="Get task statistics",
    description="Returns statistics about the tasks."
)
def get_stats():

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) FROM tasks")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE done = TRUE"
            )
            done = cursor.fetchone()[0]

    open_tasks = total - done

    return {
        "total tasks": total,
        "done": done,
        "open": open_tasks
    }


@app.post("/reset")
def reset_tasks():

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("DELETE FROM tasks")

            for task in initial_tasks:
                cursor.execute(
                    "INSERT INTO tasks (id, title, done) VALUES (%s, %s, %s)",
                    (
                        task["id"],
                        task["title"],
                        task["done"]
                    )
                )

            connection.commit()

    return {
        "message": "Tasks reset successfully.",
        "tasks": initial_tasks
    }
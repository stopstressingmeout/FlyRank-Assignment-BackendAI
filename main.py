import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_postgres_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname=os.getenv("POSTGRES_DB"),
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD")
    )

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

if __name__ == "__main__":
    connection = get_postgres_connection()
    print("Successfully connected to PostgreSQL!")
    connection.close()

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks built with FastAPI.",
    version="1.0.0"
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


@app.get("/",tags=["General"],summary="Get API information",description="Returns basic information about the Task API.")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health",tags=["General"],summary="Health check",description="Returns the health status of the API.")
def health_check():
    return {"status": "ok"}


@app.get("/tasks",tags=["Tasks"],summary="Get filtered tasks",description="Returns a list of filtered tasks.")
def get_tasks(done: bool = None, search: str = None):
    connection = get_postgres_connection()
    cursor = connection.cursor()
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
        filtered_tasks=[
            task for task in formatted_tasks
            if task["done"] == done
        ]
    else:
        filtered_tasks=formatted_tasks

    if search is not None:
        filtered_tasks=[
            task for task in filtered_tasks
            if search.lower() in task["title"].lower()
        ]
    return filtered_tasks


@app.get("/tasks/{task_id}",
         tags=["Tasks"],
         summary="Get a task by ID",
         description="Returns a single task if it exists.")
def get_task(task_id: int):

    connection = get_postgres_connection()
    cursor = connection.cursor()

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

    connection = get_postgres_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        (task.title, False)
    )

    new_id = cursor.fetchone()[0]
    connection.commit()

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    return new_task

class TaskUpdate(BaseModel):
    title:str
    done:bool

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

    connection = get_postgres_connection()
    cursor = connection.cursor()

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

    connection = get_postgres_connection()
    cursor = connection.cursor()

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

    connection = get_postgres_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_result = cursor.fetchone()
    total = total_result[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = TRUE")
    done_result = cursor.fetchone()
    done = done_result[0]

    open_tasks = total - done

    return {
        "total tasks": total,
        "done": done,
        "open": open_tasks
    }
@app.post("/reset")
def reset_tasks():

    connection = get_postgres_connection()
    cursor = connection.cursor()

    # Delete all existing tasks
    cursor.execute("DELETE FROM tasks")

    # Insert the original tasks back into the database
    for task in initial_tasks:
        cursor.execute(
            "INSERT INTO tasks (id, title, done) VALUES (%s, %s, %s)",
            (task["id"], task["title"], task["done"])
        )

    connection.commit()

    return {
        "message": "Tasks reset successfully.",
        "tasks": initial_tasks
    }


import sqlite3
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from copy import deepcopy

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
connection = sqlite3.connect("tasks.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title TEXT,
        done BOOLEAN
    )
""")
cursor.execute("SELECT COUNT(*) FROM tasks")
result = cursor.fetchone()
if result[0] == 0:
    for task in initial_tasks:
        cursor.execute(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            (task["id"], task["title"], task["done"])
        )

    connection.commit()

# In-memory database

tasks=deepcopy(initial_tasks)
current_id=len(tasks)    


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
    connection = sqlite3.connect("tasks.db")
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

    return formatted_tasks


@app.get("/tasks/{task_id}",
    tags=["Tasks"],
    summary="Get a task by ID",
    description="Returns a single task if it exists.")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


@app.post("/tasks",tags=["Tasks"],summary="Create a task",description="Creates a new task with the provided title.", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    global current_id
    new_id=current_id + 1

    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required"
        )

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)
    current_id=new_id  

    return new_task


class TaskUpdate(BaseModel):
    title:str
    done:bool

@app.put("/tasks/{task_id}", tags=["Tasks"], summary="Update a task", description="Updates the title and completion status of an existing task.")
def update_task(task_id:int,updated_task:TaskUpdate):
    if not updated_task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required"
        )

    for task in tasks:
        if task["id"] == task_id:
            task["title"] = updated_task.title
            task["done"] = updated_task.done
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

@app.delete("/tasks/{task_id}", tags=["Tasks"],summary="Delete a task",description="Deletes a task by its ID.", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

@app.get("/stats",tags=["Tasks"],summary="Get task statistics",description="Returns statistics about the tasks.")
def get_tasks():
    total=len(tasks)
    done=0
    for task in tasks:
        if task["done"]:
            done+=1

    open_tasks=total-done
    return {
        "total tasks":total,
        "done":done,
        "open":open_tasks
    }

@app.post("/reset")
def reset_tasks():
    global tasks
    global current_id

    tasks=deepcopy(initial_tasks)
    current_id=len(tasks)

    return {"message":"Tasks reset successfully.",
            "tasks":tasks}



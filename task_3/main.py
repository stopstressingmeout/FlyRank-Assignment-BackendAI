from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# In-memory database
tasks = [
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

current_id=len(tasks)    


class TaskCreate(BaseModel):
    title: str


@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
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
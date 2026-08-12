# Task API — FastAPI + SQLite

A simple CRUD API for managing tasks built with FastAPI and SQLite.

## Virtual Environment Setup (Windows - Command Prompt)

Follow these steps to create and run the project.

### 1. Create a Virtual Environment

If you haven't already created one, run:

```cmd
python -m venv venv
```

### 2. Activate the Virtual Environment

```cmd
venv\Scripts\activate
```

> **Note:** You are inside the virtual environment when your terminal prompt starts with `(venv)`.

### 3. Install Dependencies

```cmd
pip install "fastapi[standard]"
```

### 4. Start the FastAPI Development Server

Since the application entry point (`main.py`) is located at the project root, run:

```cmd
fastapi dev main.py
```

Alternatively, start the app with `uvicorn`:

```cmd
uvicorn main:app --reload
```

### 5. Access the API

Once the server starts, open:

* **API:** http://127.0.0.1:8000
* **Swagger UI:** http://127.0.0.1:8000/docs
* **ReDoc:** http://127.0.0.1:8000/redoc

---

## Why SQLite?

SQLite was used to store tasks instead of keeping them only in a Python list.

The database is stored in a local `tasks.db` file. The application automatically creates the database and the `tasks` table if they do not already exist.

Three example tasks are inserted when the table is empty. This prevents the example tasks from being duplicated every time the application starts.

Using SQLite also allows task data to persist between server restarts instead of being lost when the Python application stops.

---

## Database Structure

The project uses a `tasks` table with three columns:

| Column  | Type    | Description                                 |
| ------- | ------- | ------------------------------------------- |
| `id`    | INTEGER | Primary key for each task                   |
| `title` | TEXT    | Task title                                  |
| `done`  | BOOLEAN | Completion status (`0` = false, `1` = true) |

The database file is created automatically when the application runs.

> `tasks.db` is stored locally and is ignored by Git. A fresh clone creates its own database when the application is started.

---

## API Endpoints

The API provides the following CRUD endpoints:

| Method | Endpoint           | Description             |
| ------ | ------------------ | ----------------------- |
| GET    | `/tasks`           | Get all tasks           |
| GET    | `/tasks/{task_id}` | Get a task by ID        |
| POST   | `/tasks`           | Create a new task       |
| PUT    | `/tasks/{task_id}` | Update an existing task |
| DELETE | `/tasks/{task_id}` | Delete a task           |

### Example Task

```json
{
    "id": 1,
    "title": "Chore 1",
    "done": false
}
```

---

## Example SQL Query

The application uses parameterized SQL queries when working with task IDs.

For example:

```sql
SELECT * FROM tasks WHERE id = ?;
```

The task ID is supplied separately as a parameter rather than being directly inserted into the SQL string.

Another example used while exploring the database is:

```sql
SELECT * FROM tasks WHERE done = 1;
```

This returns all completed tasks.

---

## Viewing the Database with DB Browser for SQLite

The SQLite database can be inspected using **DB Browser for SQLite**.

Open:

```text
tasks.db
```

and select the `tasks` table under **Browse Data**.

The seeded database contains three example tasks:

| id | title   | done |
| -: | ------- | ---: |
|  1 | Chore 1 |    0 |
|  2 | Chore 2 |    1 |
|  3 | Chore 3 |    1 |

### Database Screenshot

Add a screenshot of the `tasks` table from DB Browser for SQLite here.

```text
[Insert DB Browser screenshot here]
```

---

## Testing the API

The API can be tested through the automatically generated Swagger UI:

```text
http://127.0.0.1:8000/docs
```

The CRUD endpoints can be tested using the Swagger interface to verify that tasks can be:

* Retrieved
* Retrieved by ID
* Created
* Updated
* Deleted

The database can also be opened in DB Browser to verify that changes made through the API are stored in SQLite.

---

## Project Structure

```text
Flyrank_Api/
│
├── main.py
├── .gitignore
├── README.md
└── tasks.db
```

> `tasks.db` is generated locally when the application runs and is not tracked by Git.

---

## Running the Project from a Clean Clone

After cloning the repository:

```cmd
python -m venv venv
venv\Scripts\activate
pip install "fastapi[standard]"
fastapi dev main.py
```

The application will automatically create the SQLite database and `tasks` table if they do not already exist.

Open the Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

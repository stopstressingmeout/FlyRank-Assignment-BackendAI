# Task API — FastAPI + PostgreSQL + Docker

A simple CRUD API for managing tasks built with **FastAPI and PostgreSQL**.

This version of the project containerizes both the FastAPI application and PostgreSQL database using **Docker and Docker Compose**.

The complete application can be started with a single command:

```cmd
docker compose up
```

The project previously used SQLite for data storage. It has now been migrated to PostgreSQL, which runs in its own Docker container.

---

## Docker and PostgreSQL Setup

This project uses Docker Compose to run two services together:

1. **FastAPI API**
2. **PostgreSQL database**

The architecture looks like this:

```text
                    Docker Compose
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      ┌──────────────┐          ┌──────────────┐
      │   FastAPI    │          │ PostgreSQL   │
      │     API      │◄────────►│   Database   │
      │              │          │              │
      │ taskapi-     │          │ taskdb-      │
      │ compose      │          │ compose      │
      └──────────────┘          └──────┬───────┘
                                       │
                                       ▼
                                 taskdata volume
```

Docker Compose automatically creates a network that allows the FastAPI container to communicate with the PostgreSQL container.

The API uses:

```text
POSTGRES_HOST=db
```

Here, `db` is the name of the PostgreSQL service defined in `docker-compose.yml`.

Inside Docker Compose, the API does not connect to PostgreSQL using `localhost`. Instead, it connects to the database service through the Docker network.

---

## Environment Variables

Database configuration is stored using environment variables.

Create a `.env` file in the project root.

Example:

```text
POSTGRES_PASSWORD=your_password
POSTGRES_DB=tasks
```

The `.env` file is ignored by Git and is not committed to the repository.

A safe configuration template is provided through:

```text
.env.example
```

Example:

```text
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=tasks
```

Another developer can copy `.env.example` and create their own `.env` file.

### Why use `.env`?

Database credentials should not be hardcoded in the source code or committed to GitHub.

Docker Compose reads the environment variables from `.env` and passes them to the containers.

For example:

```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

Docker Compose replaces:

```text
${POSTGRES_PASSWORD}
```

with the value stored in `.env`.

This keeps sensitive configuration separate from the application code.

---

## Running the Project with Docker

Make sure Docker Desktop is running.

To start the complete application:

```cmd
docker compose up
```

Docker Compose will:

1. Start the PostgreSQL database.
2. Create or connect to the PostgreSQL volume.
3. Build the FastAPI Docker image.
4. Start the FastAPI application.
5. Connect the FastAPI application to PostgreSQL.

To run the containers in the background:

```cmd
docker compose up -d
```

To check the running containers:

```cmd
docker compose ps
```

The project should run two containers:

```text
taskapi-compose
taskdb-compose
```

The FastAPI API is available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Why PostgreSQL?

The previous version of this project used SQLite to store tasks.

SQLite is useful for small applications because the entire database is stored in a local file.

However, this version uses PostgreSQL.

PostgreSQL is a separate database server that runs independently from the FastAPI application.

The architecture is now:

```text
FastAPI Application
        │
        │ Database Connection
        ▼
PostgreSQL Database
```

Both parts run inside separate Docker containers.

This makes the project closer to a real-world backend application where the API and database are independent services.

---

## Database Structure

The project uses a PostgreSQL database named:

```text
tasks
```

The application stores task information in a `tasks` table.

The table contains three columns:

| Column  | Type    | Description |
| ------- | ------- | ----------- |
| `id`    | INTEGER | Primary key for each task |
| `title` | TEXT | Task title |
| `done`  | BOOLEAN | Completion status |

The application creates the `tasks` table if it does not already exist.

Three example tasks are also inserted when the table is empty.

This prevents the example tasks from being duplicated every time the application or containers restart.

The initial tasks are:

| id | title | done |
| -: | ----- | ---- |
| 1 | Chore 1 | false |
| 2 | Chore 2 | true |
| 3 | Chore 3 | true |

---

## Database Connection

The FastAPI application connects to PostgreSQL using environment variables.

The application reads:

```text
POSTGRES_HOST
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

The database connection is configured through:

```python
host=os.getenv("POSTGRES_HOST")
dbname=os.getenv("POSTGRES_DB")
user=os.getenv("POSTGRES_USER")
password=os.getenv("POSTGRES_PASSWORD")
```

This allows the same application code to use different database configurations without changing the Python source code.

When running through Docker Compose, the PostgreSQL hostname is:

```text
db
```

because `db` is the name of the database service.

---

## PostgreSQL Data Persistence

PostgreSQL data is stored using a named Docker volume.

The project uses:

```text
taskdata
```

The volume is mounted inside the PostgreSQL container at:

```text
/var/lib/postgresql/data
```

This is important because containers themselves are temporary.

Without a volume, database data could be lost when containers are removed.

The data flow is:

```text
PostgreSQL Container
        │
        ▼
/var/lib/postgresql/data
        │
        ▼
taskdata Docker Volume
```

Because of this volume, data survives a Docker Compose restart.

For example:

```cmd
docker compose down
```

removes the containers and network.

Then:

```cmd
docker compose up -d
```

creates the containers again.

The PostgreSQL data remains because the Docker volume still exists.

---

## Persistence Test

Database persistence was tested by creating a task:

```json
{
    "id": 8,
    "title": "Persistence Test",
    "done": false
}
```

The Docker Compose stack was then stopped:

```cmd
docker compose down
```

The containers were removed and started again:

```cmd
docker compose up -d
```

After restarting, the task was requested again:

```cmd
curl -i http://127.0.0.1:8000/tasks/8
```

The API returned:

```text
HTTP/1.1 200 OK
```

with:

```json
{
    "id": 8,
    "title": "Persistence Test",
    "done": false
}
```

This confirms that the PostgreSQL Docker volume preserves the database data across container restarts.

---

## API Endpoints

The API provides the following CRUD endpoints:

| Method | Endpoint | Description | Success Status |
| ------ | -------- | ----------- | -------------- |
| GET | `/tasks` | Get all tasks | 200 |
| GET | `/tasks/{task_id}` | Get a task by ID | 200 |
| POST | `/tasks` | Create a new task | 201 |
| PUT | `/tasks/{task_id}` | Update an existing task | 200 |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 |

---

## Get All Tasks

Retrieve all tasks:

```cmd
curl -i http://127.0.0.1:8000/tasks
```

Example response:

```text
HTTP/1.1 200 OK
```

Example JSON:

```json
[
    {
        "id": 1,
        "title": "Chore 1",
        "done": false
    },
    {
        "id": 2,
        "title": "Chore 2",
        "done": true
    },
    {
        "id": 3,
        "title": "Chore 3",
        "done": true
    }
]
```

---

## Get a Task by ID

Retrieve a specific task:

```cmd
curl -i http://127.0.0.1:8000/tasks/1
```

Example response:

```text
HTTP/1.1 200 OK
```

Example JSON:

```json
{
    "id": 1,
    "title": "Chore 1",
    "done": false
}
```

If a task does not exist:

```cmd
curl -i http://127.0.0.1:8000/tasks/999
```

The API returns:

```text
HTTP/1.1 404 Not Found
```

---

## Create a Task

Create a new task:

```cmd
curl -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"New Task\",\"done\":false}"
```

A successful request returns:

```text
HTTP/1.1 201 Created
```

Example response:

```json
{
    "id": 7,
    "title": "New Task",
    "done": false
}
```

> The task ID may be different depending on the current state of the database.

---

## Update a Task

Update an existing task:

```cmd
curl -i -X PUT http://127.0.0.1:8000/tasks/1 -H "Content-Type: application/json" -d "{\"title\":\"Updated Task\",\"done\":true}"
```

A successful request returns:

```text
HTTP/1.1 200 OK
```

Example response:

```json
{
    "id": 1,
    "title": "Updated Task",
    "done": true
}
```

---

## Delete a Task

Delete a task:

```cmd
curl -i -X DELETE http://127.0.0.1:8000/tasks/7
```

A successful request returns:

```text
HTTP/1.1 204 No Content
```

After deletion, requesting the same task:

```cmd
curl -i http://127.0.0.1:8000/tasks/7
```

returns:

```text
HTTP/1.1 404 Not Found
```

---

## Status Codes

The API uses appropriate HTTP status codes.

| Status Code | Meaning | Used For |
| ----------- | ------- | -------- |
| 200 | OK | Successful GET and PUT requests |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 404 | Not Found | Task ID does not exist |

---

## Parameterized SQL Queries

The application uses parameterized SQL queries when working with PostgreSQL.

For example, PostgreSQL queries using `psycopg` use `%s` placeholders:

```sql
SELECT * FROM tasks WHERE id = %s;
```

The task ID is supplied separately as a parameter rather than being directly inserted into the SQL string.

This helps prevent SQL injection.

The same principle is used when retrieving, updating, or deleting tasks.

---

## Inspecting the PostgreSQL Database

The PostgreSQL database can be inspected directly from the running container.

Open the PostgreSQL shell:

```cmd
docker exec -it taskdb-compose psql -U postgres -d tasks
```

Inside PostgreSQL, list the tables:

```sql
\dt
```

View the tasks:

```sql
SELECT * FROM tasks;
```

Exit PostgreSQL:

```sql
\q
```

This provides direct confirmation that the FastAPI API is storing data inside PostgreSQL.

---

## Database Screenshot

A PostgreSQL database screenshot should show the `tasks` table and its stored data.

After creating the screenshot, add it to the repository and reference it here:

```markdown
![PostgreSQL Database](postgres-db.png)
```

For example, the screenshot can show the result of:

```sql
SELECT * FROM tasks;
```

inside the PostgreSQL container.

> The old SQLite `db-browser.png` screenshot should not be used as evidence for this PostgreSQL version.

---

## Testing the API

The API can be tested through the automatically generated Swagger UI:

```text
http://127.0.0.1:8000/docs
```

The CRUD endpoints can also be tested using `curl`.

The following functionality has been verified:

- Tasks can be retrieved.
- A task can be retrieved by ID.
- Unknown tasks return `404`.
- New tasks can be created.
- Existing tasks can be updated.
- Tasks can be deleted.
- Deleted tasks return `404`.
- Data persists after restarting Docker Compose.

---

## Stopping the Project

To stop and remove the containers:

```cmd
docker compose down
```

The PostgreSQL data remains because it is stored in the named Docker volume.

To remove the containers and database volume:

```cmd
docker compose down -v
```

> **Warning:** `docker compose down -v` removes the PostgreSQL volume and deletes the stored database data.

---

## Project Structure

```text
Flyrank_Api/
│
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
│
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
│
├── init/
│
├── README.md
│
└── postgres-db.png
```

### Important Notes

- `.env` contains local configuration and is ignored by Git.
- `.env.example` provides a safe configuration template.
- `docker-compose.yml` starts both FastAPI and PostgreSQL.
- `Dockerfile` builds the FastAPI application image.
- PostgreSQL data is stored in the `taskdata` Docker volume.

---

## Running the Project from a Clean Clone

After cloning the repository:

```cmd
git clone <your-repository-url>
cd Flyrank_Api
```

Create your environment file:

```cmd
copy .env.example .env
```

Update the `.env` file if necessary.

Then start Docker Desktop and run:

```cmd
docker compose up
```

Or run in detached mode:

```cmd
docker compose up -d
```

Docker Compose will start both:

```text
FastAPI API
PostgreSQL Database
```

No manual PostgreSQL installation is required.

Open Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

---

## Assignment Checklist

| Requirement | Status |
| ----------- | ------ |
| PostgreSQL running in Docker | Completed |
| FastAPI running in Docker | Completed |
| Docker Compose manages both services | Completed |
| Environment variables used for database configuration | Completed |
| `.env` ignored by Git | Completed |
| `.env.example` included | Completed |
| GET `/tasks` returns 200 | Completed |
| GET `/tasks/{id}` returns 200 | Completed |
| Unknown task returns 404 | Completed |
| POST `/tasks` returns 201 | Completed |
| PUT `/tasks/{id}` returns 200 | Completed |
| DELETE `/tasks/{id}` returns 204 | Completed |
| PostgreSQL data persists after restart | Completed |
| Parameterized SQL queries used | Completed |
| Swagger documentation available | Completed |

---

## Conclusion

This project demonstrates the migration of a simple FastAPI Task API from SQLite to PostgreSQL.

The application now runs as a containerized system where:

```text
FastAPI
   ↓
Docker Compose Network
   ↓
PostgreSQL
   ↓
Docker Volume
```

Docker Compose makes it possible to start the complete application stack with a single command:

```cmd
docker compose up
```

The PostgreSQL database runs independently from the API, configuration is handled through environment variables, and the Docker volume ensures that task data persists across container restarts.
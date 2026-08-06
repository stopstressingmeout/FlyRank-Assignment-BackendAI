# Virtual Environment Setup (Windows - Command Prompt)

Follow these steps to create and run the project.

## 1. Create a Virtual Environment

If you haven't already created one, run:


```cmd
python -m venv venv
```

## 2. Activate the Virtual Environment

```cmd
venv\Scripts\activate
```

> **Note:** You are inside the virtual environment when your terminal prompt starts with `(venv)`.

## 3. Install Dependencies

```cmd
pip install "fastapi[standard]"
```

## 4. Start the FastAPI Development Server

Since the application entry point (`main.py`) is located at the project root, run:

```cmd
fastapi dev main.py
```

Alternatively, start the app with `uvicorn`:

```cmd
uvicorn main:app --reload
```

## 5. Access the API

Once the server starts, open:

- **API:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
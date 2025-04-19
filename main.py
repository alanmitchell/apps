from typing import Callable, Coroutine
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import marimo
import os
import logging
from dotenv import load_dotenv
from fastapi import Form
from app_info import app_info

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notebook_dir = os.path.join(os.path.dirname(__file__), "notebooks")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

server = marimo.create_asgi_app()
app_list = []

for filename in sorted(os.listdir(notebook_dir)):
    if filename.endswith(".py"):
        app_name = os.path.splitext(filename)[0]
        app_path = os.path.join(notebook_dir, filename)
        server = server.with_app(path=f"/{app_name}", root=app_path)
        if app_name in app_info:
            app_list.append((app_name, app_info[app_name][0], app_info[app_name][1]))

# Create a FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory=templates_dir)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request, "app_list": app_list}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error occurred: {exc.detail}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "detail": exc.detail},
        status_code=exc.status_code,
    )

app.mount("/", server.build())

# Add session middleware
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key")
)

# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000, log_level="info")

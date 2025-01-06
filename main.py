from routes.auth import router as auth_router
from routes.videos import router as video_router
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import login, register_creator, register_consumer

app = FastAPI()

# Set up templates
templates = Jinja2Templates(directory="templates")  # Place the HTML files in a `templates` directory.
app.mount("/static", StaticFiles(directory="static"), name="static")  # Optional static files.

# CORS middleware for frontend-backend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="", tags=["Authentication"])
app.include_router(video_router, prefix="", tags=["Videos"])

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


#
# @app.get("/", response_class=HTMLResponse, name="home")
# async def home(request: Request):
#     return RedirectResponse(url="/login")
#
# @app.get("/login", response_class=HTMLResponse, name="login_page")
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})
#
# @app.get("/register", response_class=HTMLResponse, name="register_page")
# async def register_page(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})
#
# @app.post("/register", response_class=HTMLResponse, name="register")
# async def register_user(
#     request: Request,
#     username: str = Form(...),
#     password: str = Form(...),
#     user_type: str = Form(...),
# ):
#     if user_type == "creator":
#         await register_creator(username=username, password=password)
#     elif user_type == "consumer":
#         await register_consumer(username=username, password=password)
#     else:
#         return templates.TemplateResponse(
#             "register.html", {"request": request, "error": "Invalid user type"}
#         )
#     return RedirectResponse(url="/login", status_code=302)
#
#
# @app.get("/timeline", response_class=HTMLResponse, name="consumer_timeline")
# async def consumer_timeline(request: Request):
#     return templates.TemplateResponse("timeline.html", {"request": request})

from routes.auth import router as auth_router
from routes.videos import router as video_router
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
from fastapi import FastAPI, File, UploadFile, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Define the maximum file size in bytes (e.g., 50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# Define the maximum file size in bytes (e.g., 50 MB)

class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_size: int):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > self.max_size:
            raise HTTPException(status_code=413, detail="File size too large")
        return await call_next(request)


# Correctly add the middleware using a factory pattern
app.add_middleware(LimitUploadSizeMiddleware, max_size=MAX_FILE_SIZE)


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

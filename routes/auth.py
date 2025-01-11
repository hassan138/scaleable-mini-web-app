# from typing import Optional
#
# from bson import ObjectId
# from fastapi import APIRouter, HTTPException, Depends, Form
# from fastapi.security import OAuth2PasswordRequestForm
# from datetime import datetime, timedelta
#
# from starlette.responses import RedirectResponse
#
# from models.users import User
# from config import pwd_context, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, oauth2_scheme, db
# from utils.helpers import serialize_user
# import jwt
#
# # Router initialization
# router = APIRouter()
#
#
# # Helper functions
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
#
# def get_user(username: str):
#     user = db.users.find_one({"username": username})
#     if user:
#         return User(**user)
#
#
# def authenticate_user(username: str, password: str):
#     user = get_user(username)
#     if user and verify_password(password, user.hashed_password):
#         return user
#     return None
#
#
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#
#
# @router.post("/token", name="login_token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = db.users.find_one({"username": form_data.username})
#     if not user or not verify_password(form_data.password, user["hashed_password"]):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#
#     # Create access token
#     access_token = create_access_token(data={"sub": user["username"]})
#
#     # Serialize user data
#     user_data = serialize_user(user)
#
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": user_data
#     }
#
#
#
#
# @router.get("/users/me", response_model=User)
# async def read_users_me(token: str = Depends(oauth2_scheme)):
#     try:
#         # Decode the token
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#
#         # Ensure the username exists in the token payload
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#
#     # Retrieve user from database
#     user = get_user(username)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     return user
#
#
# # Routes
# # User APIs
# @router.get("/users/{user_id}")
# async def get_user_profile(user_id: str):
#     user = db.users.find_one({"_id": ObjectId(user_id)})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return serialize_user(user)
#
#
# @router.put("/users/{user_id}")
# async def update_user_profile(user_id: str, username: str = Form(None), password: str = Form(None)):
#     updates = {}
#     if username:
#         updates["username"] = username
#     if password:
#         updates["hashed_password"] = password
#     if not updates:
#         raise HTTPException(status_code=400, detail="No updates provided")
#     db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
#     return {"detail": "User profile updated"}
#
#
# # Routes
# @router.post("/register/creator",  name="register_creator")
# async def register_creator(username: str = Form(...), password: str = Form(...)):
#     user = {
#         "username": username,
#         "hashed_password": get_password_hash(password),
#         "is_creator": True,
#     }
#
#     result = db.users.insert_one(user)
#     user["_id"] = result.inserted_id
#     return serialize_user(user)
#
#
# @router.post("/register/consumer",  name="register_consumer")
# async def register_consumer(username: str = Form(...), password: str = Form(...)):
#     user = {
#         "username": username,
#         "hashed_password": get_password_hash(password),
#         "is_creator": False,
#     }
#
#     result = db.users.insert_one(user)
#     user["_id"] = result.inserted_id
#     return serialize_user(user)
#
#
# @router.post("/users/{user_id}/reset-password")
# async def reset_password(user_id: str, new_password: str = Form(...)):
#     hashed_password = get_password_hash(new_password)
#     db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"hashed_password": hashed_password}})
#     return {"detail": "Password reset successfully"}
#
#
# @router.get("/users")
# async def list_users(skip: int = 0, limit: int = 10):
#     users = db.users.find().skip(skip).limit(limit)
#     return [serialize_user(user) for user in users]
#
#
# @router.get("/users/search")
# async def search_users(query: str):
#     users = db.users.find({"username": {"$regex": query, "$options": "i"}})
#     return [serialize_user(user) for user in users]
#
#
# @router.put("/users/{user_id}/deactivate")
# async def deactivate_user(user_id: str):
#     db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"active": False}})
#     return {"detail": "User account deactivated"}
#
#
# @router.get("/dashboard/{creator_id}")
# async def creator_dashboard(creator_id: str):
#     # Fetch videos by the creator
#     videos = list(db.videos.find({"creator_id": ObjectId(creator_id)}))
#
#     # Aggregate likes and comments for each video
#     dashboard_data = []
#     for video in videos:
#         video_id = video["_id"]
#         like_count = db.likes.count_documents({"video_id": video_id})
#         comment_count = db.comments.count_documents({"video_id": video_id})
#
#         dashboard_data.append({
#             "video_id": str(video_id),
#             "title": video.get("title"),
#             "description": video.get("description"),
#             "likes": like_count,
#             "comments": comment_count,
#             "upload_date": video.get("upload_date"),
#         })
#
#     return dashboard_data
#
#
# @router.delete("/users/{user_id}")
# async def delete_user(user_id: str, token: str = Depends(oauth2_scheme)):
#     try:
#         # Decode the token and get the username
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#
#         # Ensure the username exists in the token payload
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#
#     # Retrieve the user making the request
#     admin_user = get_user(username)
#     if admin_user is None:
#         raise HTTPException(status_code=404, detail="Admin user not found")
#
#     # Check if the user making the request has admin privileges
#     if not admin_user.is_admin:
#         raise HTTPException(status_code=403, detail="You do not have permission to delete users")
#
#     # Fetch the user to be deleted
#     user_to_delete = db.users.find_one({"_id": ObjectId(user_id)})
#     if not user_to_delete:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     # Proceed to delete the user
#     db.users.delete_one({"_id": ObjectId(user_id)})
#
#     return {"detail": f"User with ID {user_id} has been deleted successfully"}
#
#
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta


from models.users import User
from config import pwd_context, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, oauth2_scheme, db
from utils.helpers import serialize_user
import jwt

# Router initialization
router = APIRouter()
db.users.create_index([("username", 1)], unique=True)
db.videos.create_index([("title", "text"), ("description", "text")], name="video_text_search_index")


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    user = db.users.find_one({"username": username})
    if user:
        return User(**user)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token", name="login_token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create access token
    access_token = create_access_token(data={"sub": user["username"]})

    # Serialize user data
    user_data = serialize_user(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

# User APIs
@router.get("/users/{user_id}")
async def get_user_profile(user_id: str):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user(user)


@router.put("/users/{user_id}")
async def update_user_profile(user_id: str, username: str = Form(None), password: str = Form(None)):
    updates = {}
    if username:
        # Check if username is unique
        existing_user = db.users.find_one({"username": username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        updates["username"] = username
    if password:
        updates["hashed_password"] = get_password_hash(password)
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return {"detail": "User profile updated"}


# Routes
@router.post("/register/creator", name="register_creator")
async def register_creator(username: str = Form(...), password: str = Form(...)):
    # Check if username is unique
    if db.users.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = {
        "username": username,
        "hashed_password": get_password_hash(password),
        "is_creator": True,
    }

    result = db.users.insert_one(user)
    user["_id"] = result.inserted_id
    return serialize_user(user)


@router.post("/register/consumer", name="register_consumer")
async def register_consumer(username: str = Form(...), password: str = Form(...)):
    # Check if username is unique
    if db.users.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = {
        "username": username,
        "hashed_password": get_password_hash(password),
        "is_creator": False,
    }

    result = db.users.insert_one(user)
    user["_id"] = result.inserted_id
    return serialize_user(user)


@router.post("/users/{user_id}/reset-password")
async def reset_password(user_id: str, new_password: str = Form(...)):
    hashed_password = get_password_hash(new_password)
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"hashed_password": hashed_password}})
    return {"detail": "Password reset successfully"}


@router.get("/users")
async def list_users(skip: int = 0, limit: int = 10):
    users = db.users.find().skip(skip).limit(limit)
    return [serialize_user(user) for user in users]


@router.get("/users/search")
async def search_users(query: str):
    users = db.users.find({"username": {"$regex": query, "$options": "i"}})
    return [serialize_user(user) for user in users]


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str):
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"active": False}})
    return {"detail": "User account deactivated"}


@router.get("/dashboard/{creator_id}")
async def creator_dashboard(creator_id: str):
    # Fetch videos by the creator
    videos = list(db.videos.find({"creator_id": ObjectId(creator_id)}))

    # Aggregate likes and comments for each video
    dashboard_data = []
    for video in videos:
        video_id = video["_id"]
        like_count = db.likes.count_documents({"video_id": video_id})
        comment_count = db.comments.count_documents({"video_id": video_id})

        dashboard_data.append({
            "video_id": str(video_id),
            "title": video.get("title"),
            "description": video.get("description"),
            "likes": like_count,
            "comments": comment_count,
            "upload_date": video.get("upload_date"),
        })

    return dashboard_data


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, token: str = Depends(oauth2_scheme)):
    try:
        # Decode the token and get the username
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        # Ensure the username exists in the token payload
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Retrieve the user making the request
    admin_user = get_user(username)
    if admin_user is None:
        raise HTTPException(status_code=404, detail="Admin user not found")

    # Check if the user making the request has admin privileges
    if not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="You do not have permission to delete users")

    # Fetch the user to be deleted
    user_to_delete = db.users.find_one({"_id": ObjectId(user_id)})
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    # Proceed to delete the user
    db.users.delete_one({"_id": ObjectId(user_id)})

    return {"detail": f"User with ID {user_id} has been deleted successfully"}

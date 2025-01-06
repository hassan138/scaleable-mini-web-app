from fastapi import FastAPI, HTTPException, Depends
from pymongo import MongoClient
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from bson import ObjectId
from datetime import timedelta, datetime
import jwt

# Constants
SECRET_KEY = "your_secret_key"  # Replace with a secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 6000

# MongoDB setup
DATABASE_URL = "mongodb+srv://hassan bilal:nanotech007@bitpic.vkyjc.mongodb.net/?retryWrites=true&w=majority&appName=bitpic"
client = MongoClient(DATABASE_URL)
db = client["video_platform"]
users_collection = db["users"]

# Cryptography setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI instance
app = FastAPI()

# Pydantic model for User
class User(BaseModel):
    username: str
    password: str
    is_admin: bool


# Helper function to hash the password
def hash_password(password: str):
    return pwd_context.hash(password)


# Function to check if superadmin exists and create one if not
def create_superadmin():
    # Check if the user "admin" exists
    admin_user = users_collection.find_one({"username": "admin"})

    if not admin_user:
        # Hash the password for the admin user
        hashed_password = hash_password("admin")
        superadmin_data = {
            "username": "admin",
            "password": hashed_password,
            "is_admin": True,
        }

        # Insert the superadmin into the collection
        users_collection.insert_one(superadmin_data)
        return "Superadmin created successfully."
    else:
        return "Superadmin already exists."



print(create_superadmin())
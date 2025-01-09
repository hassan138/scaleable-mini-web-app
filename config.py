from pymongo import MongoClient
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer



# Constants
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 6000

# MongoDB setup
DATABASE_URL = "mongodb+srv://hassan bilal:nanotech007@bitpic.vkyjc.mongodb.net/?retryWrites=true&w=majority&appName=bitpic"
client = MongoClient(DATABASE_URL)
db = client["video_platform"]

# Cryptography setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



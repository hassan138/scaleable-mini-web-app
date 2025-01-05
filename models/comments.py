from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from utils.helpers import PyObjectId


# Comment model

class Comment(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    content: str
    video_id: PyObjectId
    user_id: PyObjectId
    timestamp: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

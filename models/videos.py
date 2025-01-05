from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from utils.helpers import PyObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from utils.helpers import PyObjectId
from bson import ObjectId
# Video model

class Video(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    hashtags: List[str]
    filename: str
    upload_date: datetime
    creator_id: PyObjectId

    class Config:
        # Allow population by field name and allow arbitrary types like PyObjectId
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

        # Custom encoder for ObjectId and datetime
        json_encoders = {
            ObjectId: str,  # Serialize ObjectId as string
            datetime: lambda v: v.isoformat()  # Serialize datetime as ISO string
        }

    @validator("hashtags", pre=True)
    def split_hashtags(cls, v):
        if isinstance(v, str):
            return v.split()
        return v
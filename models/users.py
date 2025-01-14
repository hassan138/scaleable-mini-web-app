from bson import ObjectId
from typing import Optional
from pydantic import BaseModel, Field
from pydantic import validator


class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    hashed_password: str
    is_creator: bool
    is_admin:bool = False

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        orm = True

    @validator("id", pre=True, always=True)
    def validate_id(cls, value):
        if isinstance(value, ObjectId):
            return str(value)  # Convert ObjectId to string
        return value

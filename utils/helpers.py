from bson import ObjectId
from pydantic import BaseModel, validator, root_validator
from typing import Any, Optional

from pydantic.json_schema import JsonSchemaValue
# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate
#
#     @classmethod
#     def validate(cls, v: Any, field: Optional["ModelField"] = None):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return ObjectId(v)
#
#     @classmethod
#     def __get_pydantic_json_schema__(cls, field_schema):
#         field_schema.update(type="string")
#         return field_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> JsonSchemaValue:
        """
        Update the JSON schema to represent ObjectId as a string.
        """
        field_schema = handler(core_schema)
        field_schema.update(type="string", format="objectid")
        return field_schema

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: Any):
        """
        Return the core schema for validation.
        """
        from pydantic_core import core_schema
        return core_schema.str_schema()

# Helper Functions
def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "is_creator": user["is_creator"],
    }



# def serialize_video(video):
#     return {
#         "title": video["title"],
#         "description": video["description"],
#         "hashtags": video["hashtags"],
#         "filename": video.get("filename", "Unknown"),  # Use `.get` to avoid KeyError
#         "file_location": video["file_location"],
#         "creator_id": video["creator_id"],
#     }
def serialize_video(video):
    # Serialize video object, converting ObjectId and datetime properly
    return {
        "title": video["title"],
        "description": video["description"],
        "hashtags": video["hashtags"],
        "filename": video.get("filename", "Unknown"),  # Use `.get` to avoid KeyError
        "file_location": video["file_location"],
        "creator_id": str(video["creator_id"]),  # Convert ObjectId to string
        "upload_date": video["upload_date"].isoformat(),  # Convert datetime to ISO string
    }


def serialize_comment(comment):
    return {
        "id": str(comment["_id"]),
        "content": comment["content"],
        "video_id": str(comment["video_id"]),
        "user_id": str(comment["user_id"]),
        "timestamp": comment["timestamp"],
    }

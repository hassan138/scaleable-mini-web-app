from fastapi import APIRouter, HTTPException, Form
from bson import ObjectId
from typing import List
from datetime import datetime
from models.comments import Comment
from utils.helpers import serialize_comment
from config import db

# Router initialization
router = APIRouter()


# Routes

@router.post("/video/{video_id}/comment")
async def comment_on_video(
        video_id: str,
        content: str = Form(...),
        user_id: str = Form(...),
):
    # Ensure the video exists
    video = db.videos.find_one({"_id": ObjectId(video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Create a comment object
    comment = {
        "content": content,
        "video_id": ObjectId(video_id),
        "user_id": ObjectId(user_id),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Insert comment into the database
    result = db.comments.insert_one(comment)
    comment["_id"] = result.inserted_id

    # Return the serialized comment
    return serialize_comment(comment)


@router.get("/comments/video/{video_id}", response_model=List[Comment])
async def get_video_comments(video_id: str):
    # Find comments associated with the video
    comments = db.comments.find({"video_id": ObjectId(video_id)})

    # If no comments found, return empty list
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found for this video")

    # Return the serialized comments
    return [serialize_comment(comment) for comment in comments]


@router.get("/comments/{comment_id}")
async def get_comment(comment_id: str):
    # Find comment by its ID
    comment = db.comments.find_one({"_id": ObjectId(comment_id)})

    # If comment not found, raise an exception
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Return the serialized comment
    return serialize_comment(comment)


@router.put("/comments/{comment_id}")
async def update_comment(
        comment_id: str,
        content: str = Form(...)
):
    # Find comment by its ID
    comment = db.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Update the comment content
    db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": {"content": content, "timestamp": datetime.utcnow().isoformat()}}
    )

    # Return the updated comment
    updated_comment = db.comments.find_one({"_id": ObjectId(comment_id)})
    return serialize_comment(updated_comment)


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str):
    # Delete the comment by its ID
    result = db.comments.delete_one({"_id": ObjectId(comment_id)})

    # If no comment was deleted, raise an exception
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Return a success message
    return {"detail": "Comment deleted successfully"}

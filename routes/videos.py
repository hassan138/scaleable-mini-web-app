from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
import cloudinary
import cloudinary.uploader
from config import db
from utils.helpers import serialize_video, serialize_comment

# Cloudinary Configuration
cloudinary.config(
    cloud_name="dptixq5pl",
    api_key="531695646727655",
    api_secret="f7xfdft7c63RlYGG9nEtKUUl7dI",
    secure=False
)
# Router initialization
router = APIRouter()


# Dependency for role-based access
def is_creator(creator_id: str):
    creator = db.users.find_one({"_id": ObjectId(creator_id), "is_creator": True})
    if not creator:
        raise HTTPException(status_code=403, detail="Only creators can access this route")
    return creator


@router.post("/upload/video")
async def upload_video(
        title: str = Form(...),
        description: str = Form(...),
        hashtags: str = Form(...),
        file: UploadFile = Form(...),
        creator_id: str = Form(...),
):
    # Check if the creator exists and is valid
    creator = db.users.find_one({"_id": ObjectId(creator_id), "is_creator": True})
    if not creator:
        raise HTTPException(status_code=403, detail="Only creators can upload videos")

    # Upload the video to Cloudinary
    upload_result = cloudinary.uploader.upload_large(file.file, resource_type="video")
    video_url = upload_result.get("secure_url")

    # Prepare video metadata
    video = {
        "title": title,
        "description": description,
        "hashtags": hashtags.split(),
        "filename": file.filename,  # Ensure filename is included
        "url": video_url,
        "file_location": video_url,  # Ensure file_location is included
        "creator_id": ObjectId(creator_id),
        "upload_date": datetime.utcnow(),  # Use datetime object directly
    }

    # Insert video into the database
    result = db.videos.insert_one(video)
    video["_id"] = result.inserted_id  # Add the generated _id to the video

    # Return serialized video data
    return serialize_video(video)


@router.get("/videos")
async def list_videos(skip: int = 0, limit: int = 10):
    videos = db.videos.find().skip(skip).limit(limit)
    return [serialize_video(video) for video in videos]


@router.get("/videos/latest", response_model=List[dict])
async def get_latest_videos():
    videos = db.videos.find().sort("upload_date", -1)
    return [serialize_video(video) for video in videos]


@router.get("/video/{video_id}")
async def get_video(video_id: str):
    video = db.videos.find_one({"_id": ObjectId(video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return serialize_video(video)


@router.post("/video/{video_id}/comment")
async def comment_on_video(video_id: str, content: str = Form(...), user_id: str = Form(...)):
    video = db.videos.find_one({"_id": ObjectId(video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    comment = {
        "content": content,
        "video_id": ObjectId(video_id),
        "user_id": ObjectId(user_id),
        "timestamp": datetime.utcnow().isoformat(),
    }
    result = db.comments.insert_one(comment)
    comment["_id"] = result.inserted_id
    return {
        "id": str(comment["_id"]),
        "content": comment["content"],
        "timestamp": comment["timestamp"],
    }


@router.get("/videos/creator/{creator_id}")
async def get_creator_videos(creator_id: str):
    try:
        # Ensure the creator_id is valid
        if not ObjectId.is_valid(creator_id):
            raise HTTPException(status_code=400, detail="Invalid creator_id")

        # Use MongoDB aggregation to fetch videos and comment counts
        pipeline = [
            {"$match": {"creator_id": ObjectId(creator_id)}},  # Match videos by creator_id
            {
                "$lookup": {  # Join with the comments collection
                    "from": "comments",
                    "localField": "_id",  # Match video "_id" with "video_id" in comments
                    "foreignField": "video_id",
                    "as": "comments",
                }
            },
            {
                "$addFields": {  # Add a field for comment count
                    "comment_count": {"$size": "$comments"}
                }
            },
            {
                "$project": {  # Exclude the comments array from the output
                    "comments": 0
                }
            }
        ]

        videos = list(db.videos.aggregate(pipeline))

        # Serialize the response
        response = [serialize_video(video) for video in videos]
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/video/{video_id}")
async def update_video(
        video_id: str,
        title: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        hashtags: Optional[str] = Form(None),
):
    updates = {}
    if title:
        updates["title"] = title
    if description:
        updates["description"] = description
    if hashtags:
        updates["hashtags"] = hashtags

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    result = db.videos.update_one({"_id": ObjectId(video_id)}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")

    video = db.videos.find_one({"_id": ObjectId(video_id)})
    return serialize_video(video)


@router.delete("/video/{video_id}")
async def delete_video(video_id: str):
    result = db.videos.delete_one({"_id": ObjectId(video_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"detail": "Video deleted successfully"}


@router.get("/videos/consumer")
async def consumer_videos(skip: int = 0, limit: int = 10):
    """
    Route for consumers to view videos.
    """
    videos = db.videos.find().skip(skip).limit(limit)
    return [serialize_video(video) for video in videos]


@router.get("/dashboard/{creator_id}")
async def creator_dashboard(creator_id: str, creator=Depends(is_creator)):
    """
    Route for creators to view their uploaded videos and stats.
    """
    videos = db.videos.find({"creator_id": ObjectId(creator_id)})
    dashboard = []
    for video in videos:
        video_data = serialize_video(video)
        # Adding likes and comments count
        likes_count = db.likes.count_documents({"video_id": video["_id"]})
        comments_count = db.comments.count_documents({"video_id": video["_id"]})
        video_data.update({
            "likes": likes_count,
            "comments": comments_count,
        })
        dashboard.append(video_data)
    return dashboard


@router.post("/video/{video_id}/like")
async def like_video(video_id: str, user_id: str):
    """
    Like a video.
    """
    video = db.videos.find_one({"_id": ObjectId(video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    # Ensure user hasn't already liked the video
    existing_like = db.likes.find_one({"video_id": ObjectId(video_id), "user_id": ObjectId(user_id)})
    if existing_like:
        raise HTTPException(status_code=400, detail="Video already liked")

    like = {
        "video_id": ObjectId(video_id),
        "user_id": ObjectId(user_id),
        "timestamp": datetime.utcnow()
    }
    db.likes.insert_one(like)
    return {"detail": "Video liked"}


@router.get("/video/{video_id}/comments")
async def get_video_comments(video_id: str):
    """
    Get comments for a specific video.
    """
    video = db.videos.find_one({"_id": ObjectId(video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Fetch comments and serialize them before returning
    comments_cursor = db.comments.find({"video_id": ObjectId(video_id)})
    comments = [serialize_comment(comment) for comment in comments_cursor]

    return comments


@router.get("/videos/search")
async def search_videos(query: str, skip: int = 0, limit: int = 10):
    videos = db.videos.find({"$text": {"$search": query}}).skip(skip).limit(limit)
    return [serialize_video(video) for video in videos]

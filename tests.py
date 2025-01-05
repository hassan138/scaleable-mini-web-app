
from bson import ObjectId
from config import db

# Find all videos that do not have _id
videos_without_id = db.videos.find({"_id": {"$exists": False}})

# For each video, assign a new ObjectId
for video in videos_without_id:
    video["_id"] = ObjectId()  # Generate new ObjectId
    db.videos.save(video)  # Save the updated document back to the database
    print(f"Updated video with new _id: {video.get('title', 'Unknown')}")

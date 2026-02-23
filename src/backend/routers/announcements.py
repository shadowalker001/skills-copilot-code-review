from fastapi import APIRouter, Depends, HTTPException
from pymongo.collection import Collection
from datetime import datetime
from ..database import announcements_collection
from ..routers.auth import get_current_user

router = APIRouter()

@router.get("/announcements")
def get_announcements():
    now = datetime.now().isoformat()
    announcements = list(announcements_collection.find({"expiration_date": {"$gt": now}}))
    for a in announcements:
        a["_id"] = str(a["_id"])
    return announcements

@router.post("/announcements")
def add_announcement(announcement: dict, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    announcement["created_by"] = user["username"]
    if "expiration_date" not in announcement:
        raise HTTPException(status_code=400, detail="Expiration date required")
    if "start_date" not in announcement:
        announcement["start_date"] = datetime.now().isoformat()
    result = announcements_collection.insert_one(announcement)
    return {"_id": str(result.inserted_id)}

@router.put("/announcements/{announcement_id}")
def update_announcement(announcement_id: str, update: dict, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    result = announcements_collection.update_one({"_id": announcement_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"updated": True}

@router.delete("/announcements/{announcement_id}")
def delete_announcement(announcement_id: str, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"deleted": True}

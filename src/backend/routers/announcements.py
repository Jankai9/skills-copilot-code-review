"""
Announcement endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from ..database import announcements_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)

def announcement_serializer(ann):
    return {
        "id": str(ann.get("_id", "")),
        "title": ann.get("title", ""),
        "message": ann.get("message", ""),
        "start_date": ann.get("start_date"),
        "expiration_date": ann.get("expiration_date"),
        "created_by": ann.get("created_by", ""),
        "created_at": ann.get("created_at"),
        "last_modified": ann.get("last_modified"),
    }

@router.get("", response_model=List[dict])
@router.get("/", response_model=List[dict])
def get_announcements(
    active_only: Optional[bool] = False
) -> List[dict]:
    """
    Get all announcements, optionally only active (not expired)
    """
    now = datetime.now()
    query = {}
    if active_only:
        query["expiration_date"] = {"$gte": now}
        # Optionally filter by start_date
        query["$or"] = [
            {"start_date": {"$lte": now}},
            {"start_date": None},
            {"start_date": {"$exists": False}}
        ]
    anns = [announcement_serializer(a) for a in announcements_collection.find(query)]
    return anns

@router.post("/", response_model=dict)
def create_announcement(announcement: dict) -> dict:
    """
    Create a new announcement
    """
    announcement["created_at"] = datetime.now()
    announcement["last_modified"] = datetime.now()
    res = announcements_collection.insert_one(announcement)
    announcement["id"] = str(res.inserted_id)
    return announcement

@router.put("/{announcement_id}", response_model=dict)
def update_announcement(announcement_id: str, update: dict) -> dict:
    """
    Update an existing announcement
    """
    update["last_modified"] = datetime.now()
    result = announcements_collection.update_one({"_id": announcement_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    ann = announcements_collection.find_one({"_id": announcement_id})
    return announcement_serializer(ann)

@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str):
    """
    Delete an announcement
    """
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"success": True}

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .supabase_client import supabase

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

# ============================
# REQUEST MODELS
# ============================

class AddBookmarkRequest(BaseModel):
    user_id: str
    article: dict

class RemoveBookmarkRequest(BaseModel):
    user_id: str
    article_url: str


# ============================
# ADD BOOKMARK
# ============================

@router.post("/add")
async def add_bookmark(payload: AddBookmarkRequest):
    try:
        user_id = payload.user_id
        article = payload.article

        print("📌 ADD BOOKMARK:", user_id)

        article_url = article.get("url")
        if not article_url:
            raise HTTPException(status_code=400, detail="Missing article URL")

        # Prevent duplicate
        exists = (
            supabase.table("bookmarks")
            .select("*")
            .eq("user_id", user_id)
            .eq("article_url", article_url)
            .execute()
        )

        if exists.data:
            print("⚠ Already bookmarked")
            return {"success": True, "message": "Already bookmarked"}

        row = {
            "user_id": user_id,
            "article_url": article_url,
            "article": article,
        }

        print("➡ Saving article:", article_url)
        supabase.table("bookmarks").insert(row).execute()

        return {"success": True, "message": "Bookmark added"}

    except Exception as e:
        print("❌ ERROR add_bookmark:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================
# REMOVE BOOKMARK
# ============================

@router.delete("/remove")
async def remove_bookmark(payload: RemoveBookmarkRequest):
    try:
        print("🗑 REMOVE BOOKMARK:", payload)

        supabase.table("bookmarks") \
            .delete() \
            .eq("user_id", payload.user_id) \
            .eq("article_url", payload.article_url) \
            .execute()

        return {"success": True, "message": "Bookmark removed"}

    except Exception as e:
        print("❌ ERROR remove_bookmark:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================
# LIST BOOKMARKS
# ============================

@router.get("/{user_id}")
async def get_bookmarks(user_id: str):
    try:
        print("📌 Fetching bookmarks for:", user_id)

        res = (
            supabase.table("bookmarks")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        data = res.data or []

        print("📌 Found", len(data), "bookmarks")
        return data

    except Exception as e:
        print("❌ ERROR get_bookmarks:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

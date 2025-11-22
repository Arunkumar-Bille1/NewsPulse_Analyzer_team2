from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .supabase_client import supabase

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


# =====================================================
# 📌 REQUEST MODELS
# =====================================================

class AddBookmarkRequest(BaseModel):
    user_id: str
    article: dict


class RemoveBookmarkRequest(BaseModel):
    user_id: str
    article_url: str


class CheckBookmarkRequest(BaseModel):
    user_id: str
    article_url: str


# =====================================================
# ⭐ CHECK BOOKMARK (ONLY ONE! FIXED)
# =====================================================

@router.post("/check")
def check_bookmark(payload: CheckBookmarkRequest):
    try:
        result = (
            supabase.table("bookmarks")
            .select("id")
            .eq("user_id", payload.user_id)
            .eq("article_url", payload.article_url)
            .limit(1)    # IMPORTANT: Python client needs this
            .execute()
        )

        exists = len(result.data or []) > 0
        return {"exists": exists}

    except Exception as e:
        print("❌ ERROR check_bookmark:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ⭐ ADD BOOKMARK
# =====================================================

@router.post("/add")
async def add_bookmark(payload: AddBookmarkRequest):
    try:
        user_id = payload.user_id
        article = payload.article
        article_url = article.get("url")

        if not article_url:
            raise HTTPException(status_code=400, detail="Missing article URL")

        # Prevent duplicate
        exists = (
            supabase.table("bookmarks")
            .select("id")
            .eq("user_id", user_id)
            .eq("article_url", article_url)
            .execute()
        )

        if exists.data:
            return {"success": True, "message": "Already bookmarked"}

        # Insert bookmkark
        supabase.table("bookmarks").insert({
            "user_id": user_id,
            "article_url": article_url,
            "article": article,
        }).execute()

        return {"success": True, "message": "Bookmark added"}

    except Exception as e:
        print("❌ ERROR add_bookmark:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ⭐ REMOVE BOOKMARK
# =====================================================

@router.delete("/remove")
async def remove_bookmark(payload: RemoveBookmarkRequest):
    try:
        supabase.table("bookmarks") \
            .delete() \
            .eq("user_id", payload.user_id) \
            .eq("article_url", payload.article_url) \
            .execute()

        return {"success": True, "message": "Bookmark removed"}

    except Exception as e:
        print("❌ ERROR remove_bookmark:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ⭐ GET ALL BOOKMARKS FOR USER
# =====================================================

@router.get("/{user_id}")
async def get_bookmarks(user_id: str):
    try:
        res = (
            supabase.table("bookmarks")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return res.data or []

    except Exception as e:
        print("❌ ERROR get_bookmarks:", e)
        raise HTTPException(status_code=500, detail=str(e))

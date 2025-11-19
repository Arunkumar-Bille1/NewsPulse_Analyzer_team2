from fastapi import APIRouter
from .supabase_client import supabase
from .schemas import BookmarkCreate, CompareCreate
from datetime import datetime

router = APIRouter()

# -------------------------------
# ⭐ BOOKMARKS
# -------------------------------

@router.post("/bookmark/add")
def add_bookmark(data: BookmarkCreate):
    exists = supabase.table("bookmarks").select("*").eq("user_id", data.user_id)\
        .eq("article_id", data.article_id).execute()

    if exists.data:
        return {"message": "Already bookmarked"}

    supabase.table("bookmarks").insert({
        "user_id": data.user_id,
        "article_id": data.article_id,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return {"message": "Bookmark added"}

@router.get("/bookmark/list/{user_id}")
def list_bookmarks(user_id: str):
    res = supabase.table("bookmarks").select("*").eq("user_id", user_id).execute()
    return res.data

@router.delete("/bookmark/remove")
def remove_bookmark(data: BookmarkCreate):
    supabase.table("bookmarks")\
        .delete()\
        .eq("user_id", data.user_id)\
        .eq("article_id", data.article_id).execute()

    return {"message": "Bookmark removed"}


# -------------------------------
# ⭐ COMPARE ARTICLES
# -------------------------------

@router.post("/compare/add")
def add_compare(data: CompareCreate):
    res = supabase.table("compare_articles").select("*").eq("user_id", data.user_id).execute()

    if not res.data:
        supabase.table("compare_articles").insert({
            "user_id": data.user_id,
            "article_ids": [data.article_id],
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        return {"message": "Added to compare list"}

    compare = res.data[0]

    existing = compare["article_ids"]

    if data.article_id in existing:
        return {"message": "Already in compare list"}

    if len(existing) >= 3:
        return {"message": "You can compare maximum 3 articles"}

    existing.append(data.article_id)

    supabase.table("compare_articles").update({
        "article_ids": existing,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("user_id", data.user_id).execute()

    return {"message": "Updated compare list"}

@router.get("/compare/list/{user_id}")
def list_compare(user_id: str):
    res = supabase.table("compare_articles").select("*").eq("user_id", user_id).execute()

    if not res.data:
        return {"user_id": user_id, "article_ids": []}

    return res.data[0]

@router.delete("/compare/clear/{user_id}")
def clear_compare(user_id: str):
    supabase.table("compare_articles").delete().eq("user_id", user_id).execute()
    return {"message": "Compare list cleared"}

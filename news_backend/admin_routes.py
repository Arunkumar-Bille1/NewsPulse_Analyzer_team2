# news_backend/admin_routes.py
# news_backend/admin_routes.py
from fastapi import APIRouter, Depends, HTTPException
from news_backend.supabase_client import supabase
from news_backend.auth import require_admin, CurrentUser  # import from auth, not main

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
def list_users(_: CurrentUser = Depends(require_admin)):
    res = supabase.table("users").select("*").order("id", desc=True).execute()
    print("ADMIN /users:", getattr(res, "error", None), len(res.data or []))
    if hasattr(res, "error") and res.error:
        raise HTTPException(status_code=400, detail=str(res.error))
    rows = res.data or []
    # normalize fields expected by the UI
    out = []
    for r in rows:
        out.append({
            "id": r.get("id"),
            "name": r.get("name") or r.get("full_name") or "",
            "email": r.get("email") or "",
            "role": (r.get("role") or "user").lower(),
            "country": r.get("country") or r.get("location") or None,
        })
    return out

@router.get("/dashboard")
def dashboard(_: CurrentUser = Depends(require_admin)):
    res = supabase.table("users").select("id,role").execute()
    if hasattr(res, "error") and res.error:
        raise HTTPException(status_code=400, detail=str(res.error))
    rows = res.data or []
    total = len(rows)
    admins = sum(1 for r in rows if (r.get("role") or "").lower() == "admin")
    return {"total_users": total, "admin_users": admins, "regular_users": total - admins, "active_today": total}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, me: CurrentUser = Depends(require_admin)):
    if user_id == me.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    supabase.table("user_profiles").delete().eq("user_id", user_id).execute()
    supabase.table("users").delete().eq("id", user_id).execute()
    return {"ok": True}

# --------------------------------------------------------------------
# EXTRA: Admin analytics / system status endpoints
# --------------------------------------------------------------------
from datetime import datetime
import random

@router.get("/system_status")
def system_status(_: CurrentUser = Depends(require_admin)):
    """Simulated system monitoring metrics."""
    uptime = "98.5%"
    avg_response_time = "1.2s"
    daily_requests = 4200 + random.randint(-300, 300)
    return {
        "system_uptime": uptime,
        "avg_response_time": avg_response_time,
        "daily_requests": daily_requests,
        "status": "Online",
        "last_checked": datetime.utcnow().isoformat(),
    }

@router.get("/insights")
def advanced_insights(_: CurrentUser = Depends(require_admin)):
    """Advanced trend analysis metrics (placeholder until you connect real model)."""
    trend_spike = "AI Regulation mentions increased by 245% in the last 24 hours"
    correlations = {
        "Technology→Economy": round(random.uniform(0.8, 0.9), 2),
        "Environment→Policy": round(random.uniform(0.7, 0.8), 2),
        "Health→Technology": round(random.uniform(0.6, 0.7), 2),
    }
    chart_series = [
        {"day": d, "Technology": 100 + i * 10, "Environment": 90 + i * 8, "Economy": 95 + i * 6}
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ]
    return {
        "trend_spike": trend_spike,
        "correlations": correlations,
        "chart_series": chart_series,
        "last_update": datetime.utcnow().isoformat(),
    }

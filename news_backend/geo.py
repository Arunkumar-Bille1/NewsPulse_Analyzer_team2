# # geo.py
# from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
# from pydantic import BaseModel
# from typing import Optional, List, Dict, Any
# import logging
#
# from .geo_tagger import tag_article_with_location
# from .supabase_client import (
#     get_articles,
#     save_geo_tag,
#     get_geo_analytics,
#     fetch_articles_batch,
# )
#
# router = APIRouter(prefix="/geo", tags=["Geo"])
# logger = logging.getLogger("news_backend.geo")
# logger.setLevel(logging.INFO)
#
# class TagArticleRequest(BaseModel):
#     article: Dict[str, Any]
#
# class SaveGeoRequest(BaseModel):
#     article_url: str
#     country: str
#     state: Optional[str] = None
#     city: Optional[str] = None
#     lat: Optional[float] = None
#     lon: Optional[float] = None
#     location: Optional[str] = None
#
# class GeoFilterResponse(BaseModel):
#     count: int
#     articles: List[Dict[str, Any]]
#
# @router.post("/tag")
# def api_tag_article(payload: TagArticleRequest):
#     try:
#         article = payload.article
#         tagged = tag_article_with_location(article)
#         for k in ["lat", "lon", "location", "country", "state", "city"]:
#             tagged.setdefault(k, None)
#         return {"status": "success", "tagged": tagged}
#     except Exception as e:
#         logger.exception("Error in api_tag_article")
#         raise HTTPException(status_code=500, detail=str(e))
#
# @router.post("/save")
# def api_save_geo(payload: SaveGeoRequest):
#     try:
#         result = save_geo_tag(
#             payload.article_url,
#             payload.country or "",
#             payload.state or "",
#             payload.city or "",
#             payload.lat,
#             payload.lon,
#             payload.location,
#         )
#         return {"status": "success", "result": result}
#     except Exception as e:
#         logger.exception("Error in api_save_geo")
#         raise HTTPException(status_code=500, detail=str(e))
#
# @router.get("/news", response_model=GeoFilterResponse)
# def api_get_news_by_geo(
#     country: Optional[str] = Query(None),
#     state: Optional[str] = Query(None),
#     city: Optional[str] = Query(None),
#     limit: int = Query(500, ge=1, le=5000),
# ):
#     try:
#         articles = get_articles(country=country, state=state, city=city) or []
#         if limit:
#             articles = articles[:limit]
#         return {"count": len(articles), "articles": articles}
#     except Exception as e:
#         logger.exception("Error in api_get_news_by_geo")
#         raise HTTPException(status_code=500, detail=str(e))
#
# @router.get("/analytics")
# def api_geo_analytics(limit_countries: int = Query(200, ge=1)):
#     try:
#         raw = get_geo_analytics()
#         if isinstance(raw, dict):
#             top = []
#             for country, info in raw.items():
#                 if isinstance(info, dict):
#                     cnt = info.get("count", 0)
#                     locs = info.get("locations", [])
#                 else:
#                     cnt = int(info) if isinstance(info, (int, str)) else 0
#                     locs = []
#                 top.append({"country": country, "count": cnt, "locations": locs})
#             top_sorted = sorted(top, key=lambda x: x["count"], reverse=True)[:limit_countries]
#             total = sum(x["count"] for x in top_sorted)
#             return {"top_countries": top_sorted, "total": total}
#         if isinstance(raw, list):
#             total = sum(item.get("count", 0) for item in raw)
#             top_sorted = sorted(raw, key=lambda x: x.get("count", 0), reverse=True)[:limit_countries]
#             return {"top_countries": top_sorted, "total": total}
#         return {"data": raw}
#     except Exception as e:
#         logger.exception("Error in api_geo_analytics")
#         raise HTTPException(status_code=500, detail=str(e))
#
# class BatchTagRequest(BaseModel):
#     batch_size: int = 200
#     dry_run: bool = True
#     start_offset: int = 0
#
# def _process_batch(offset: int, batch_size: int, dry_run: bool):
#     try:
#         rows = fetch_articles_batch(offset=offset, limit=batch_size)
#         processed = 0
#         for a in rows:
#             tagged = tag_article_with_location(a)
#             if not dry_run:
#                 try:
#                     save_geo_tag(
#                         a.get("url") or a.get("article_url") or "",
#                         tagged.get("country") or "",
#                         tagged.get("state") or "",
#                         tagged.get("city") or "",
#                         tagged.get("lat"),
#                         tagged.get("lon"),
#                         tagged.get("location"),
#                     )
#                 except Exception as ee:
#                     logger.warning("Failed to save geo tag for %s: %s", a.get("url"), str(ee))
#             processed += 1
#         logger.info("Batch processed offset=%s size=%s dry_run=%s processed=%s", offset, batch_size, dry_run, processed)
#         return {"processed": processed}
#     except Exception as e:
#         logger.exception("Error in _process_batch_and_save")
#         return {"error": str(e)}
#
# @router.post("/batch-tag")
# def api_batch_tag(payload: BatchTagRequest, background_tasks: BackgroundTasks):
#     try:
#         offset = payload.start_offset or 0
#         batch_size = payload.batch_size or 200
#         dry_run = payload.dry_run if payload.dry_run is not None else True
#         background_tasks.add_task(_process_batch, offset, batch_size, dry_run)
#         return {"status": "started", "offset": offset, "batch_size": batch_size, "dry_run": dry_run}
#     except Exception as e:
#         logger.exception("Error in api_batch_tag")
#         raise HTTPException(status_code=500, detail=str(e))
#
# @router.get("/health")
# def api_health():
#     return {"geo_tagger": True}






from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta

from .geo_tagger import tag_article_with_location
from .supabase_client import (
    get_articles,
    save_geo_tag,
    get_geo_analytics,
    fetch_articles_batch,
    supabase,  # export supabase in supabase_client.py
)

router = APIRouter(tags=["Geo"])
logger = logging.getLogger("news_backend.geo")
logger.setLevel(logging.INFO)


class TagArticleRequest(BaseModel):
    article: Dict[str, Any]


class SaveGeoRequest(BaseModel):
    article_url: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    location: Optional[str] = None


class GeoFilterResponse(BaseModel):
    count: int
    articles: List[Dict[str, Any]]


@router.post("/tag")
def api_tag_article(payload: TagArticleRequest):
    try:
        article = payload.article
        tagged = tag_article_with_location(article)
        for k in ["lat", "lon", "location", "country", "state", "city"]:
            tagged.setdefault(k, None)
        return {"status": "success", "tagged": tagged}
    except Exception as e:
        logger.exception("Error in api_tag_article")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
def api_save_geo(payload: SaveGeoRequest):
    try:
        result = save_geo_tag(
            payload.article_url,
            payload.country or "",
            payload.state or "",
            payload.city or "",
            payload.lat,
            payload.lon,
            payload.location,
        )
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("Error in api_save_geo")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news", response_model=GeoFilterResponse)
def api_get_news_by_geo(
    country: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
):
    try:
        articles = get_articles(country=country, state=state, city=city) or []
        if limit:
            articles = articles[:limit]
        return {"count": len(articles), "articles": articles}
    except Exception as e:
        logger.exception("Error in api_get_news_by_geo")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
def api_geo_analytics(limit_countries: int = Query(200, ge=1)):
    try:
        raw = get_geo_analytics()
        if isinstance(raw, dict):
            top = []
            for country, info in raw.items():
                if isinstance(info, dict):
                    cnt = info.get("count", 0)
                    locs = info.get("locations", [])
                else:
                    cnt = int(info) if isinstance(info, (int, str)) else 0
                    locs = []
                top.append({"country": country, "count": cnt, "locations": locs})
            top_sorted = sorted(top, key=lambda x: x["count"], reverse=True)[
                :limit_countries
            ]
            total = sum(x["count"] for x in top_sorted)
            return {"top_countries": top_sorted, "total": total}
        if isinstance(raw, list):
            total = sum(item.get("count", 0) for item in raw)
            top_sorted = sorted(
                raw, key=lambda x: x.get("count", 0), reverse=True
            )[:limit_countries]
            return {"top_countries": top_sorted, "total": total}
        return {"data": raw}
    except Exception as e:
        logger.exception("Error in api_geo_analytics")
        raise HTTPException(status_code=500, detail=str(e))


class BatchTagRequest(BaseModel):
    batch_size: int = 200
    dry_run: bool = True
    start_offset: int = 0


def _process_batch(offset: int, batch_size: int, dry_run: bool):
    try:
        rows = fetch_articles_batch(offset=offset, limit=batch_size)
        processed = 0
        for a in rows:
            tagged = tag_article_with_location(a)
            if not dry_run:
                try:
                    save_geo_tag(
                        a.get("url") or a.get("article_url") or "",
                        tagged.get("country") or "",
                        tagged.get("state") or "",
                        tagged.get("city") or "",
                        tagged.get("lat"),
                        tagged.get("lon"),
                        tagged.get("location"),
                    )
                except Exception as ee:
                    logger.warning(
                        "Failed to save geo tag for %s: %s", a.get("url"), str(ee)
                    )
            processed += 1
        logger.info(
            "Batch processed offset=%s size=%s dry_run=%s processed=%s",
            offset,
            batch_size,
            dry_run,
            processed,
        )
        return {"processed": processed}
    except Exception as e:
        logger.exception("Error in _process_batch_and_save")
        return {"error": str(e)}


@router.post("/batch-tag")
def api_batch_tag(payload: BatchTagRequest, background_tasks: BackgroundTasks):
    try:
        offset = payload.start_offset or 0
        batch_size = payload.batch_size or 200
        dry_run = payload.dry_run if payload.dry_run is not None else True
        background_tasks.add_task(_process_batch, offset, batch_size, dry_run)
        return {
            "status": "started",
            "offset": offset,
            "batch_size": batch_size,
            "dry_run": dry_run,
        }
    except Exception as e:
        logger.exception("Error in api_batch_tag")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def api_health():
    return {"geo_tagger": True}


class GeoPoint(BaseModel):
    lat: float
    lon: float
    weight: int = 1
    country: Optional[str] = None
    location: Optional[str] = None
    published_at: Optional[str] = None


@router.get("/heat", response_model=List[GeoPoint])
def geo_heat(
    days: int = Query(7, ge=1, le=90),
    topic: Optional[str] = Query(None, description="Optional topic/keyword filter"),
    limit: int = Query(5000, ge=1, le=20000),
):
    """
    Minimal payload for heatmap: just lat/lon (+ optional metadata).
    Reads from Supabase 'articles' table where lat & lon are not null.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)

        query = (
            supabase.table("articles")
            .select("lat, lon, country, location, published_at, keywords")
            .not_.is_("lat", None)
            .not_.is_("lon", None)
            .gte("published_at", cutoff.isoformat())
            .order("published_at", desc=True)
            .limit(limit)
        )

        rows = query.execute().data or []

        points: List[Dict[str, Any]] = []

        for r in rows:
            if topic:
                kws = r.get("keywords") or []
                if isinstance(kws, list):
                    if topic.lower() not in [str(k).lower() for k in kws]:
                        continue

            lat = r.get("lat")
            lon = r.get("lon")
            if lat is None or lon is None:
                continue

            points.append(
                {
                    "lat": float(lat),
                    "lon": float(lon),
                    "weight": 1,
                    "country": r.get("country"),
                    "location": r.get("location"),
                    "published_at": r.get("published_at"),
                }
            )

        return points
    except Exception as e:
        logger.exception("Error in /geo/heat")
        raise HTTPException(status_code=500, detail=str(e))

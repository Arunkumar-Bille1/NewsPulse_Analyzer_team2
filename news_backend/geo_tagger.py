# # geo_tagger.py
# # ---------------------------------------
# # GEO-TAGGER v2 — Ensemble spaCy + HF NER + regex fallback
# # Caching + safe OpenCage usage + candidate filtering
# # ---------------------------------------
#
# import os
# import re
# import time
# import logging
# from typing import List, Optional, Dict, Any
#
# import spacy
# from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
# from opencage.geocoder import OpenCageGeocode
# from requests.exceptions import RequestException
#
# logger = logging.getLogger("geo_tagger")
# logger.setLevel(logging.INFO)
#
# OPENCAGE_API_KEY = os.environ.get("OPENCAGE_API_KEY", "c19df82d29024dc38b3bc91e6e426820")
# _GEOCODE_RETRY = 2
# _GEOCODE_RETRY_BACKOFF = 0.8
# _GEOCODE_CACHE_TTL = 60 * 60 * 24
# _MAX_GEOCODE_CANDIDATES = 3
# _MIN_LOCATION_LENGTH = 2
# _MAX_LOCATION_LENGTH = 80
#
# geocoder = OpenCageGeocode(OPENCAGE_API_KEY)
#
# # Load spaCy
# try:
#     nlp = spacy.load("en_core_web_trf")
#     logger.info("Loaded en_core_web_trf")
# except Exception:
#     nlp = spacy.load("en_core_web_sm")
#     logger.info("Loaded en_core_web_sm (fallback)")
#
# # Load HF NER
# HF_MODEL_NAME = "dslim/bert-base-NER"
# try:
#     tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
#     hf_model = AutoModelForTokenClassification.from_pretrained(HF_MODEL_NAME)
#     hf_ner = pipeline("ner", model=hf_model, tokenizer=tokenizer, aggregation_strategy="simple")
#     logger.info("Loaded HF NER")
# except Exception:
#     hf_ner = None
#     logger.exception("Failed to load HF NER — continuing with spaCy only")
#
# # Simple in-memory cache
# _geocode_cache: Dict[str, Any] = {}
#
# def _cache_get(key: str):
#     entry = _geocode_cache.get(key)
#     if not entry:
#         return None
#     ts, val = entry
#     if (time.time() - ts) > _GEOCODE_CACHE_TTL:
#         _geocode_cache.pop(key, None)
#         return None
#     return val
#
# def _cache_set(key: str, value: Any):
#     _geocode_cache[key] = (time.time(), value)
#
# # Clean text
# def clean_text(text: Optional[str]) -> str:
#     if not text:
#         return ""
#     txt = re.sub(r"http\S+", " ", text)
#     txt = re.sub(r"<[^>]+>", " ", txt)
#     txt = re.sub(r"[^A-Za-z0-9À-ÖØ-öø-ÿ ,\.\-']", " ", txt)
#     txt = re.sub(r"\s+", " ", txt).strip()
#     return txt
#
# # spaCy extraction
# def spacy_locations(text: str) -> List[str]:
#     try:
#         doc = nlp(text)
#         labels = {"GPE", "LOC", "FAC", "ORG"}
#         return [ent.text for ent in doc.ents if ent.label_ in labels]
#     except Exception:
#         return []
#
# # HF extraction
# def hf_locations(text: str) -> List[str]:
#     if not hf_ner:
#         return []
#     try:
#         results = hf_ner(text)
#         locs = []
#         for ent in results:
#             group = ent.get("entity_group", "").upper()
#             word = ent.get("word") or ""
#             if group in {"LOC", "GPE", "MISC", "ORG"}:
#                 word = word.strip()
#                 if _MIN_LOCATION_LENGTH <= len(word) <= _MAX_LOCATION_LENGTH:
#                     word = re.sub(r"^[\"'`]+|[\"'`]+$", "", word)
#                     locs.append(word)
#         return locs
#     except Exception:
#         logger.exception("hf_locations failed")
#         return []
#
# # regex fallback
# _REGEX_PREP = re.compile(
#     r"\b(?:in|near|at|from|around|off|on|within|outside)\s+([A-Z][A-Za-z0-9\-\.\' ]{1,60})",
#     flags=re.IGNORECASE,
# )
# def regex_locations(text: str) -> List[str]:
#     matches = _REGEX_PREP.findall(text)
#     cleaned = []
#     for m in matches:
#         m = m.strip().rstrip(".,;:")
#         if _MIN_LOCATION_LENGTH <= len(m) <= _MAX_LOCATION_LENGTH:
#             cleaned.append(m)
#     return cleaned
#
# def merge_candidates(text: str) -> List[str]:
#     s1 = spacy_locations(text)
#     s2 = hf_locations(text)
#     s3 = regex_locations(text)
#     all_cands = s1 + s2 + s3
#     normalized = []
#     for c in all_cands:
#         if not c:
#             continue
#         c = c.replace("\n", " ").strip()
#         c = re.sub(r"\s+", " ", c)
#         c = c.replace(" - ", " ").strip()
#         if _MIN_LOCATION_LENGTH <= len(c) <= _MAX_LOCATION_LENGTH:
#             normalized.append(c)
#     final = []
#     for c in normalized:
#         if c not in final:
#             final.append(c)
#     return final
#
# _BAD_WORDS = {
#     "news", "minister", "police", "office", "agency", "court", "bank",
#     "report", "team", "desk", "sources", "service", "author", "writer",
#     "journal", "press"
# }
# def is_valid_location_candidate(loc: str) -> bool:
#     low = loc.lower()
#     for bad in _BAD_WORDS:
#         if bad in low:
#             return False
#     if len(loc.split()) > 5:
#         return False
#     name_prefixes = {"mr", "mrs", "dr", "prof"}
#     if any(low.startswith(p + " ") for p in name_prefixes):
#         return False
#     if not (_MIN_LOCATION_LENGTH <= len(loc) <= _MAX_LOCATION_LENGTH):
#         return False
#     return True
#
# def geocode(place: str) -> Optional[Dict[str, Any]]:
#     if not place or not place.strip():
#         return None
#     key = place.strip().lower()
#     cached = _cache_get(key)
#     if cached is not None:
#         return cached
#     attempt = 0
#     while attempt <= _GEOCODE_RETRY:
#         try:
#             res = geocoder.geocode(place, no_annotations=1, limit=1)
#             if res:
#                 d = res[0]
#                 out = {
#                     "input": place,
#                     "location": d.get("formatted"),
#                     "lat": d["geometry"]["lat"],
#                     "lon": d["geometry"]["lng"],
#                     "components": d.get("components", {}),
#                     "country": d.get("components", {}).get("country"),
#                     "state": d.get("components", {}).get("state") or d.get("components", {}).get("region"),
#                     "city": d.get("components", {}).get("city") or d.get("components", {}).get("town") or d.get("components", {}).get("village") or d.get("components", {}).get("county"),
#                     "raw": d,
#                 }
#                 _cache_set(key, out)
#                 return out
#             else:
#                 _cache_set(key, None)
#                 return None
#         except RequestException as rexc:
#             logger.warning("Geocode request exception for '%s': %s", place, str(rexc))
#             attempt += 1
#             time.sleep(_GEOCODE_RETRY_BACKOFF * attempt)
#         except Exception:
#             logger.exception("Unexpected geocode error for '%s'", place)
#             attempt += 1
#             time.sleep(_GEOCODE_RETRY_BACKOFF * attempt)
#     _cache_set(key, None)
#     return None
#
# def tag_article_with_location(article: Dict[str, Any]) -> Dict[str, Any]:
#     pieces = []
#     if isinstance(article, dict):
#         pieces.append(article.get("title", "") or "")
#         pieces.append(article.get("description", "") or "")
#         pieces.append(article.get("content", "") or article.get("full_text", "") or "")
#         pieces.append(article.get("source", "") or article.get("source_name", "") or "")
#     full_text = clean_text(" ".join(pieces))
#     candidates = merge_candidates(full_text)
#     candidates = [c for c in candidates if is_valid_location_candidate(c)]
#     if not candidates:
#         article["location"] = None
#         article["lat"] = None
#         article["lon"] = None
#         article["country"] = None
#         article["state"] = None
#         article["city"] = None
#         return article
#     candidates = candidates[:_MAX_GEOCODE_CANDIDATES]
#     for cand in candidates:
#         try:
#             geo = geocode(cand)
#             if geo and geo.get("country"):
#                 article["location"] = geo.get("location") or cand
#                 article["lat"] = geo.get("lat")
#                 article["lon"] = geo.get("lon")
#                 article["country"] = geo.get("country")
#                 article["state"] = geo.get("state")
#                 article["city"] = geo.get("city")
#                 return article
#         except Exception:
#             logger.exception("Error geocoding candidate '%s'", cand)
#             continue
#     source_country_hint = article.get("source_country") or article.get("country_hint") or None
#     if source_country_hint:
#         for cand in candidates:
#             try:
#                 query = f"{cand}, {source_country_hint}"
#                 geo = geocode(query)
#                 if geo and geo.get("country"):
#                     article["location"] = geo.get("location") or cand
#                     article["lat"] = geo.get("lat")
#                     article["lon"] = geo.get("lon")
#                     article["country"] = geo.get("country")
#                     article["state"] = geo.get("state")
#                     article["city"] = geo.get("city")
#                     return article
#             except Exception:
#                 logger.exception("Error geocoding candidate with hint '%s'", cand)
#                 continue
#     article["location"] = None
#     article["lat"] = None
#     article["lon"] = None
#     article["country"] = None
#     article["state"] = None
#     article["city"] = None
#     return article
#
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     sample = {
#         "title": "Floods hit parts of Assam and Guwahati",
#         "description": "Local officials in Guwahati said the Brahmaputra river overflowed after heavy rains.",
#         "content": "The worst affected areas were in and around Guwahati and Kamrup district. Rescue teams from Assam Police and NDRF were deployed.",
#         "source": "example-news"
#     }
#     tagged = tag_article_with_location(sample)
#     print("Tagged result:", tagged)



# geo_tagger.py — GDELT-aware, high-coverage geotagger

import os
import re
import time
import logging
from typing import List, Optional, Dict, Any

import spacy
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from opencage.geocoder import OpenCageGeocode
from requests.exceptions import RequestException

logger = logging.getLogger("geo_tagger")
logger.setLevel(logging.INFO)

OPENCAGE_API_KEY = os.environ.get("OPENCAGE_API_KEY", "c19df82d29024dc38b3bc91e6e426820")

_GEOCODE_RETRY = 2
_GEOCODE_RETRY_BACKOFF = 0.8
_GEOCODE_CACHE_TTL = 60 * 60 * 24
_MAX_GEOCODE_CANDIDATES = 5
_MIN_LOCATION_LENGTH = 2
_MAX_LOCATION_LENGTH = 80

geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

# -------------------- MODELS -------------------- #

try:
    nlp = spacy.load("en_core_web_trf")
    logger.info("Loaded en_core_web_trf")
except Exception:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Loaded en_core_web_sm (fallback)")

HF_MODEL_NAME = "dslim/bert-base-NER"
try:
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
    hf_model = AutoModelForTokenClassification.from_pretrained(HF_MODEL_NAME)
    hf_ner = pipeline(
        "ner",
        model=hf_model,
        tokenizer=tokenizer,
        aggregation_strategy="simple",
    )
    logger.info("Loaded HF NER")
except Exception:
    hf_ner = None
    logger.exception("Failed to load HF NER — continuing with spaCy only")

# -------------------- CACHE -------------------- #

_geocode_cache: Dict[str, Any] = {}


def _cache_get(key: str):
    entry = _geocode_cache.get(key)
    if not entry:
        return None
    ts, val = entry
    if (time.time() - ts) > _GEOCODE_CACHE_TTL:
        _geocode_cache.pop(key, None)
        return None
    return val


def _cache_set(key: str, value: Any):
    _geocode_cache[key] = (time.time(), value)


# -------------------- CLEANING -------------------- #

def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    txt = re.sub(r"http\S+", " ", text)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"[^A-Za-z0-9À-ÖØ-öø-ÿ ,\.\-']", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


# -------------------- CANDIDATE EXTRACTION -------------------- #

def spacy_locations(text: str) -> List[str]:
    try:
        doc = nlp(text)
        labels = {"GPE", "LOC", "FAC", "ORG"}
        return [ent.text for ent in doc.ents if ent.label_ in labels]
    except Exception:
        return []


def hf_locations(text: str) -> List[str]:
    if not hf_ner:
        return []
    try:
        results = hf_ner(text)
        locs: List[str] = []
        for ent in results:
            group = ent.get("entity_group", "").upper()
            word = ent.get("word") or ""
            if group in {"LOC", "GPE", "MISC", "ORG"}:
                word = word.strip()
                if _MIN_LOCATION_LENGTH <= len(word) <= _MAX_LOCATION_LENGTH:
                    word = re.sub(r'^[\"\'`]+|[\"\'`]+$', "", word)
                    locs.append(word)
        return locs
    except Exception:
        logger.exception("hf_locations failed")
        return []


_REGEX_PREP = re.compile(
    r"\b(?:in|near|at|from|around|off|on|within|outside)\s+([A-Z][A-Za-z0-9\-\.\' ]{1,60})",
    flags=re.IGNORECASE,
)


def regex_locations(text: str) -> List[str]:
    matches = _REGEX_PREP.findall(text)
    cleaned: List[str] = []
    for m in matches:
        m = m.strip().rstrip(".,;:")
        if _MIN_LOCATION_LENGTH <= len(m) <= _MAX_LOCATION_LENGTH:
            cleaned.append(m)
    return cleaned


def merge_candidates(text: str) -> List[str]:
    s1 = spacy_locations(text)
    s2 = hf_locations(text)
    s3 = regex_locations(text)

    all_cands = s1 + s2 + s3
    normalized: List[str] = []
    for c in all_cands:
        if not c:
            continue
        c = c.replace("\n", " ").strip()
        c = re.sub(r"\s+", " ", c)
        c = c.replace(" - ", " ").strip()
        if _MIN_LOCATION_LENGTH <= len(c) <= _MAX_LOCATION_LENGTH:
            normalized.append(c)

    final: List[str] = []
    for c in normalized:
        if c not in final:
            final.append(c)
    return final


_BAD_WORDS = {
    "news", "minister", "police", "office", "agency", "court", "bank",
    "report", "team", "desk", "sources", "service", "author", "writer",
    "journal", "press",
}


def is_valid_location_candidate(loc: str) -> bool:
    low = loc.lower()
    for bad in _BAD_WORDS:
        if bad in low:
            return False
    if len(loc.split()) > 5:
        return False
    name_prefixes = {"mr", "mrs", "dr", "prof"}
    if any(low.startswith(p + " ") for p in name_prefixes):
        return False
    if not (_MIN_LOCATION_LENGTH <= len(loc) <= _MAX_LOCATION_LENGTH):
        return False
    return True


# -------------------- GEOCODING HELPERS -------------------- #

def _geocode_raw(query: str) -> Optional[Dict[str, Any]]:
    if not query or not query.strip():
        return None

    key = f"fwd::{query.strip().lower()}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    attempt = 0
    while attempt <= _GEOCODE_RETRY:
        try:
            res = geocoder.geocode(query, no_annotations=1, limit=1)
            if res:
                d = res[0]
                out = {
                    "input": query,
                    "location": d.get("formatted"),
                    "lat": d["geometry"]["lat"],
                    "lon": d["geometry"]["lng"],
                    "components": d.get("components", {}),
                    "country": d.get("components", {}).get("country"),
                    "state": d.get("components", {}).get("state")
                        or d.get("components", {}).get("region"),
                    "city": d.get("components", {}).get("city")
                        or d.get("components", {}).get("town")
                        or d.get("components", {}).get("village")
                        or d.get("components", {}).get("county"),
                    "raw": d,
                }
                _cache_set(key, out)
                return out
            else:
                _cache_set(key, None)
                return None
        except RequestException as rexc:
            logger.warning("Geocode request exception for '%s': %s", query, str(rexc))
            attempt += 1
            time.sleep(_GEOCODE_RETRY_BACKOFF * attempt)
        except Exception:
            logger.exception("Unexpected geocode error for '%s'", query)
            attempt += 1
            time.sleep(_GEOCODE_RETRY_BACKOFF * attempt)

    _cache_set(key, None)
    return None


def _reverse_geocode(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    key = f"rev::{round(lat, 4)},{round(lon, 4)}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    attempt = 0
    while attempt <= _GEOCODE_RETRY:
        try:
            res = geocoder.reverse_geocode(lat, lon, no_annotations=1, limit=1)
            if res:
                d = res[0]
                out = {
                    "lat": lat,
                    "lon": lon,
                    "location": d.get("formatted"),
                    "country": d.get("components", {}).get("country"),
                    "state": d.get("components", {}).get("state")
                        or d.get("components", {}).get("region"),
                    "city": d.get("components", {}).get("city")
                        or d.get("components", {}).get("town")
                        or d.get("components", {}).get("village")
                        or d.get("components", {}).get("county"),
                    "components": d.get("components", {}),
                    "raw": d,
                }
                _cache_set(key, out)
                return out
            else:
                _cache_set(key, None)
                return None
        except RequestException as rexc:
            logger.warning("Reverse geocode exception for %s,%s: %s", lat, lon, str(rexc))
            attempt += 1
            time.sleep(_GEOCODE_RETRY_BACKOFF * attempt)
        except Exception:
            logger.exception("Unexpected reverse geocode error")
            attempt += 1
            time.sleep(_GEOCODE_RETRY_BACKOFF * attempt)

    _cache_set(key, None)
    return None


def geocode_best(patterns: List[str]) -> Optional[Dict[str, Any]]:
    for q in patterns:
        if not q:
            continue
        geo = _geocode_raw(q)
        if geo and geo.get("lat") is not None and geo.get("lon") is not None:
            if geo.get("country"):
                return geo
    return None


def geocode_country_centroid(country_name: str) -> Optional[Dict[str, Any]]:
    if not country_name:
        return None
    return geocode_best([country_name])


# -------------------- WRITE BACK -------------------- #

def _set_article_location(article: Dict[str, Any], geo: Optional[Dict[str, Any]], fallback_label: Optional[str] = None):
    if geo:
        article["location"] = geo.get("location") or fallback_label
        article["lat"] = geo.get("lat")
        article["lon"] = geo.get("lon")
        article["country"] = geo.get("country")
        article["state"] = geo.get("state")
        article["city"] = geo.get("city")
    else:
        article.setdefault("location", fallback_label)
        article.setdefault("lat", None)
        article.setdefault("lon", None)
        article.setdefault("country", None)
        article.setdefault("state", None)
        article.setdefault("city", None)
    return article


# -------------------- MAIN ENTRY -------------------- #

# -------------------- MAIN ENTRY -------------------- #

def tag_article_with_location(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Priority:
    1) If article already has lat/lon (e.g. from GDELT) -> reverse geocode to normalize.
    2) Else run NER + geocode on extracted city/state.
    3) Else fall back to source_country / country_hint centroid.
    """

    # 1) Respect existing coordinates (from GDELT or other feeds)
    try:
        lat = article.get("lat")
        lon = article.get("lon")
        if lat is not None and lon is not None:
            rev = _reverse_geocode(float(lat), float(lon))
            if rev:
                return _set_article_location(
                    article,
                    rev,
                    fallback_label=article.get("location"),
                )
    except Exception:
        logger.exception("Reverse geocode failed, will fall back to NER pipeline")

    # 2) Extract location from text
    pieces: List[str] = []
    if isinstance(article, dict):
        pieces.append(article.get("title", "") or "")
        pieces.append(article.get("description", "") or "")
        pieces.append(article.get("content", "") or article.get("full_text", "") or "")

        # SAFE source -> string
        src = article.get("source") or article.get("source_name") or ""
        if isinstance(src, dict):
            # typical NewsAPI shape: {"id": "...", "name": "..."}
            src = src.get("name") or src.get("id") or ""
        elif not isinstance(src, str):
            src = str(src or "")

        pieces.append(src)

    full_text = clean_text(" ".join(pieces))

    candidates = merge_candidates(full_text)
    candidates = [c for c in candidates if is_valid_location_candidate(c)]

    source_country_hint = article.get("source_country") or article.get("country_hint")

    if candidates:
        candidates = candidates[:_MAX_GEOCODE_CANDIDATES]
        for cand in candidates:
            patterns = [cand]
            if source_country_hint:
                patterns.append(f"{cand}, {source_country_hint}")
            geo = geocode_best(patterns)
            if geo and geo.get("country"):
                return _set_article_location(article, geo, fallback_label=cand)

    # 3) Fall back to country-level centroid
    if source_country_hint:
        geo_country = geocode_country_centroid(source_country_hint)
        if geo_country:
            label = geo_country.get("country") or source_country_hint
            return _set_article_location(article, geo_country, fallback_label=label)

    # 4) No clue at all
    return _set_article_location(article, None, fallback_label=None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sample = {
        "title": "Floods hit parts of Assam and Guwahati",
        "description": "Local officials in Guwahati said the Brahmaputra river overflowed.",
        "source": "example-news",
        "source_country": "India",
    }
    tagged = tag_article_with_location(sample)
    print("Tagged:", tagged)
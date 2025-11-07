import os
import praw
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datetime import datetime
from news_backend.models import NewsBase
from pathlib import Path
from typing import List, Dict


# Load .env file
env_path = Path(__file__).resolve().parent / ".env"
print(f"Looking for .env at: {env_path}")
load_dotenv(env_path)

#NEWS_API_KEY = fd6b4247f1054b2e8b2f3c1eed92ee45
#GNEWS_KEY =f74752ad4603941d97396533741a563d
#REDDIT_CLIENT_ID ="up9mA01v608o84gLtvMhYA" 
#REDDIT_CLIENT_SECRET = "0z_wuVPMlo3o5_Si7IoxmRWOhF7iaA" # pyright: ignore[reportUndefinedVariable]
# Get API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY","226b77d5fd..........your api key.........6bfdc")
GNEWS_KEY = os.getenv("GNEWS_KEY","50c4a52........your api keyu.......5918d3c")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID","jqealzF.....your key...SA0rg")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET","ulPlCNFW.....your api key........iwmw")


print(f"Loaded NEWS_API_KEY: {NEWS_API_KEY[:6] + '...' if NEWS_API_KEY else 'None'}")
print(f"Loaded GNEWS_KEY: {GNEWS_KEY[:6] + '...' if GNEWS_KEY else 'None'}")
print(f"Loaded REDDIT_CLIENT_ID: {REDDIT_CLIENT_ID[:6] + '...' if REDDIT_CLIENT_ID else 'None'}")



def fetch_newsapi(query="technology"):
    print(f"Fetching from NewsAPI with key: {bool(NEWS_API_KEY)} | Query: {query}")

    if not NEWS_API_KEY:
        print("Missing NEWS_API_KEY")
        return []

    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={NEWS_API_KEY}"
    r = requests.get(url)
    print("Response status (NewsAPI):", r.status_code)

    if r.status_code != 200:
        print("NewsAPI request failed:", r.text)
        return []

    data = r.json()
    if data.get("status") != "ok":
        print("NewsAPI returned error:", data)
        return []

    articles = [
        {
            "title": a.get("title"),
            "description": a.get("description"),
            "url": a.get("url"),
            "image": a.get("urlToImage"),
            "publishedAt": a.get("publishedAt"),
            "source": {"name": a.get("source", {}).get("name", "NewsAPI")},
        }
        for a in data.get("articles", [])
        if a.get("title") and a.get("url")
    ]
    print(f"NewsAPI returned {len(articles)} articles.")
    return articles



def fetch_gnews(query="technology"):
    print(f"Fetching from GNews with key: {bool(GNEWS_KEY)} | Query: {query}")

    if not GNEWS_KEY:
        print("Missing GNEWS_KEY")
        return []

    url = f"https://gnews.io/api/v4/search?q={query}&token={GNEWS_KEY}&lang=en"
    r = requests.get(url)
    print("Response status (GNews):", r.status_code)

    if r.status_code != 200:
        print("GNews request failed:", r.text)
        return []

    data = r.json()
    if not data.get("articles"):
        print("GNews returned no articles:", data)
        return []

    articles = [
        {
            "title": a.get("title"),
            "description": a.get("description"),
            "url": a.get("url"),
            "image": a.get("image"),
            "publishedAt": a.get("publishedAt"),
            "source": {
                "name": a.get("source") if isinstance(a.get("source"), str)
                else a.get("source", {}).get("name", "GNews")
            },
        }
        for a in data.get("articles", [])
        if a.get("title") and a.get("url")
    ]
    print(f"GNews returned {len(articles)} articles.")
    return articles



def fetch_reddit_news(query="technology", limit=15):
    """Fetch news from Reddit"""
    print(f"Fetching from Reddit | Query: {query}")
    
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("Missing Reddit credentials")
        return []
    
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent="NewsApp/1.0 by DescriptionFirm1268"
        )
        
        articles = []
        subreddits = ["worldnews", "news", "technology", "business", "science"]
        posts_per_subreddit = max(1, limit // len(subreddits))
        
        for subreddit_name in subreddits:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                
                for post in subreddit.search(query, limit=posts_per_subreddit, time_filter="day", sort="relevance"):
                    if post.is_self or not post.url:
                        continue
                    
                    article = {
                        "title": post.title,
                        "description": post.selftext[:200] if post.selftext else f"From r/{subreddit_name}",
                        "url": post.url,
                        "image": _extract_reddit_image(post),
                        "publishedAt": datetime.fromtimestamp(post.created_utc).isoformat(),
                        "source": {"name": f"Reddit r/{subreddit_name}"}
                    }
                    articles.append(article)
                    
            except Exception as e:
                print(f"Error fetching from r/{subreddit_name}: {e}")
                continue
        
        print(f"Reddit returned {len(articles)} articles.")
        return articles
        
    except Exception as e:
        print(f"Reddit API Error: {e}")
        return []


def _extract_reddit_image(post):
    """Extract image from Reddit post"""
    try:
        if hasattr(post, 'preview'):
            return post.preview['images'][0]['source']['url']
        if hasattr(post, 'thumbnail') and post.thumbnail.startswith('http'):
            return post.thumbnail
    except:
        pass
    return None



def get_combined_news(query="technology"):
    from datetime import datetime
    
    print(f"\nCombining news for query: '{query}'")
    results = []
    results.extend(fetch_newsapi(query))
    results.extend(fetch_gnews(query))
    results.extend(fetch_reddit_news(query, limit=15))
    
    print(f"Total combined articles: {len(results)}")
    
    # Sort articles by published date (newest first)
    try:
        results = sorted(
            results,
            key=lambda x: datetime.fromisoformat(
                x.get("publishedAt", "1970-01-01T00:00:00").replace("Z", "+00:00")
            ),
            reverse=True
        )
        print("Articles sorted by date (newest first)")
    except Exception as e:
        print(f"Error sorting articles: {e}")
    
    return results


def save_news_to_db(db: Session, articles):
    print(f"Saving {len(articles)} articles to DB...")
    for article in articles:
        exists = db.query(NewsBase).filter(NewsBase.url == article["url"]).first()
        if exists:
            continue

        published_at = None
        if article.get("publishedAt"):
            try:
                published_at = datetime.fromisoformat(
                    article["publishedAt"].replace("Z", "+00:00")
                )
            except Exception:
                published_at = datetime.utcnow()

        news_item = NewsBase(
            title=article["title"],
            source=article.get("source", {}).get("name", "Unknown"),
            publishedAt=published_at,
            url=article["url"],
            description=article.get("description"),
            image=article.get("image"),
        )
        db.add(news_item)
    db.commit()
    print("Articles saved successfully.")

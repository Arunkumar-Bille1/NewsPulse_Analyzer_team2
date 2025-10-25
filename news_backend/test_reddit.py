import os
from dotenv import load_dotenv
import praw

load_dotenv()

print("REDDIT_CLIENT_ID:", os.getenv("REDDIT_CLIENT_ID"))
print("REDDIT_CLIENT_SECRET:", os.getenv("REDDIT_CLIENT_SECRET"))

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="NewsApp/1.0 by DescriptionFirm1268"
)

subreddit = reddit.subreddit("technology")
for post in subreddit.hot(limit=3):
    print(post.title)

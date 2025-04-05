import os
import praw
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def fetch_reddit_posts(query="Tesla", subreddit="stocks", limit=5):
    posts = []
    try:
        for submission in reddit.subreddit(subreddit).search(query, limit=limit, sort='new'):
            if not submission.stickied:
                text = submission.title
                if submission.selftext:
                    text += f". {submission.selftext}"
                posts.append(text.strip())
    except Exception as e:
        print(f"Error fetching Reddit posts: {e}")
    
    return posts

# For quick testing
if __name__ == "__main__":
    posts = fetch_reddit_posts("Tesla")
    for p in posts:
        print("-", p)

from newsapi import NewsApiClient
import os
from dotenv import load_dotenv
from prediction_engine.features.sentiment import FinBERTSentimentAnalyzer


# ===== Load environment variables =====
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# ===== Initialize NewsAPI client =====
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
finbert = FinBERTSentimentAnalyzer()

# ===== Fetch latest news =====
def fetch_latest_news(query="Tesla", limit=5):
    try:
        articles = newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=limit)
        return [a['title'] + ". " + a['description'] for a in articles['articles'] if a['description']]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# ===== Get sentiment-scored news =====
def get_scored_news(symbol):
    headlines = fetch_latest_news(symbol)
    scored_news = []

    for headline in headlines:
        sentiment, scores = finbert.analyze(headline)
        scored_news.append({
            "headline": headline,
            "sentiment": sentiment,
            "scores": scores
        })

    return scored_news

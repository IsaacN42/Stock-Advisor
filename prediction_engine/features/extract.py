import pandas as pd
from prediction_engine.data_ingestion.news import get_scored_news
from prediction_engine.data_ingestion.price import fetch_price_data

def combine_features(symbol):
    # Get price data
    price_df = fetch_price_data(symbol)
    if price_df.empty:
        return None

    # Get sentiment-scored news
    news = get_scored_news(symbol)

    # Aggregate sentiment scores into average values
    sentiment_scores = {'positive': 0, 'neutral': 0, 'negative': 0}
    for item in news:
        for k in sentiment_scores:
            sentiment_scores[k] += item['scores'].get(k, 0)

    if news:
        for k in sentiment_scores:
            sentiment_scores[k] /= len(news)
    else:
        sentiment_scores = {k: 0 for k in sentiment_scores}

    # Add sentiment scores to the latest price row (most recent row)
    for k, v in sentiment_scores.items():
        price_df.at[price_df.index[-1], f'sentiment_{k}'] = v

    return price_df
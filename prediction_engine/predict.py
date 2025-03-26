from prediction_engine.data_ingestion.news import get_scored_news
from prediction_engine.data_ingestion.price import fetch_price_data
from prediction_engine.features.extract import combine_features
from prediction_engine.models import predict  # uses __init__.py

def run_prediction(symbol="TSLA"):
    # Fetch news with sentiment scores
    news = get_scored_news(symbol)

    # Fetch price data and add indicators
    price_df = fetch_price_data(symbol)

    # Combine all features into one DataFrame
    features = combine_features(symbol)
    if features is None:
        return f"⚠️ No data available for {symbol}, skipping."

    # Run the prediction model
    result = predict(features, news)

    return result

if __name__ == "__main__":
    print(run_prediction("TSLA"))

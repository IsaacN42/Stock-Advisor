from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Initialize FinBERT
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
labels = ['neutral', 'positive', 'negative']

def predict_with_finbert(features_df, news_items):
    if not news_items:
        return "🤖 No recent news to analyze. Cannot make a prediction."

    # Aggregate sentiment scores
    scores = {'positive': 0, 'neutral': 0, 'negative': 0}
    for item in news_items:
        text = item["headline"]
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1).squeeze()
        for i, label in enumerate(labels):
            scores[label] += float(probs[i])

    # Normalize scores
    for label in scores:
        scores[label] /= len(news_items)

    # Combine with technical RSI & MACD logic
    rsi = features_df['rsi'].iloc[-1] if 'rsi' in features_df else 50
    macd = features_df['macd'].iloc[-1] if 'macd' in features_df else 0

    # Decision logic
    sentiment_score = scores['positive'] - scores['negative']
    direction = "rise" if sentiment_score > 0.05 and macd > 0 and rsi < 70 else "drop"
    confidence = round(abs(sentiment_score) * 100 + abs(macd * 10), 2)
    reason = f"Sentiment skewed {direction} and MACD suggests momentum"

    return f"Prediction: {direction} with {confidence}% confidence. Reason: {reason}."

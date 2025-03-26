
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

class FinBERTSentimentAnalyzer:
    def __init__(self):
        # Load tokenizer and model from Hugging Face
        self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        self.model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
        self.labels = ['neutral', 'positive', 'negative']

    def analyze(self, text):
        # Tokenize and prepare the input
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Compute softmax probabilities
        probs = F.softmax(outputs.logits, dim=1).squeeze()

        # Build a dictionary of label: score
        scores = {label: float(probs[i]) for i, label in enumerate(self.labels)}
        
        # Choose the label with the highest score
        sentiment = max(scores, key=scores.get)

        return sentiment, scores

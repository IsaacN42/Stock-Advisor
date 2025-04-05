import { useEffect, useState } from 'react';

export default function PredictionCard({ symbol }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        const response = await fetch(`http://localhost:8000/predict/${symbol}`);
        const data = await response.json();
        setPrediction(data.prediction);
      } catch (error) {
        console.error("Error fetching prediction:", error);
        setPrediction("Error fetching prediction.");
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [symbol]);

  const renderPrediction = () => {
    if (typeof prediction !== 'string') return prediction;

    const lines = prediction.split('\n');
    return (
      <div className="space-y-2">
        {lines.map((line, idx) => {
          // Headlines
          if (line.startsWith('[')) {
            return <p key={idx} className="text-sm text-zinc-400">{line}</p>;
          }

          // Bold key info
          if (line.startsWith('[')) {
            return <p key={idx} className="font-medium">{line}</p>;
          }

          // Labeling
          if (line.startsWith("Prediction:") || line.startsWith("Reason:")) {
            return <p key={idx}><strong>{line}</strong></p>;
          }

          return <p key={idx}>{line}</p>;
        })}
      </div>
    );
  };

  return (
    <div className="rounded-2xl shadow-lg p-4 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white w-full max-w-xl">
      <h2 className="text-xl font-semibold mb-2">{symbol}</h2>
      {loading ? (
        <p className="animate-pulse">Loading prediction...</p>
      ) : (
        renderPrediction()
      )}
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import SymbolCard from "./components/symbol_card";

function App() {
  const [watchlist, setWatchlist] = useState([]);
  const [predictions, setPredictions] = useState({});

  useEffect(() => {
    const fetchConfigAndPredictions = async () => {
      try {
        // Load config.json via backend
        const configRes = await fetch("http://127.0.0.1:8000/config");
        const configData = await configRes.json();
        const symbols = configData.watchlist || [];
        setWatchlist(symbols);

        // Load prediction per symbol
        symbols.forEach(async (symbol) => {
          try {
            const res = await fetch(`http://127.0.0.1:8000/predict/${symbol}`);
            const data = await res.json();
            setPredictions(prev => ({ ...prev, [symbol]: data.prediction }));
          } catch (err) {
            console.error(`Failed to fetch prediction for ${symbol}`, err);
          }
        });
      } catch (error) {
        console.error("Failed to load config:", error);
      }
    };

    fetchConfigAndPredictions();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-6 space-y-6">
      <h1 className="text-4xl font-bold mb-4">📈 AI Trading Dashboard</h1>
      {watchlist.map(symbol => (
        <SymbolCard key={symbol} symbol={symbol} prediction={predictions[symbol]} />
      ))}
    </div>
  );
}

export default App;

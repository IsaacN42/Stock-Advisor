import React from 'react';
import PredictionCard from './components/prediction_card';

function App() {
  const symbols = ['TSLA', 'AAPL', 'NVDA', 'BTCUSD'];

  return (
    <div className="min-h-screen bg-zinc-900 p-8 text-white">
      <h1 className="text-3xl font-bold mb-6">Live Predictions Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {symbols.map((symbol) => (
          <PredictionCard key={symbol} symbol={symbol} />
        ))}
      </div>
    </div>
  );
}

export default App;

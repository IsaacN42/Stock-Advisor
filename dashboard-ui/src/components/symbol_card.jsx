import React from "react";

export default function SymbolCard({ symbol, prediction }) {
  const tvEmbedUrl = `https://www.tradingview.com/embed-widget/mini-symbol-overview/?symbol=${symbol}&interval=60&locale=en`;

  return (
    <div className="bg-zinc-900 rounded-2xl shadow-lg p-4 w-full max-w-5xl mx-auto text-white">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">{symbol}</h2>
        <span className="text-sm bg-zinc-700 px-2 py-1 rounded-full">
          Confidence: {extractConfidence(prediction)}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* TradingView chart */}
        <div className="h-72 w-full">
          <iframe
            src={tvEmbedUrl}
            frameBorder="0"
            className="w-full h-full rounded-xl"
            allowFullScreen
          ></iframe>
        </div>

        {/* News + Prediction */}
        <div className="overflow-y-auto max-h-72 bg-zinc-800 p-3 rounded-xl">
          <h3 className="text-lg font-semibold mb-2">Prediction Summary</h3>
          <pre className="whitespace-pre-wrap text-sm font-mono">
            {prediction || "Loading..."}
          </pre>
        </div>
      </div>
    </div>
  );
}

function extractConfidence(prediction) {
  if (!prediction) return "--";
  const match = prediction.match(/(\d{1,3}\.\d{1,2})%/);
  return match ? match[1] + "%" : "--";
}

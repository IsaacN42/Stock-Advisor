from fastapi import FastAPI
from prediction_engine.predict import run_prediction
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (localhost:5173 for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Stock Advisor API is running."}

@app.get("/predict/{symbol}")
def predict(symbol: str):
    result = run_prediction(symbol)
    return {"symbol": symbol, "prediction": result}

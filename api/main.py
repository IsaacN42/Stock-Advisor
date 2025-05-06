from fastapi import FastAPI
from prediction_engine.predict import run_prediction
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi.responses import JSONResponse

app = FastAPI()

# Allow frontend (localhost:5173 for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
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

@app.get("/config")
def get_config():
    try:
        with open("config.json", "r") as f:
            config_data = json.load(f)
        return JSONResponse(content=config_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
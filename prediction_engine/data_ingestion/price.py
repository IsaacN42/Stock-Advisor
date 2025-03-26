import os
import pandas as pd
from alpaca_trade_api.rest import REST
from datetime import datetime, timedelta
from dotenv import load_dotenv
import ta

load_dotenv()

APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = "https://api.alpaca.markets"

alpaca = REST(
    key_id=APCA_API_KEY_ID,
    secret_key=APCA_API_SECRET_KEY,
    base_url=ALPACA_BASE_URL
)

def fetch_price_data(symbol: str, days_back=3, interval='15Min'):
    end = datetime.utcnow()
    start = end - timedelta(days=days_back)

    try:
        bars = alpaca.get_bars(
            symbol,
            timeframe=interval,
            start=start.isoformat() + 'Z',
            end=end.isoformat() + 'Z',
            limit=1000,
            feed='iex'
        ).df


        if bars.empty:
            print(f"No data found for {symbol}.")
            return pd.DataFrame()

        bars.index = pd.to_datetime(bars.index)
        return bars

    except Exception as e:
        print(f"Failed to fetch price data for {symbol}: {e}")
        return pd.DataFrame()

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df['rsi'] = ta.momentum.rsi(df['close'])
    df['macd'] = ta.trend.macd_diff(df['close'])
    df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
    df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()

    return df

if __name__ == "__main__":
    df = fetch_price_data("TSLA")
    df = add_indicators(df)
    print(df.tail())
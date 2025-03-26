import discord
import asyncio
from newsapi.newsapi_client import NewsApiClient
from alpaca_trade_api.rest import REST
import pandas as pd
import ta
import mplfinance as mpf
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from prediction_engine.predict import run_prediction

# ====== Fetch Keys ======
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../keys.env'))

APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_USER_ID = int(os.getenv("DISCORD_USER_ID"))

# ====== Watchlist ======
WATCHLIST = ['BTCUSD', 'TSLA']

# ======= Alpaca Setup =======
ALPACA_BASE_URL = "https://api.alpaca.markets"
alpaca = REST(
    key_id=APCA_API_KEY_ID,
    secret_key=APCA_API_SECRET_KEY,
    base_url=ALPACA_BASE_URL
)

# ======= NewsAPI Setup =======
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

# ======= Discord Setup =======
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# ======= 1. Fetch Stock Data for Charting =======
def get_stock_data(symbol):
    try:
        today = datetime.utcnow()
        weekday = today.weekday()

        # Weekend logic (only for stocks)
        if '/' not in symbol and weekday >= 5:
            days_to_subtract = weekday - 4
            target_date = today - timedelta(days=days_to_subtract)
        else:
            target_date = today

        start_date = target_date.strftime('%Y-%m-%dT00:00:00Z')
        end_date = target_date.strftime('%Y-%m-%dT23:59:59Z')

        barset = alpaca.get_bars(
            symbol,
            timeframe='15Min',
            start=start_date,
            end=end_date,
            limit=1000
        ).df

        barset.index = pd.to_datetime(barset.index)
        print(f"Fetched Data for {symbol}")
        return barset
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# ======= 2. Plot Candlestick Chart =======
def plot_intraday_mplfinance(df, symbol):
    if df.empty:
        return None

    df.index.name = 'Date'
    charts_folder = os.path.join(os.path.dirname(__file__), 'charts')
    os.makedirs(charts_folder, exist_ok=True)

    date_str = df.index[0].strftime('%Y-%m-%d')
    filename = os.path.join(charts_folder, f"{symbol.replace('/', '')}_mpl-chart_{date_str}.png")

    style = mpf.make_mpf_style(base_mpf_style='nightclouds', rc={'font.size': 8})

    mpf.plot(df,
             type='candle',
             style=style,
             title=f"{symbol} Intraday Chart ({date_str})",
             ylabel='Price (USD)',
             volume=True,
             volume_panel=1,
             panel_ratios=(4, 1),
             savefig=filename)

    print(f"Saved chart as {filename}")
    return filename

# ======= 3. TradingView Link =======
def get_tradingview_link(symbol):
    if '/' in symbol:
        return f"https://www.tradingview.com/symbols/{symbol.replace('/', '')}USD/"
    else:
        return f"https://www.tradingview.com/symbols/{symbol.upper()}/"

# ======= 4. Advisor Core Loop with Prediction Integration =======
async def run_advisor():
    user = await client.fetch_user(DISCORD_USER_ID)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    for symbol in WATCHLIST:
        print(f"Running Advisor Check for {symbol}...")
        try:
            prediction_summary = run_prediction(symbol)
        except Exception as e:
            prediction_summary = f"⚠️ Error running prediction for {symbol}: {e}"

        chart_df = get_stock_data(symbol)
        chart_file = plot_intraday_mplfinance(chart_df, symbol)
        tradingview_link = get_tradingview_link(symbol)

        await user.send(f"{timestamp}\n{prediction_summary}\n🔗 Chart: {tradingview_link}")

        if chart_file:
            with open(chart_file, 'rb') as f:
                await user.send(file=discord.File(f))

        print(f"Notification sent for {symbol}.")

# ======= 5. Discord Events =======
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    while True:
        await run_advisor()
        await asyncio.sleep(900)  # Every 15 minutes

# ======= 6. Start Bot =======
client.run(DISCORD_TOKEN)

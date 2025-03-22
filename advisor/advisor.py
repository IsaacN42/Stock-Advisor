# advisor.py

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

# ====== Fetch Keys ======
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../keys.env'))

APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_USER_ID = int(os.getenv("DISCORD_USER_ID"))

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

# ======= 1. Fetch News =======
def get_latest_news(query='Tesla'):
    try:
        articles = newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=5)
        headlines = [article['title'] for article in articles['articles']]
        print(f"Fetched News: {headlines}")
        return headlines
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# ======= 2. Fetch Stock Data =======
def get_stock_data(symbol='TSLA'):
    try:
        today = datetime.utcnow()
        weekday = today.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun

        if weekday >= 5:
            # Weekend → pull Friday's data
            days_to_subtract = weekday - 4
            target_date = today - timedelta(days=days_to_subtract)
            print(f"Weekend detected. Pulling Friday's data: {target_date.date()}")
        else:
            # Weekday → pull today's data
            target_date = today
            print(f"Pulling today's data: {target_date.date()}")

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
        print(f"Fetched Stock Data for {symbol}")
        return barset
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return pd.DataFrame()

# ======= 3. Analyze Stock =======
def analyze_stock(df):
    if not df.empty:
        df['rsi'] = ta.momentum.rsi(df['close'])
        print(f"RSI Calculated: {df['rsi'].iloc[-1]:.2f}")
    return df

# ======= 4. Plot Candlestick Chart =======
def plot_intraday_mplfinance(df, symbol):
    if df.empty:
        return None

    df.index.name = 'Date'

    # Ensure charts folder exists
    charts_folder = os.path.join(os.path.dirname(__file__), 'charts')
    os.makedirs(charts_folder, exist_ok=True)

    filename = os.path.join(charts_folder, f"{symbol}_mpl_chart.png")

    style = mpf.make_mpf_style(base_mpf_style='nightclouds', rc={'font.size': 8})

    mpf.plot(df, type='candle', style=style,
             title=f"{symbol} Intraday Chart ({df.index[0].date()})",
             ylabel='Price (USD)',
             volume=True,
             savefig=filename)

    print(f"Saved chart as {filename}")
    return filename


# ======= 5. TradingView Dynamic Link =======
def get_dynamic_tradingview_link(symbol):
    return f"https://IsaacN42.github.io/stock-advisor/widget/?symbol=NASDAQ:{symbol}"

# ======= 6. Pattern Recognition Logic =======
def pattern_recognition(news, stock_df):
    try:
        if not stock_df.empty:
            latest_rsi = stock_df['rsi'].iloc[-1]
            keywords = ['recall', 'lawsuit', 'downgrade', 'negative']
            if any(any(k in n.lower() for k in keywords) for n in news) and latest_rsi > 70:
                return f"🚨 Negative Alert: {symbol} RSI={latest_rsi:.2f}, might drop."
    except Exception as e:
        print(f"Pattern recognition error: {e}")
    return None

# ======= 7. Advisor Core Function =======
async def run_advisor():
    print("Running Advisor Check...")
    symbol = 'TSLA'
    news = get_latest_news(symbol)
    stock_df = get_stock_data(symbol)
    stock_df = analyze_stock(stock_df)
    signal = pattern_recognition(news, stock_df)

    # Generate chart
    chart_file = plot_intraday_mplfinance(stock_df, symbol)
    tradingview_link = get_dynamic_tradingview_link(symbol)

    user = await client.fetch_user(DISCORD_USER_ID)

    if signal:
        await user.send(f"{signal}\nView {symbol} Interactive Chart: {tradingview_link}")
    else:
        await user.send(f"✅ Advisor Bot: No significant {symbol} pattern detected currently.\nView Chart: {tradingview_link}")

    # Send chart image
    if chart_file:
        with open(chart_file, 'rb') as f:
            await user.send(file=discord.File(f))

    print("Notification and chart sent.")

# ======= 8. Discord Bot Events =======
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Single run
    await run_advisor()
    await client.close()

# ======= 9. Run Bot =======
client.run(DISCORD_TOKEN)

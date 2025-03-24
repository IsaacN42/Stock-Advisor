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

# ====== Watchlist ======
WATCHLIST = ['BTCUSD']

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
def get_latest_news(query):
    try:
        articles = newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=5)
        headlines = [article['title'] for article in articles['articles']]
        print(f"Fetched News for {query}: {headlines}")
        return headlines
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# ======= 2. Fetch Stock Data =======
def get_stock_data(symbol):
    try:
        today = datetime.utcnow()
        weekday = today.weekday()

        # Weekend logic (only for stocks, crypto trades 24/7)
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

# ======= 3. Analyze Stock =======
def analyze_stock(df):
    if not df.empty:
        df['rsi'] = ta.momentum.rsi(df['close'])
        df['macd'] = ta.trend.macd_diff(df['close'])
        df['ema_short'] = ta.trend.ema_indicator(df['close'], window=12)
        df['ema_long'] = ta.trend.ema_indicator(df['close'], window=26)
        bb = ta.volatility.BollingerBands(df['close'])
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        print(f"Indicators calculated: RSI={df['rsi'].iloc[-1]:.2f}, MACD={df['macd'].iloc[-1]:.2f}")
    return df

# ======= 4. Plot Candlestick Chart =======
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
             panel_ratios=(4,1),
             savefig=filename)

    print(f"Saved chart as {filename}")
    return filename

# ======= 5. TradingView Dynamic Link =======
def get_dynamic_tradingview_link(symbol):
    if '/' in symbol:
        # For crypto (assuming you're using USD pairs like BTC/USD)
        clean_symbol = symbol.replace('/', '')
        return f"https://www.tradingview.com/symbols/{clean_symbol.upper()}USD/"
    else:
        # For stocks
        return f"https://www.tradingview.com/symbols/{symbol.upper()}/"


# ======= 6. Pattern Recognition Logic =======
def pattern_recognition(news, stock_df, symbol):
    try:
        if not stock_df.empty:
            latest_rsi = stock_df['rsi'].iloc[-1]
            latest_macd = stock_df['macd'].iloc[-1]
            ema_short = stock_df['ema_short'].iloc[-1]
            ema_long = stock_df['ema_long'].iloc[-1]
            close = stock_df['close'].iloc[-1]
            bb_upper = stock_df['bb_upper'].iloc[-1]
            bb_lower = stock_df['bb_lower'].iloc[-1]

            keywords = ['recall', 'lawsuit', 'downgrade', 'negative', 'upgrade', 'invest']
            alert_msgs = []

            # RSI Overbought/Oversold
            if latest_rsi > 70:
                alert_msgs.append(f"⚠️ {symbol} RSI={latest_rsi:.2f} Overbought, possible drop.")
            elif latest_rsi < 30:
                alert_msgs.append(f"⚠️ {symbol} RSI={latest_rsi:.2f} Oversold, possible rise.")

            # MACD Crossover
            if stock_df['macd'].iloc[-2] < 0 and latest_macd > 0:
                alert_msgs.append(f"📊 {symbol} MACD Bullish Crossover.")
            elif stock_df['macd'].iloc[-2] > 0 and latest_macd < 0:
                alert_msgs.append(f"📊 {symbol} MACD Bearish Crossover.")

            # EMA Crossover
            if ema_short > ema_long and stock_df['ema_short'].iloc[-2] <= stock_df['ema_long'].iloc[-2]:
                alert_msgs.append(f"📈 {symbol} EMA Bullish Crossover.")
            elif ema_short < ema_long and stock_df['ema_short'].iloc[-2] >= stock_df['ema_long'].iloc[-2]:
                alert_msgs.append(f"📉 {symbol} EMA Bearish Crossover.")

            # Bollinger Band Breaches
            if close > bb_upper:
                alert_msgs.append(f"🚀 {symbol} closing above Bollinger Upper Band.")
            elif close < bb_lower:
                alert_msgs.append(f"🔻 {symbol} closing below Bollinger Lower Band.")

            # News Keywords
            for n in news:
                if any(k in n.lower() for k in keywords):
                    alert_msgs.append(f"📰 News Trigger: \"{n}\"")

            if alert_msgs:
                return "\n".join(alert_msgs)
    except Exception as e:
        print(f"Pattern recognition error: {e}")
    return None

# ======= 7. Advisor Core Function =======
async def run_advisor():
    user = await client.fetch_user(DISCORD_USER_ID)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    for symbol in WATCHLIST:
        print(f"Running Advisor Check for {symbol}...")
        news = get_latest_news(symbol)
        stock_df = get_stock_data(symbol)
        stock_df = analyze_stock(stock_df)
        signal = pattern_recognition(news, stock_df, symbol)

        tradingview_link = get_dynamic_tradingview_link(symbol)
        chart_file = plot_intraday_mplfinance(stock_df, symbol)

        if signal:
            await user.send(f"{timestamp}\n{signal}\nChart: {tradingview_link}")
        else:
            await user.send(f"{timestamp}\n✅ No significant {symbol} pattern detected. Chart: {tradingview_link}")

        if chart_file:
            with open(chart_file, 'rb') as f:
                await user.send(file=discord.File(f))
        print(f"Notification sent for {symbol}.")

# ======= 8. Discord Bot Events =======
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    while True:
        await run_advisor()
        await asyncio.sleep(900)  # Every 15 mins

# ======= 9. Run Bot =======
client.run(DISCORD_TOKEN)
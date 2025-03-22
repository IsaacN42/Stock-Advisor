import discord
import asyncio
from newsapi.newsapi_client import NewsApiClient
from alpaca_trade_api.rest import REST
import pandas as pd
import ta
import mplfinance as mpf

# ======= Alpaca Setup =======
APCA_API_KEY_ID = "AKSUSZTC5PKLOPWJBFMV"
APCA_API_SECRET_KEY = "eD1nWPj81V4eVbfmqWh2iBHEMRpRJdPO4bclz3wa"
ALPACA_BASE_URL = "https://api.alpaca.markets"

alpaca = REST(
    key_id=APCA_API_KEY_ID,
    secret_key=APCA_API_SECRET_KEY,
    base_url=ALPACA_BASE_URL
)

# ======= NewsAPI Setup =======
newsapi = NewsApiClient(api_key="f44aab4e002a486aa166613714fe8151")

# ======= Discord Setup =======
DISCORD_TOKEN = "MTM1Mjc2MTQxNjM3MjcxNTU5MA.GihUiC.7e2RaYBWv84fqr8wOXRsfQkytErZAB3x3SZugg"
DISCORD_USER_ID = 477583926525820948  # Replace with your ID (int)

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
        barset = alpaca.get_bars(symbol, '1Min', limit=100).df
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

    filename = f"{symbol}_mpl_chart.png"

    style = mpf.make_mpf_style(base_mpf_style='nightclouds', rc={'font.size': 8})

    mpf.plot(df, type='candle', style=style,
             title=f"{symbol} Intraday Chart",
             ylabel='Price (USD)',
             volume=True,
             savefig=filename)

    print(f"Saved chart as {filename}")
    return filename

# ======= 5. TradingView Dynamic Link =======
def get_dynamic_tradingview_link(symbol):
    return f"https://IsaacN42.github.io/tradingview-charts/?symbol=NASDAQ:{symbol}"

# ======= 6. Pattern Recognition Logic =======
def pattern_recognition(news, stock_df):
    try:
        if not stock_df.empty:
            latest_rsi = stock_df['rsi'].iloc[-1]
            keywords = ['recall', 'lawsuit', 'downgrade', 'negative']
            if any(any(k in n.lower() for k in keywords) for n in news) and latest_rsi > 70:
                return f"🚨 Negative Alert: TSLA RSI={latest_rsi:.2f}, might drop."
    except Exception as e:
        print(f"Pattern recognition error: {e}")
    return None

# ======= 7. Advisor Core Function =======
async def run_advisor():
    print("Running Advisor Check...")
    news = get_latest_news('TSLA')
    stock_df = get_stock_data('TSLA')
    stock_df = analyze_stock(stock_df)
    signal = pattern_recognition(news, stock_df)

    # Generate chart
    chart_file = plot_intraday_mplfinance(stock_df, 'TSLA')
    tradingview_link = get_dynamic_tradingview_link('TSLA')

    user = await client.fetch_user(DISCORD_USER_ID)

    if signal:
        await user.send(f"{signal}\nView TSLA Interactive Chart: {tradingview_link}")
    else:
        await user.send(f"✅ Advisor Bot: No significant TSLA pattern detected currently.\nView TSLA Chart: {tradingview_link}")

    # Send chart image
    if chart_file:
        with open(chart_file, 'rb') as f:
            await user.send(file=discord.File(f))

    print("Notification and chart sent.")

# ======= 8. Discord Bot Events =======
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Option 1: Single run
    await run_advisor()
    await client.close()

    # Option 2 (optional): Keep checking every X minutes
    # while True:
    #     await run_advisor()
    #     await asyncio.sleep(900)  # Every 15 minutes

# ======= 9. Run Bot =======
client.run(DISCORD_TOKEN)

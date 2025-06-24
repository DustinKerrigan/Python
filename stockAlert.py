import discord
from discord.ext import tasks, commands
import pandas as pd
import yfinance as yf
import datetime
import pytz
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
channel_id = 1339315526295359518
stocks = ["META", "NVDA", "GS", "WFC", "ENPH", "CAT", "NCLH", "MGM", "CMCSA", "NKE", "SBUX","DAL","HD","AFRM","RBLX","VLO","CVX","CRWD","COST","TSLA"]
opening_prices = {} 
MARKET_OPEN_TIME = datetime.time(9, 45, 0)  # 9:45 AM ET
MARKET_CLOSE_TIME = datetime.time(16, 0, 0)  # 4:00 PM ET
eastern_tz = pytz.timezone('US/Eastern')

def is_market_open():
    now = datetime.datetime.now(eastern_tz)
    current_time = now.time()
    is_weekday = now.weekday() < 5
    is_within_hours = MARKET_OPEN_TIME <= current_time <= MARKET_CLOSE_TIME
    return is_weekday and is_within_hours

async def get_daily_open(stock):
    try:
        data = yf.download(stock, period='1d', auto_adjust=False)
        return round(float(data['Open'].iloc[0]), 2)
    except Exception as e:
        print("Error fetching daily open price for", stock, ":", e)
        return None

async def get_current_price(stock):
    try:
        data = yf.download(stock, period='1d', auto_adjust=False)
        return round(float(data['Close'].iloc[-1]), 2)
    except Exception as e:
        print("Error fetching current price for", stock, ":", e)
        return None

@tasks.loop(minutes=1)
async def check_stock_prices():
    if not is_market_open():
        now = datetime.datetime.now(eastern_tz)
        current_time = now.time()
        if MARKET_CLOSE_TIME <= current_time <= datetime.time(16, 1, 0):
            print(f"⏳Market closed at {now.strftime('%H:%M:%S')}.⏳")
            opening_prices.clear()  # Reset opening prices for next day
        return
    
    if not opening_prices:
        channel = bot.get_channel(channel_id)
        now = datetime.datetime.now(eastern_tz)
        await channel.send(f"⏳Market monitoring started at {now.strftime('%H:%M:%S ET')}.⏳")
    
    for stock in stocks:
        current_price = await get_current_price(stock)
        if current_price is None:
            continue  
        if stock not in opening_prices:
            opening_prices[stock] = await get_daily_open(stock)
        opening_price = opening_prices.get(stock)
        if opening_price is not None and current_price is not None and current_price == opening_price:
            await send_stock_alert(stock, current_price)

async def send_stock_alert(stock, price):
    try:
        channel = bot.get_channel(channel_id)
        message = f"📢Price Alert: {stock} has reached its DAILY OPENING price of {price}."
        await channel.send(message)  # send message to chat
    except Exception as e:
        print("Error sending message", e)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_stock_prices.start()
    print("Bot is running. It will automatically monitor stocks during market hours.")

bot.run(TOKEN)
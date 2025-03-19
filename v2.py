import schedule
import time
import asyncio
import discord
from discord.ext import tasks, commands
import pandas as pd
import yfinance as yf
import threading
from datetime import datetime

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
channel_id = 1339315526295359518

stocks = ["META", "NVDA", "GS", "WFC", "ENPH", "CAT", "NCLH", "MGM", "CMCSA", "PARA", "NKE", "SBUX", "DAL", "HD", "AFRM", "RBLX", "VLO", "CVX", "CRWD", "COST", "TSLA"]

opening_prices = {}  
running = False  #state flag

async def get_daily_open(stock):
    try:
        data = yf.download(stock, period='1d', auto_adjust=False)
        return round(float(data['Open'].iloc[0]), 2)
    except Exception as e:
        print(f"Error fetching daily open price for {stock}: {e}")
        return None

async def get_current_price(stock):
    try:
        data = yf.download(stock, period='1d', auto_adjust=False)
        return round(float(data['Close'].iloc[-1]), 2)
    except Exception as e:
        print(f"Error fetching current price for {stock}: {e}")
        return None

@tasks.loop(minutes=1)
async def check_stock_prices():
    for stock in stocks:
        current_price = await get_current_price(stock)
        if current_price is None:
            continue  
        if stock not in opening_prices:
            opening_prices[stock] = await get_daily_open(stock)
        opening_price = opening_prices.get(stock)
        if opening_price is not None and current_price == opening_price:
            await send_stock_alert(stock, current_price)

async def send_stock_alert(stock, price):
    try:
        channel = bot.get_channel(channel_id)
        message = f"Price Alert: {stock} has reached its DAILY OPENING price of {price}."
        await channel.send(message)
    except Exception as e:
        print(f"Error sending message: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_stock_prices.start()

async def start_bot():
    global running
    if not running:
        print("Starting bot...")
        running = True
        await bot.start("MTE5NjYwODkwNjQzNzM0OTQ5Nw.G__5WS.VGGMFzYRFToEny04InLybSh43rXZZwnirPmPRo")

async def stop_bot():
    global running
    if running:
        print("Stopping bot...")
        running = False
        check_stock_prices.cancel() 
        await bot.close()

def run_scheduler():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    #bot start at 9:45 AM and stop at 4:00 PM
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        getattr(schedule.every(), day).at("09:45").do(lambda: loop.create_task(start_bot()))
        getattr(schedule.every(), day).at("16:00").do(lambda: loop.create_task(stop_bot()))

    print("Scheduler running... Waiting for 9:45 AM.")

    while True:
        schedule.run_pending()
        time.sleep(30)  

#scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

#if we need to start the bot immediately (if it's within market hours)
now = datetime.now().time()
market_open = datetime.strptime("09:45", "%H:%M").time()
market_close = datetime.strptime("16:00", "%H:%M").time()

if market_open <= now <= market_close:
    asyncio.run(start_bot())  #start the bot immediately if it's within trading hours

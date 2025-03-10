import discord
from discord.ext import tasks, commands
import pandas as pd
import yfinance as yf

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

channel_id = 1339315526295359518

stocks = ["META", "NVDA", "GS", "WFC", "ENPH", "CAT", "NCLH", "MGM", "CMCSA", "PARA", "NKE", "SBUX","DAL","HD","AFRM","RBLX","VLO","CVX","CRWD","COST","TSLA"]

opening_prices = {}  # store the daily open
#current version as of 3/10/25
async def get_daily_open(stock):
    try:
        data = yf.download(stock, period='1d',auto_adjust=False)
        return round(float(data['Open'].iloc[0]),2) #adjusted this
    except Exception as e:
        print("Error fetching daily open price for", stock, ":", e)
        return None

async def get_current_price(stock):
    try:
        data = yf.download(stock, period='1d',auto_adjust=False)
        return round(float(data['Close'].iloc[-1]),2)  #adjusted this
    except Exception as e:
        print("Error fetching current price for", stock, ":", e)
        return None

@tasks.loop(minutes=1)
async def check_stock_prices():
    for stock in stocks:
        current_price = await get_current_price(stock)
        if current_price is None:
            continue  #skip if no price is fetched
        if stock not in opening_prices:
            opening_prices[stock] = await get_daily_open(stock)
        opening_price = opening_prices.get(stock)
        if opening_price is not None and current_price is not None and current_price == opening_price:
            await send_stock_alert(stock, current_price)

async def send_stock_alert(stock, price):
    try:
        channel = bot.get_channel(channel_id)
        message = f"Price Alert: {stock} has reached its DAILY OPENING price of {price}."
        await channel.send(message)  # send message to chat
    except Exception as e:
        print("Error sending message", e)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_stock_prices.start()

bot.run("MTE5NjYwODkwNjQzNzM0OTQ5Nw.G__5WS.VGGMFzYRFToEny04InLybSh43rXZZwnirPmPRo")


import os
import time
import yfinance as yf
import discord
from discord.ext import tasks, commands

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

channel_id = 1197258358508494850  

stocks = ["UAA", "META", "NVDA", "GS", "WFC","ENPH","CAT","NCLH","MGM","CMCSA","PARA","NKE","SBUX"]

opening_prices = {} #store the daily open

@tasks.loop(seconds=60)  
async def check_stock_prices():
    for i, stock in enumerate(stocks):
        data = yf.download(stock, period="1d")
        current_price = round(data["Close"].iloc[-1],2)
        if stock not in opening_prices: #store opening price when needed
            opening_prices[stock] = round(data["Open"].iloc[0],2)
            continue  
        opening_price = opening_prices[stock] #retrieve price to be compared to daily open 
        if current_price == opening_price:
            await send_stock_alert(stock, current_price)

async def send_stock_alert(stock, price):
    channel = bot.get_channel(channel_id)
    message = f"Price Alert: {stock} has reached its DAILY OPENING price of {price}."
    await channel.send(message) #send message to chat

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_stock_prices.start()

bot.run("MTE5NjYwODkwNjQzNzM0OTQ5Nw.GWVR7F.ETxve754K25m4hLYuf8J_0O4fNvd0FOKDkBx6g") 

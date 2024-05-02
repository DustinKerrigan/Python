import discord
from discord.ext import tasks, commands
import datetime
import requests
import csv
import pandas as pd

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

channel_id = 1197258358508494850

stocks = ["UAA", "META", "NVDA", "GS", "WFC","ENPH","CAT","NCLH","MGM","CMCSA","PARA","NKE","SBUX"]

opening_prices = {}  # store the daily open

YAHOO_TODAY = "http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sd1ohgl1vl1"

def get_quote_today(symbol):
    response = requests.get(YAHOO_TODAY % symbol)
    reader = csv.reader(response.text.strip().split("\n"))
    for row in reader:
        if row[0] == symbol:
            return row

def get_daily_open(symbol):
    today = datetime.date.today()
    df = pd.DataFrame(index=pd.DatetimeIndex(start=today, end=today, freq="D"),
                      columns=["Open", "High", "Low", "Close", "Volume", "Adj Close"],
                      dtype=float)
    row = get_quote_today(symbol)
    df.iloc[0] = list(map(float, row[2:]))
    return df

@tasks.loop(minutes=1)
async def check_stock_prices():
    for stock in stocks:
        current_price = get_current_price(stock)
        if current_price is None:
            continue
        opening_price = get_opening_price(stock)
        if current_price == opening_price:
            await send_stock_alert(stock, current_price)

def get_current_price(stock):
    YAHOO_QUOTE = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock}"
    response = requests.get(YAHOO_QUOTE)
    data = response.json()
    if 'error' in data:
        return None
    return round(data['quoteResponse']['result'][0]['regularMarketPrice'], 2)

def get_opening_price(stock):
    if stock not in opening_prices:
        opening_prices[stock] = fetch_opening_price(stock)
    return opening_prices[stock]

def fetch_opening_price(stock):
    response = requests.get(YAHOO_TODAY % stock)
    reader = csv.reader(response.text.strip().split("\n"))
    for row in reader:
        if row[0] == stock:
            return float(row[2])
    return None

async def send_stock_alert(stock, price):
    channel = bot.get_channel(channel_id)
    message = f"Price Alert: {stock} has reached its DAILY OPENING price of {price}."
    await channel.send(message)  # send message to chat

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_stock_prices.start()

bot.run("MTE5NjYwODkwNjQzNzM0OTQ5Nw.G__5WS.VGGMFzYRFToEny04InLybSh43rXZZwnirPmPRo")

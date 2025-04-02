import asyncio
import discord
from discord.ext import tasks, commands
import yfinance as yf
from datetime import datetime

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
channel_id = 1339315526295359518  # Replace with your actual channel ID

stocks = ["META", "NVDA", "GS", "WFC", "ENPH", "CAT", "NCLH", "MGM", "CMCSA", "PARA", 
          "NKE", "SBUX", "DAL", "HD", "AFRM", "RBLX", "VLO", "CVX", "CRWD", "COST", "TSLA"]

opening_prices = {}
running = False  # State flag

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
        if channel:
            message = f"📢 Price Alert: {stock} has reached its DAILY OPENING price of {price}."
            await channel.send(message)
        else:
            print("⚠️ Channel not found.")
    except Exception as e:
        print(f"⚠️ Error sending message: {e}")

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')
    check_stock_prices.start()

async def start_bot():
    global running
    if not running:
        print("🚀 Starting bot...")
        running = True
        await bot.start("MTE5NjYwODkwNjQzNzM0OTQ5Nw.G__5WS.VGGMFzYRFToEny04InLybSh43rXZZwnirPmPRo")  # Replace with your actual bot token

async def stop_bot():
    global running
    if running:
        print("🛑 Stopping bot...")
        running = False
        check_stock_prices.cancel()
        await bot.close()  # Proper shutdown of the bot

async def bot_scheduler():
    """Scheduler that runs in the bot's event loop, ensuring it doesn't shut down immediately."""
    while True:
        now = datetime.now().time()
        market_open = datetime.strptime("09:45", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()

        if market_open <= now <= market_close:
            if not running:
                print("⏳ Market open - Starting bot from scheduler...")
                await start_bot()
        else:
            if running:
                print("⏳ Market closed - Stopping bot from scheduler...")
                await stop_bot()

        await asyncio.sleep(60)  # Check every minute

async def main():
    """Runs the bot and scheduler together using asyncio.run()."""
    asyncio.create_task(bot_scheduler())  # Run scheduler in the background
    await start_bot()  # Start bot in main event loop

if __name__ == "__main__":
    try:
        asyncio.run(main())  # ✅ FIX: Use asyncio.run() instead of get_event_loop()
    except KeyboardInterrupt:
        print("🛑 Bot stopped manually.")

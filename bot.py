import discord  # Library for creating discord bots
from discord.ext import commands  # Allows us to create commands for the bot
import requests  # Used to send HTTP requests to fetch web pages
from bs4 import BeautifulSoup  # A library for parsing HTML and extracting data from web pages

DISCORD_TOKEN = "MTIzMzQ0MTk2MDA2OTU2NjUxNA.G_qCzE.SHx4pPMUe9lHNc7K4iIK6kOorDyEcHxBUTtX5U"
CHANNEL_ID = 1233457185443414106


# Creates a bot instance with the command prefix '!'
# Any message starting with '!' will be interpreted as a command for the bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# Defining a global list to store the watched stocks
watched_stocks = []


# Event handler that runs when the bot successfully connects to Discord
# Prints a message to indicate that the bot has logged in
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello! Stock bot is ready")


# Greetings
@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")


# Ask bot for details about a single or multiple stocks in a single msg
@bot.command()
async def stocks(ctx, *stock_symbols):
    stock_data = fetch_stock_data(stock_symbols)
    for data in stock_data:
        await ctx.send(f"Stock Symbol: {data['Symbol']}\nCurrent Price: {data['Current Price']}\nExpected Price: {data['Expected Price']}\nChange: {data['Change']}\nPercent Change: {data['Percent Change']}")


# Ask bot for a specific detail that applies to the followign stocks in a single msg
@bot.command()
async def stockInfo(ctx, info_type, *stock_symbols):
    valid_info_types = ['Symbol', 'Current Price', 'Expected Price', 'Change', 'PercentChange']
    if info_type.capitalize() not in valid_info_types:
        await ctx.send(f"Invalid info type. Valid info types are: {', '.join(valid_info_types)}")
        return
    
    stock_data = fetch_stock_data(stock_symbols)
    for data in stock_data:
        info = data.get(info_type.capitalize(), "Invalid Info Type")
        await ctx.send(f"{info_type.capitalize()}: {info}")


# Ask bot to add stocks of choice to your watchList so you can check up on them quickly whenever you'd like
@bot.command()
async def watchStocks(ctx, *stock_symbols):
    global watched_stocks
    watched_stocks.extend(stock_symbols)
    await ctx.send(f"Added {', '.join(stock_symbols)} to the watchlist.")


# Ask bot to show you the details of your preferred stocks (quicker than asking for stocks by typing names again)
@bot.command()
async def viewStocks(ctx):
    global watched_stocks
    if watched_stocks:
        await ctx.send("Watchlist:")
        stock_data = fetch_stock_data(watched_stocks)
        for data in stock_data:
            await ctx.send(f"Stock Symbol: {data['Symbol']}\nCurrent Price: {data['Current Price']}\nExpected Price: {data['Expected Price']}\nChange: {data['Change']}\nPercent Change: {data['Percent Change']}")
    else:
        await ctx.send("Watchlist is empty.")


# Communicatign with Yahoo Finance Page to collect the information we need
def fetch_stock_data(stock_symbols):
    stock_data = []

    for stock_symbol in stock_symbols:

        # Using the Yahoo Finance API to get data about the Current Price and the Expected Target Price
        apiUrl = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/stock/modules"
        querystring = {"ticker":stock_symbol,"module":"financial-data"}
        headers = {
	        "X-RapidAPI-Key": "d1d1495a3fmsh88e16d854d024c3p14d747jsnfe2f6a8d04e0",
	        "X-RapidAPI-Host": "yahoo-finance15.p.rapidapi.com"
        }

        response = requests.get(apiUrl, headers=headers, params=querystring)
        data = response.json()
        price = data['body']['currentPrice']['raw']
        exp = data['body']['targetMeanPrice']['raw']
        
        # Using Yahoo Finance URL and BeautifulSoup Library to Scrape data about the Price Change in terms of currency and percentage
        url = f"https://finance.yahoo.com/quote/{stock_symbol}"

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching data for {stock_symbol}: {e}")
            continue

        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, "html.parser")

        # Using the tags and class names to find the associated value
        change_element = soup.find('div', {'class': 'Mend(20px)'}).find_all('span')[0]
        change = change_element.text
        percent_change_element = soup.find('div', {'class': 'Mend(20px)'}).find_all('span')[1]
        percent_change = percent_change_element.text

        # Append data to list
        stock_data.append({
            "Symbol": stock_symbol,
            "Current Price": price,
            "Expected Price": exp,
            "Change": change,
            "Percent Change": percent_change
        })

    return stock_data


# Running the bot
bot.run(DISCORD_TOKEN)


'''
Sample inputs:
!hello
!stocks AAPL GOOG AMZN
!stockInfo change AAPL MSFT
!watchStocks AAPL GME
!viewStocks
'''
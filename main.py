import requests
import datetime
from newsapi import NewsApiClient
from html import unescape

# Specific company informations

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

# API setup
stock_price_api_endpoint = "https://www.alphavantage.co/query"
stock_price_api_parameters = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": "5E5JA9IZVZBDDZBF",
}

# Getting stocks informations for company from API
company_stocks = requests.get(
    url=stock_price_api_endpoint, params=stock_price_api_parameters
)
company_stocks_json = company_stocks.json()


now = datetime.datetime.now()

# Checking if stocks API has information for today
try:
    todays_stock_date = now.date()
    today_stock = company_stocks_json["Time Series (Daily)"][str(todays_stock_date)]

# If not get previous day info
except KeyError:
    todays_stock_date = now.today() - datetime.timedelta(1)
    # Looping for a last work day beacouse API does not have info on Saturday or Sunday
    while todays_stock_date.weekday() > 4:
        todays_stock_date = now.today() - datetime.timedelta(1)

    # Looping for a workday before a date in "todays_stock_date" variable.
    last_stock_date = todays_stock_date - datetime.timedelta(1)
    while last_stock_date.weekday() > 4:
        last_stock_date -= datetime.timedelta(1)

    # Getting ifo from API about stocks from 2 days
    today_stock = company_stocks_json["Time Series (Daily)"][
        str(todays_stock_date.date())
    ]
    yesterday_stock = company_stocks_json["Time Series (Daily)"][
        str(last_stock_date.date())
    ]
else:
    # If stock has gotten info for todays stocks setup the rest of API info
    last_stock_date = now.date() - datetime.timedelta(1)
    while last_stock_date.weekday() > 4:
        last_stock_date -= datetime.timedelta(1)

    yesterday_stock = company_stocks_json["Time Series (Daily)"][
        str(last_stock_date.date())
    ]

finally:
    # Prices of the stocks at close time of a day
    today_stock_close_price = float(today_stock["4. close"])
    yesterday_stock_close_price = float(yesterday_stock["4. close"])


# Checking if stocks changed more than 5%
good_news = (
    today_stock_close_price / yesterday_stock_close_price < 0.95,
    today_stock_close_price / yesterday_stock_close_price > 1.05,
)

# If stock changed create txt file with news of what could happend for that price jump
if any(good_news):
    print("Good news")

    # API setup
    newsapi = NewsApiClient(api_key="a63f2fc526624ba58c49fc3df5f4553b")
    top_articles = newsapi.get_everything(
        q=COMPANY_NAME, sort_by="relevancy", language="en", page_size=100
    )

    # Top 3 most relevant articles
    top_3_articles = top_articles["articles"][:3]

    # Dictionary with article titles as keys and contents as values
    top_3_articles_content = {
        article["title"]: article["content"] for article in top_3_articles
    }

    # Create txt file
    with open("articles.txt", "w") as stocks_news_file:

        # write articles into txt and unescape from html tags in text problem
        for key, message in top_3_articles_content.items():
            stocks_news_file.write(
                f"Headline: {unescape(key)}\nContent: {unescape(message)}\n\n"
            )

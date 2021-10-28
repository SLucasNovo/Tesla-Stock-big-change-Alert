import requests
import datetime as dt
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API = ''
STOCK_API_KEY = os.environ.get('stock_key')
STOCK_PARAMS = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'TSLA',
    'apikey': STOCK_API_KEY
}

NEWS_API_KEY = os.environ.get('newsapy_key')
NEWS_API = 'https://newsapi.org/v2/everything'
NEWS_PARAMS = {
    'apiKey': NEWS_API_KEY,
    'q': 'Tesla'

}

ACCOUNT_SID = os.environ.get('account_sid')
AUTH_TOKEN = os.environ.get('auth_token')


# ---------------------------------NEWS --------------------------------- #

def get_news():
    news_response = requests.get(NEWS_API, NEWS_PARAMS)
    news_response.raise_for_status()
    news_data = news_response.json()
    articles = news_data['articles'][:3]

    articles_dict = {i['title']: i['description'] for i in articles}

    message = ''
    for k, v in articles_dict.items():
        message += f'Headline: {k}\nBrief:{v}\n'
    return message

# ---------------------------------SEND MESSAGE --------------------------------- #


def send_message(news):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages \
        .create(
            body=news,
            from_='TWILLIO_PHONE_NUMBER',
            to='PHONE_NUMBER'
        )


# ---------------------------------STOCK PRICE --------------------------------- #

# Get today/yesterday date formatted as string
weekend_days = [5, 6]
year = dt.datetime.now().year
month = dt.datetime.now().month
day = dt.datetime.now().day
today = dt.datetime.today().strftime('%Y-%m-%d')
yesterday = dt.date(year, month, (day-1)).strftime('%Y-%m-%d')
yesterdayterday = dt.date(year, month, (day-2)).strftime('%Y-%m-%d')

# Connect to Stock Price Api
price_response = requests.get('https://www.alphavantage.co/query', params=STOCK_PARAMS)
price_response.raise_for_status()
price_data = price_response.json()
# print(price_data)

# Get closing time price and opening time price
price_daily_data = price_data['Time Series (Daily)']

# close_yesterday = float(price_daily_data[yesterday]['4. close'])
# open_today = float(price_daily_data[today]['1. open'])
close_yesterday = float(price_daily_data[yesterdayterday]['4. close'])
open_today = float(price_daily_data[yesterday]['4. close'])
percentage_difference = (open_today-close_yesterday)/close_yesterday

# Check if there's cause to message me variance bigger than 5%
if abs(percentage_difference) > 0.01:
    headline = ''
    if percentage_difference > 0:
        headline = f'TSLA 🔺{round(percentage_difference*100,0)}%\n'
    else:
        headline = f'TSLA 🔻{round(percentage_difference * 100, 0)}%\n'
    headline += get_news()
    send_message(headline)

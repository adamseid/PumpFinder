from django.shortcuts import render
import requests
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta


API_KEY = 'z1uI5pTNJXNMNsos8W2z0JboBUePPSH1'
BASE_URL = 'https://api.polygon.io'

def get_today_data(ticker):
    current_date = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
    print(yesterday)
    url = f'{BASE_URL}/v1/open-close/{ticker}/{yesterday}?apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    print(url)

    if response.status_code != 200:
        print(f"Error fetching data: {data['error']}")
        return None
    
    print(data)

def get_weekly_macd(ticker,timestamp):
    url = f'{BASE_URL}/v1/indicators/macd/{ticker}?timestamp={timestamp}&timespan=week&adjusted=true&short_window=12&long_window=26&signal_window=9&series_type=close&order=desc&limit=10&apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print(f"Error fetching data: {data['error']}")
        return None

    macdData = data['results']

    if(macdData['values']):
        return macdData['values'][0]['histogram']
    return "Error"

def get_daily_macd(ticker,timestamp):
    url = f'{BASE_URL}/v1/indicators/macd/{ticker}?timestamp={timestamp}&timespan=day&adjusted=true&short_window=12&long_window=26&signal_window=9&series_type=close&order=desc&limit=10&apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print(f"Error fetching data: {data['error']}")
        return None

    macdData = data['results']

    if(macdData['values']):
        return macdData['values'][0]['histogram']
    return "Trading Day Not Over"

def get_previous_data(ticker):
    url = f'{BASE_URL}/v2/aggs/ticker/{ticker}/prev?apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print(f"Error fetching data: {data['error']}")
        return None

    df = pd.DataFrame(data['results'])
    df['t'] = pd.to_datetime(df['t'], unit='ms').dt.date
    ticker = df['T'].iloc[0] 
    timestamp = df['t'].iloc[0] 
    # df['DMACD'] = get_daily_macd(ticker,timestamp)
    # df['WMACD'] = get_weekly_macd(ticker,timestamp)
    df.set_index('t', inplace=True)
    # # Calculate MACD using pandas-ta
    # df.ta.macd(close=df['c'], append=True)
    # print(df.tail(1))
    return df.tail(1)

def stock_data(request):
    ticker = 'AAPL'  # Always display AAPL data
    # stock_info = get_previous_data(ticker)
    # temp_stock_info = get_today_data(ticker)

    context = {
        'ticker': ticker,
        'stock_info': stock_info,
    }
    return render(request, 'stock_data.html', context)

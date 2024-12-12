from tradingview_ta import TA_Handler, Interval, TradingView
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from ..models import Stock_List, StockData
import os
from django.conf import settings
from googleapiclient.discovery import build
from google.oauth2 import service_account
from .helper import helper


# Path to your Service Account JSON file
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'StockViewerApp', 'static', 'StockViewerApp', 'json', 'credentials.json')

# Scopes required by the API (in this case, reading and writing to Google Sheets)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID of your spreadsheet (get it from the URL of the Google Sheet)
# SPREADSHEET_ID = '1t1j18sULoxu_yPIP4mmN2zOrANC--un6k9iGHB2E3Zo'
SPREADSHEET_ID = '1Cv3fYqNMapymGytbBULjT6Tc3BDISp5SfmmJbhEaZTE'



def read_stocks_data():
    # Authenticate and initialize the Sheets API service
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Define the range of data to read (entire "Stocks" tab)
    range_name = 'Stocks'  # Assuming the tab name is "Stocks"

    
    try:
        for tab in ["Stocks", "Crypto"]:
            range_name = f'{tab}'  # Specify the tab name
            result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
            print(result)
            values = result.get('values', [])

            if values:
                data = values[1:]  # Remaining rows as data
                for stocks in data:
                    helper.add_new_stocks(ticker=stocks[0], screener=stocks[1], exchange=stocks[2])
                
            else:
                print(f"No data found in the '{tab}' tab.")

    except Exception as e:
        print(f"An error occurred while reading the tabs: {e}")
        return None
    
def update_spreadsheet():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = spreadsheet.get('sheets', [])
    stock_list = Stock_List.objects.all()

    for stocks in stock_list:
        tab_exists = False
        tab_id = None
        for sheet in sheets:
            if sheet['properties']['title'] == stocks.ticker:
                tab_exists = True
                tab_id = sheet['properties']['sheetId']
                break
        
        if not tab_exists:
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': stocks.ticker
                    }
                }
            }]
            service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': requests}).execute()
            range_name = f'{stocks.ticker}!A1'
        
            values = [['date', 'price', 'resistance', 'support', 'support/resistance score', 'ma', 'ma score', 'macd 1d', 'macd 1d velocity', 'macd 1d score', 'macd 1w', 'macd 1w velocity', 'macd 1w score', 'total score', 'direction']]  # The value to write to the cell
            # Prepare the body of the request
            body = {
                'values': values
            }
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range=range_name,
                valueInputOption='RAW', body=body).execute()
        
        range_name = f'{stocks.ticker}!A2' 
        recent_stock_data = StockData.objects.filter(stock_list=stocks).order_by('-date')

        values = helper.get_total_score(recent_stock_data)
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=range_name,
            valueInputOption='RAW', body=body).execute()
    return

def update_database():
    pst_timezone = pytz.timezone('America/Los_Angeles')
    start_time = datetime.now(pst_timezone).replace(hour=6, minute=30, second=0, microsecond=0).astimezone(pytz.UTC)
    end_time = datetime.now(pst_timezone).replace(hour=16, minute=0, second=0, microsecond=0).astimezone(pytz.UTC)
    current_date = datetime.now(pst_timezone).astimezone(pytz.UTC)
    stock_list = Stock_List.objects.all()
    timeout = None
    for stock in stock_list:
        daily_stock_analysis = helper.get_stock_data(stock.ticker, stock.exchange, stock.screener, Interval.INTERVAL_1_DAY, timeout)
        weekly_stock_analysis = helper.get_stock_data(stock.ticker, stock.exchange, stock.screener, Interval.INTERVAL_1_WEEK, timeout)
        prev_stock_data = StockData.objects.filter(
            stock_list=stock,
        ).order_by('-date').first()            
        support = prev_stock_data.support if prev_stock_data else daily_stock_analysis['Pivot.M.Classic.S1']
        resistance = prev_stock_data.resistance if prev_stock_data else daily_stock_analysis['Pivot.M.Classic.R1']

        if(stock.screener == "crypto"):
            helper.create_new_database_entry(daily_stock_analysis, weekly_stock_analysis, current_date, support, resistance, stock, prev_stock_data)
            print(f"Added new StockData for {stock.ticker} on {current_date}")
        else:
            # If we are updating database during trading hours
            if start_time <= current_date <= end_time:
                helper.create_new_database_entry(daily_stock_analysis, weekly_stock_analysis, current_date, support, resistance, stock, prev_stock_data)
                print(f"Added new StockData for {stock.ticker} on {current_date}")
            # If we are updating database not during trading hours
            else:
                if prev_stock_data and prev_stock_data.date.date() == current_date.date():
                    helper.update_database_entry(prev_stock_data, daily_stock_analysis, weekly_stock_analysis, support, resistance, stock)
                    print(f"Updated StockData for {stock.ticker} on {current_date}")
                else:
                    helper.create_new_database_entry(daily_stock_analysis, weekly_stock_analysis, current_date, support, resistance, stock, prev_stock_data)
                    print(f"Added new StockData for {stock.ticker} on {current_date}")
    return
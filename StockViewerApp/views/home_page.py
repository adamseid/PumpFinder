from django.shortcuts import render
from datetime import datetime, timedelta
from tradingview_ta import TA_Handler, Interval, Exchange
from ..models import Stock_List
from .update_database_spreadsheet import update_database, update_spreadsheet, read_stocks_data



def update_database_spreadsheet():
    # update_database()
    update_spreadsheet()
    # read_stocks_data()

def home_page(request):
    stock_list = Stock_List.objects.exclude(screener="crypto")
    crypto_list = Stock_List.objects.filter(screener="crypto")
    # Check if the 'Update Spreadsheet' button was clicked
    if request.method == 'GET' and 'update_database_spreadsheet' in request.GET:
        update_database_spreadsheet()
    context = {
        'stock_list': stock_list,
        'crypto_list': crypto_list
    }

    return render(request, 'home_page.html', context)

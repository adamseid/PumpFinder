from django.shortcuts import render
from datetime import datetime, timedelta
from tradingview_ta import TA_Handler, Interval, Exchange
from ..models import Stock_List, StockData
from .update_database_spreadsheet import update_database, update_spreadsheet, read_stocks_data
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt  # For bypassing CSRF on AJAX requests if needed
from django.http import JsonResponse
from django.template.loader import render_to_string
from decimal import Decimal, ROUND_HALF_UP

def round_significant(num, sig_digits=3):
    if num is None:
        return num
    elif num > 1 or num < -1:
        return round(num, sig_digits)
    elif num == 0:
        return round(num)
    else:
        return round(num, sig_digits)

def home_page(request):
    if request.method == 'GET' and 'update_stock_list' in request.GET:
        read_stocks_data()
    
    if request.method == 'GET' and 'update_database' in request.GET:
        update_database()

    if request.method == 'GET' and 'update_spreadsheet' in request.GET:
        update_spreadsheet()

    sort_field = request.GET.get('sort', "-total_score")
    most_recent_stock_data = (
        StockData.objects.filter(
            date__in=StockData.objects.values('stock_list').annotate(latest_date=Max('date')).values_list('latest_date', flat=True)
        )
        .select_related('stock_list')  
        .order_by(sort_field)  
    )
# stock_data.price_change = round_significant(stock_data.price_change) 
    for stock_data in most_recent_stock_data:
        stock_data.total_score = round_significant(stock_data.total_score)  
        stock_data.current_price = round_significant(stock_data.current_price)  
        stock_data.daily_profit = round_significant(stock_data.current_price * (stock_data.price_change/100))
        stock_data.daily_return = round_significant((stock_data.current_price *  (stock_data.price_change/100)) / (stock_data.current_price *  (stock_data.price_change/100) + stock_data.current_price))
        stock_data.support_resistance_score = round_significant(stock_data.support_resistance_score)  
        stock_data.kinematics_score = 0
        stock_data.five_day_velocity_score = 0
        stock_data.five_day_accelaration_score = 0
        stock_data.daily_macd_velocity = round_significant(stock_data.daily_macd_velocity)  
        stock_data.daily_macd_score = round_significant(stock_data.daily_macd_score) 
        stock_data.weekly_macd_velocity = round_significant(stock_data.weekly_macd_velocity) 
        stock_data.weekly_macd_score = round_significant(stock_data.weekly_macd_score) 
        total_ma_score =  stock_data.ma_50d_score + stock_data.ma_100d_score + stock_data.ma_200d_score
        stock_data.ma_50d_score = round_significant(stock_data.ma_50d_score)  
        stock_data.ma_100d_score = round_significant(stock_data.ma_100d_score)  
        stock_data.ma_200d_score = round_significant(stock_data.ma_200d_score)  
        stock_data.ma_score = round_significant(total_ma_score)   

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Handle AJAX requests
        table_html = render_to_string('_stock_table.html', {'stock_list': most_recent_stock_data})
        return JsonResponse({'table_html': table_html})

    context = {
        'stock_list': most_recent_stock_data,
    }

    return render(request, 'home_page.html', context)

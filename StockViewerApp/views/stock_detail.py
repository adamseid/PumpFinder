from django.shortcuts import render, get_object_or_404
from ..models import Stock_List, StockData
import math

def round_significant(num, sig_figs=2):
    return num
    """
    Rounds a number to the specified number of significant figures.
    """
    if num is None:
        return None
    try:
        num = float(num)
        if num == 0:
            return 0
        order_of_magnitude = math.floor(math.log10(abs(num)))
        scale_factor = 10 ** (sig_figs - 1 - order_of_magnitude)
        return round(num * scale_factor) / scale_factor
    except (ValueError, TypeError):
        return num  # Return the original if conversion fails

def stock_detail(request, ticker):
    stock = get_object_or_404(Stock_List, ticker=ticker)
    
    stock_data_queryset = StockData.objects.filter(stock_list=stock).order_by('-date')
    
    # Round numerical fields to 2 significant figures
    stock_data = []
    for data in stock_data_queryset:
        stock_data.append({
            'id': data.id,
            'date': data.date,
            'current_price': round_significant(data.close),
            'resistance': round_significant(data.resistance),
            'support': round_significant(data.support),
            'support_resistance_score': round_significant(data.support_resistance_score),
            'sma_200': round_significant(data.sma_200),
            'ma_score': round_significant(data.ma_score),
            'daily_macd_histogram': round_significant(data.daily_macd_histogram),
            'daily_macd_velocity': round_significant(data.daily_macd_velocity),
            'daily_macd_score': round_significant(data.daily_macd_score),
            'weekly_macd_histogram': round_significant(data.weekly_macd_histogram),
            'weekly_macd_velocity': round_significant(data.weekly_macd_velocity),
            'weekly_macd_score': round_significant(data.weekly_macd_score),
            'total_score': round_significant(data.total_score),
            'direction': round_significant(data.direction),
            'exchange': stock.exchange
        })

    return render(request, 'stock_detail.html', {'stock': stock, 'stock_data': stock_data})

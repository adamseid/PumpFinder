from django.shortcuts import render
from datetime import datetime, timedelta
import pytz
from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
from ..models import Stock_List, StockData

def get_stock_data(ticker, exchange, screener, interval, timeout):
    handler = TA_Handler(
        symbol= ticker,
        exchange= exchange,
        screener= screener,
        interval= interval,
        timeout= timeout
    )

    analysis = handler.get_analysis()

    return analysis

def stock_data(request):
    pst_timezone = pytz.timezone('America/Los_Angeles')
    current_date = datetime.now(pst_timezone).strftime('%Y-%m-%d')
    stock_list = Stock_List.objects.all()
    timeout = None
    for stock in stock_list:
        daily_stock_analysis = get_stock_data(stock.ticker, stock.exchange, stock.screener, Interval.INTERVAL_1_DAY, timeout)
        weekly_stock_analysis = get_stock_data(stock.ticker, stock.exchange, stock.screener, Interval.INTERVAL_1_WEEK, timeout)
    
    for stock in Stock_List.objects.all():
        daily_stock_analysis = get_stock_data(stock.ticker, stock.exchange, stock.screener, Interval.INTERVAL_1_DAY, timeout)
        weekly_stock_analysis = get_stock_data(stock.ticker, stock.exchange, stock.screener, Interval.INTERVAL_1_WEEK, timeout)

        stock_data = StockData.objects.filter(date=current_date, stock_list=stock).first()

        if stock_data:
            # If the StockData entry exists, update it
            stock_data.open = daily_stock_analysis.indicators['open']
            stock_data.close = daily_stock_analysis.indicators['close']
            stock_data.high = daily_stock_analysis.indicators['high']
            stock_data.low = daily_stock_analysis.indicators['low']
            stock_data.volume = daily_stock_analysis.indicators['volume']
            stock_data.sma_200 = daily_stock_analysis.indicators['SMA200']
            stock_data.daily_macd_line = daily_stock_analysis.indicators['MACD.macd']
            stock_data.daily_macd_signal = daily_stock_analysis.indicators['MACD.signal']
            stock_data.daily_macd_histogram = daily_stock_analysis.indicators['MACD.macd'] - daily_stock_analysis.indicators['MACD.signal']
            stock_data.weekly_macd_line = weekly_stock_analysis.indicators['MACD.macd']
            stock_data.weekly_macd_signal = weekly_stock_analysis.indicators['MACD.signal']
            stock_data.weekly_macd_histogram = weekly_stock_analysis.indicators['MACD.macd'] - weekly_stock_analysis.indicators['MACD.signal']
            stock_data.rsi = daily_stock_analysis.indicators['RSI']
            stock_data.save()  # Save the updated record
            print(f"Updated StockData for {stock.ticker} on {current_date}")
        else:
            # If no entry exists, create a new StockData entry
            new_stock_data = StockData(
                date=current_date,
                open=daily_stock_analysis.indicators['open'],
                close=daily_stock_analysis.indicators['close'],
                high=daily_stock_analysis.indicators['high'],
                low=daily_stock_analysis.indicators['low'],
                volume=daily_stock_analysis.indicators['volume'],
                sma_200=daily_stock_analysis.indicators['SMA200'],
                daily_macd_line=daily_stock_analysis.indicators['MACD.macd'],
                daily_macd_signal=daily_stock_analysis.indicators['MACD.signal'],
                daily_macd_histogram=daily_stock_analysis.indicators['MACD.macd'] - daily_stock_analysis.indicators['MACD.signal'],
                weekly_macd_line=weekly_stock_analysis.indicators['MACD.macd'],
                weekly_macd_signal=weekly_stock_analysis.indicators['MACD.signal'],
                weekly_macd_histogram=weekly_stock_analysis.indicators['MACD.macd'] - weekly_stock_analysis.indicators['MACD.signal'],
                rsi=daily_stock_analysis.indicators['RSI'],
                stock_list=stock  # ForeignKey relationship
            )
            new_stock_data.save()  # Save the new record
            print(f"Added new StockData for {stock.ticker} on {current_date}")

    context = {
        'stock_list': stock_list,
    }
    return render(request, 'all_stock_data.html', context)

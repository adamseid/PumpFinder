from ...models import Stock_List, StockData
from tradingview_ta import TA_Handler, Interval, TradingView


def get_stock_data(ticker, exchange, screener, interval, timeout):
    handler = TA_Handler(
        symbol= ticker,
        exchange= exchange,
        screener= screener,
        interval= interval,
        timeout= timeout
    )
    try:
        analysis = handler.get_analysis()
        return analysis
    except Exception as e:
        print(f"Error when fetching {ticker}: {str(e)}")
        return None

def add_new_stocks(ticker, screener, exchange, name=None, category=None, sector=None, industry=None, image_url=None):

    if not Stock_List.objects.filter(ticker=ticker).exists():
        new_stock = Stock_List(
            ticker=ticker,
            screener=screener,
            exchange=exchange,
            name=name,
            category=category,
            sector=sector,
            industry=industry,
            image_url=image_url,
        )
        new_stock.save()
    
    return

def re_adjust_support_resistance(stock, support, resistance, current_price):
    previous_support_resistance = StockData.objects.filter(
        stock_list=stock,
        support__lt=current_price,  # Support is less than current price
        resistance__gt=current_price  # Resistance is greater than current price
    ).exclude(
        support=support,
        resistance=resistance
    ).order_by('-date').first()
    if previous_support_resistance:
        return previous_support_resistance
    return None

def get_support_resistance_score(support, resistance , price, stock):
    if support is None or resistance is None:
        return 0

    if price >  resistance:
        return 2
    elif price < support:
        return -2

    # Get all StockData entries for the specific stock, ordered by date (most recent first)
    support_resistance_broken = StockData.objects.filter(
        stock_list=stock
    ).exclude(
        support=support,
        resistance=resistance
    ).filter(
        support__isnull=False,
        resistance__isnull=False
    ).order_by('-date').first()


    if support_resistance_broken:
        if support_resistance_broken.support == resistance:
            return -2
        elif support_resistance_broken.resistance == support:
            return 2
    return 0

def get_ma_score(ma , price):
    if ma is None:
        return 0
    if price > ma:
        return 1
    elif price < ma:
        return -1
    return 0

def get_macd_velocity(Macd, prev_Macd):
    previous_macd = prev_Macd.daily_macd_histogram
    return float(Macd) - float(previous_macd)

def get_macd_score(Macd, MacdVelocity):
    if float(Macd) > 0 and MacdVelocity > 0:
        return 2
    elif float(Macd) < 0 and MacdVelocity < 0:
        return -2
    return 0

def get_current_price(close, high, low):
    return ((close + high + low)/3)

def get_total_score(stock_data):
    total_score_array = []
    for stock in stock_data:
        date = stock.date.strftime('%Y-%m-%d %H:%M')
        price = float(stock.close)
        resistance = (stock.resistance)
        support = (stock.support)
        if support and resistance is not None:
            support = float(support)
            resistance = float(resistance)
        elif resistance is not None:
            resistance = float(resistance)
            support = "N/A"
        elif support is not None:
            support = float(support)
            resistance = "N/A"
        else:
            support = "N/A"
            resistance = "N/A"

        support_resistance_score = "N/A"
        ma_score = "N/A"
        ma = float(stock.sma_200)
        daily_macd_velocity = "N/A"
        daily_macd_score = "N/A"
        weekly_macd_velocity = "N/A"
        weekly_macd_score = "N/A"
        total_score = "N/A"
        direction = "N/A"
        daily_macd = float(stock.daily_macd_histogram)
        weekly_macd = float(stock.weekly_macd_histogram)

        if stock.support_resistance_score is not None:
            support_resistance_score = float(stock.support_resistance_score)
        if stock.ma_score is not None:
            ma_score = float(stock.ma_score)
        if stock.daily_macd_velocity is not None:
            daily_macd_velocity = float(stock.daily_macd_velocity)
        if stock.daily_macd_score is not None:
            daily_macd_score = float(stock.daily_macd_score)
        if stock.weekly_macd_velocity is not None:
            weekly_macd_velocity = float(stock.weekly_macd_velocity)
        if stock.weekly_macd_score is not None:
            weekly_macd_score = float(stock.weekly_macd_score)
        if stock.total_score is not None:
            total_score = float(stock.total_score)
        if stock.direction is not None:
            direction = float(stock.direction)
        
        total_score_array.append([date, price, resistance, support, support_resistance_score, ma, 
            ma_score, daily_macd, daily_macd_velocity, daily_macd_score, weekly_macd, 
            weekly_macd_velocity, weekly_macd_score, total_score, direction])
    return total_score_array

def create_new_database_entry(daily_stock_analysis, weekly_stock_analysis, current_date, support, resistance, stock, prev_stock_data):
    # current_price = get_current_price(daily_stock_analysis.indicators['close'], daily_stock_analysis.indicators['high'], daily_stock_analysis.indicators['low'])
    
    current_price = daily_stock_analysis.indicators['close']
    support_resistance_score = get_support_resistance_score(support, resistance , current_price, stock)
    if support_resistance_score == 2 or support_resistance_score == -2:
        support =  daily_stock_analysis.indicators['Pivot.M.Classic.S1']
        resistance =  daily_stock_analysis.indicators['Pivot.M.Classic.R1']
    ma_100d_score = get_ma_score(daily_stock_analysis.indicators['SMA100'] , current_price)
    ma_200d_score  = get_ma_score(daily_stock_analysis.indicators['SMA200'] , current_price)
    ma_50d_score  = get_ma_score(daily_stock_analysis.indicators['SMA50'] , current_price)
    daily_Macd = daily_stock_analysis.indicators['MACD.macd'] - daily_stock_analysis.indicators['MACD.signal']
    weekly_Macd = weekly_stock_analysis.indicators['MACD.macd'] - weekly_stock_analysis.indicators['MACD.signal']
    daily_macd_velocity = None
    weekly_macd_velocity = None
    daily_macd_score = None
    weekly_macd_score = None
    direction = None
    total_score = None
    if prev_stock_data is not None:
        daily_macd_velocity = get_macd_velocity(daily_Macd, prev_stock_data)
        weekly_macd_velocity = get_macd_velocity(weekly_Macd, prev_stock_data)
        daily_macd_score = get_macd_score(daily_Macd, daily_macd_velocity)
        weekly_macd_score = get_macd_score(weekly_Macd, weekly_macd_velocity)
        total_score = support_resistance_score + ma_50d_score + ma_100d_score + ma_200d_score + daily_macd_score + weekly_macd_score
        if total_score > 4:
            direction = 2
        elif total_score > 2:
            direction = 1
        elif total_score < -2:
            direction = -1
        elif total_score < -4:
            direction = -2
        else:
            direction = 0

    new_stock_data = StockData(
        date=current_date,
        recommend_all = daily_stock_analysis.indicators['Recommend.Other'],
        recommend_ma = daily_stock_analysis.indicators['Recommend.All'],
        recommend_other = daily_stock_analysis.indicators['Recommend.MA'],
        rsi = daily_stock_analysis.indicators['RSI'],
        yesterday_rsi = daily_stock_analysis.indicators['RSI[1]'],
        stoch_k = daily_stock_analysis.indicators['Stoch.K'],
        stoch_d =  daily_stock_analysis.indicators['Stoch.D'],
        yesterday_stoch_k = daily_stock_analysis.indicators['Stoch.K[1]'],
        yesterday_stoch_d =  daily_stock_analysis.indicators['Stoch.D[1]'],
        commodity_channel_index = daily_stock_analysis.indicators['CCI20'],
        yesterday_commodity_channel_index = daily_stock_analysis.indicators['CCI20[1]'], 
        adx = daily_stock_analysis.indicators['ADX'], 
        adx_di_positive = daily_stock_analysis.indicators['ADX+DI'],
        adx_di_negative = daily_stock_analysis.indicators['ADX-DI'],
        yesterday_adx_di_positive = daily_stock_analysis.indicators['ADX+DI[1]'],
        yesterday_adx_di_negative = daily_stock_analysis.indicators['ADX-DI[1]'],
        awesome_oscillator = daily_stock_analysis.indicators['AO'],
        yesterday_awesome_oscillator = daily_stock_analysis.indicators['AO[1]'],
        two_days_ago_awesome_oscillator = daily_stock_analysis.indicators['AO[2]'],
        momentum = daily_stock_analysis.indicators['Mom'],
        yesterday_momentum = daily_stock_analysis.indicators['Mom[1]'],
        daily_macd_line=daily_stock_analysis.indicators['MACD.macd'],
        daily_macd_signal=daily_stock_analysis.indicators['MACD.signal'],
        daily_macd_histogram=daily_stock_analysis.indicators['MACD.macd'] - daily_stock_analysis.indicators['MACD.signal'],
        weekly_macd_line=weekly_stock_analysis.indicators['MACD.macd'],
        weekly_macd_signal=weekly_stock_analysis.indicators['MACD.signal'],
        weekly_macd_histogram=weekly_stock_analysis.indicators['MACD.macd'] - weekly_stock_analysis.indicators['MACD.signal'],
        stoch_rsi = daily_stock_analysis.indicators['Stoch.RSI.K'],
        stoch_rsi_k = daily_stock_analysis.indicators['Stoch.RSI.K'],
        williams_r_recommendation = daily_stock_analysis.indicators['Rec.WR'],
        williams_r = daily_stock_analysis.indicators['W.R'],
        bollinger_bands_recommendation = daily_stock_analysis.indicators['Rec.BBPower'],
        bollinger_bands_power = daily_stock_analysis.indicators['BBPower'],
        bollinger_bands_lower = daily_stock_analysis.indicators['BB.lower'],
        bollinger_bands_upper = daily_stock_analysis.indicators['BB.upper'],
        ultimate_oscillator_recommendation = daily_stock_analysis.indicators['Rec.UO'],
        ultimate_oscillator = daily_stock_analysis.indicators['UO'],
        ema_5 = daily_stock_analysis.indicators['EMA5'],
        ema_10 = daily_stock_analysis.indicators['EMA10'],
        ema_20 = daily_stock_analysis.indicators['EMA20'],
        ema_30 = daily_stock_analysis.indicators['EMA30'],
        ema_50 = daily_stock_analysis.indicators['EMA50'],
        ema_100 = daily_stock_analysis.indicators['EMA100'],
        ema_200 = daily_stock_analysis.indicators['EMA200'],
        sma_5 = daily_stock_analysis.indicators['SMA5'],
        sma_10 = daily_stock_analysis.indicators['SMA10'],
        sma_20 = daily_stock_analysis.indicators['SMA20'],
        sma_30 = daily_stock_analysis.indicators['SMA30'],
        sma_50 = daily_stock_analysis.indicators['SMA50'],
        sma_100 = daily_stock_analysis.indicators['SMA100'],
        sma_200 = daily_stock_analysis.indicators['SMA200'],
        ichimoku_recommendation = daily_stock_analysis.indicators['Rec.Ichimoku'],
        ichimoku_base_line = daily_stock_analysis.indicators['Ichimoku.BLine'],
        volume_weighted_moving_average_recommendation = daily_stock_analysis.indicators['Rec.VWMA'],
        volume_weighted_moving_average = daily_stock_analysis.indicators['VWMA'],
        hull_moving_average_recommendation = daily_stock_analysis.indicators['Rec.HullMA9'],
        hull_moving_average = daily_stock_analysis.indicators['HullMA9'],
        pivot_classic_s3 = daily_stock_analysis.indicators['Pivot.M.Classic.S3'],
        pivot_classic_s2 = daily_stock_analysis.indicators['Pivot.M.Classic.S2'],
        pivot_classic_s1 = daily_stock_analysis.indicators['Pivot.M.Classic.S1'],
        pivot_classic_middle = daily_stock_analysis.indicators['Pivot.M.Classic.Middle'],
        pivot_classic_r1 = daily_stock_analysis.indicators['Pivot.M.Classic.R1'],
        pivot_classic_r2 = daily_stock_analysis.indicators['Pivot.M.Classic.R2'],
        pivot_classic_r3 = daily_stock_analysis.indicators['Pivot.M.Classic.R3'],
        pivot_fibonacci_s3 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.S3'],
        pivot_fibonacci_s2 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.S2'],
        pivot_fibonacci_s1 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.S1'],
        pivot_fibonacci_middle = daily_stock_analysis.indicators['Pivot.M.Fibonacci.Middle'],
        pivot_fibonacci_r1 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.R1'],
        pivot_fibonacci_r2 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.R2'],
        pivot_fibonacci_r3 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.R3'],
        pivot_camarilla_s3 = daily_stock_analysis.indicators['Pivot.M.Camarilla.S3'],
        pivot_camarilla_s2 = daily_stock_analysis.indicators['Pivot.M.Camarilla.S2'],
        pivot_camarilla_s1 = daily_stock_analysis.indicators['Pivot.M.Camarilla.S1'],
        pivot_camarilla_middle = daily_stock_analysis.indicators['Pivot.M.Camarilla.Middle'],
        pivot_camarilla_r1 = daily_stock_analysis.indicators['Pivot.M.Camarilla.R1'],
        pivot_camarilla_r2 = daily_stock_analysis.indicators['Pivot.M.Camarilla.R2'],
        pivot_camarilla_r3 = daily_stock_analysis.indicators['Pivot.M.Camarilla.R3'],
        pivot_woodie_s3 = daily_stock_analysis.indicators['Pivot.M.Woodie.S3'],
        pivot_woodie_s2 = daily_stock_analysis.indicators['Pivot.M.Woodie.S2'],
        pivot_woodie_s1 = daily_stock_analysis.indicators['Pivot.M.Woodie.S1'],
        pivot_woodie_middle = daily_stock_analysis.indicators['Pivot.M.Woodie.Middle'],
        pivot_woodie_r1 = daily_stock_analysis.indicators['Pivot.M.Woodie.R1'],
        pivot_woodie_r2 = daily_stock_analysis.indicators['Pivot.M.Woodie.R2'],
        pivot_woodie_r3 = daily_stock_analysis.indicators['Pivot.M.Woodie.R3'],
        pivot_demark_s1 = daily_stock_analysis.indicators['Pivot.M.Demark.S1'],
        pivot_demark_middle = daily_stock_analysis.indicators['Pivot.M.Demark.Middle'],
        pivot_demark_r1 = daily_stock_analysis.indicators['Pivot.M.Demark.R1'],
        parabolic_sar = daily_stock_analysis.indicators['P.SAR'],
        price_change = daily_stock_analysis.indicators['change'],
        open=daily_stock_analysis.indicators['open'],
        close=daily_stock_analysis.indicators['close'],
        high=daily_stock_analysis.indicators['high'],
        low=daily_stock_analysis.indicators['low'],
        volume=daily_stock_analysis.indicators['volume'],        
        support = support,
        resistance = resistance,
        current_price = current_price,
        support_resistance_score = support_resistance_score,
        ma_100d_score  = ma_100d_score,
        ma_200d_score  = ma_200d_score,
        ma_50d_score = ma_50d_score,
        daily_macd_velocity = daily_macd_velocity,
        daily_macd_score = daily_macd_score,
        weekly_macd_velocity = weekly_macd_velocity,
        weekly_macd_score = weekly_macd_score,        
        total_score = total_score,
        direction = direction,
        stock_list=stock  # ForeignKey relationship
    )
    new_stock_data.save()  

def update_database_entry(prev_stock_data, daily_stock_analysis, weekly_stock_analysis, support, resistance, stock):
    # current_price = get_current_price(daily_stock_analysis.indicators['close'], daily_stock_analysis.indicators['high'], daily_stock_analysis.indicators['low'])
    current_price = daily_stock_analysis.indicators['close']
    support_resistance_score = get_support_resistance_score(support, resistance , current_price, stock)
    if support_resistance_score == 2 or support_resistance_score == -2:
        support =  daily_stock_analysis.indicators['Pivot.M.Classic.S1']
        resistance =  daily_stock_analysis.indicators['Pivot.M.Classic.R1']
    ma_100d_score = get_ma_score(daily_stock_analysis.indicators['SMA100'] , current_price)
    ma_200d_score  = get_ma_score(daily_stock_analysis.indicators['SMA200'] , current_price)
    ma_50d_score  = get_ma_score(daily_stock_analysis.indicators['SMA50'] , current_price)
    daily_Macd = daily_stock_analysis.indicators['MACD.macd'] - daily_stock_analysis.indicators['MACD.signal']
    weekly_Macd = weekly_stock_analysis.indicators['MACD.macd'] - weekly_stock_analysis.indicators['MACD.signal']
    daily_macd_velocity = get_macd_velocity(daily_Macd, prev_stock_data)
    weekly_macd_velocity = get_macd_velocity(weekly_Macd, prev_stock_data)
    daily_macd_score = get_macd_score(daily_Macd, daily_macd_velocity)
    weekly_macd_score = get_macd_score(weekly_Macd, weekly_macd_velocity)
    total_score = support_resistance_score + ma_100d_score + ma_200d_score + ma_50d_score  + daily_macd_score + weekly_macd_score
    direction = 0
    if total_score > 4:
        direction = 2
    elif total_score > 2:
        direction = 1
    elif total_score < -2:
        direction = -1
    elif total_score < -4:
        direction = -2
    else:
        direction = 0

    prev_stock_data.recommend_all = daily_stock_analysis.indicators['Recommend.Other']
    prev_stock_data.recommend_ma = daily_stock_analysis.indicators['Recommend.All']
    prev_stock_data.recommend_other = daily_stock_analysis.indicators['Recommend.MA']
    prev_stock_data.rsi = daily_stock_analysis.indicators['RSI']
    prev_stock_data.yesterday_rsi = daily_stock_analysis.indicators['RSI[1]']
    prev_stock_data.stoch_k = daily_stock_analysis.indicators['Stoch.K']
    prev_stock_data.stoch_d =  daily_stock_analysis.indicators['Stoch.D']
    prev_stock_data.yesterday_stoch_k = daily_stock_analysis.indicators['Stoch.K[1]']
    prev_stock_data.yesterday_stoch_d =  daily_stock_analysis.indicators['Stoch.D[1]']
    prev_stock_data.commodity_channel_index = daily_stock_analysis.indicators['CCI20']
    prev_stock_data.yesterday_commodity_channel_index = daily_stock_analysis.indicators['CCI20[1]']
    prev_stock_data.adx = daily_stock_analysis.indicators['ADX']
    prev_stock_data.adx_di_positive = daily_stock_analysis.indicators['ADX+DI']
    prev_stock_data.adx_di_negative = daily_stock_analysis.indicators['ADX-DI']
    prev_stock_data.yesterday_adx_di_positive = daily_stock_analysis.indicators['ADX+DI[1]']
    prev_stock_data.yesterday_adx_di_negative = daily_stock_analysis.indicators['ADX-DI[1]']
    prev_stock_data.awesome_oscillator = daily_stock_analysis.indicators['AO']
    prev_stock_data.yesterday_awesome_oscillator = daily_stock_analysis.indicators['AO[1]']
    prev_stock_data.two_days_ago_awesome_oscillator = daily_stock_analysis.indicators['AO[2]']
    prev_stock_data.momentum = daily_stock_analysis.indicators['Mom']
    prev_stock_data.yesterday_momentum = daily_stock_analysis.indicators['Mom[1]']
    prev_stock_data.daily_macd_line=daily_stock_analysis.indicators['MACD.macd']
    prev_stock_data.daily_macd_signal=daily_stock_analysis.indicators['MACD.signal']
    prev_stock_data.daily_macd_histogram=daily_stock_analysis.indicators['MACD.macd'] - daily_stock_analysis.indicators['MACD.signal']
    prev_stock_data.weekly_macd_line=weekly_stock_analysis.indicators['MACD.macd']
    prev_stock_data.weekly_macd_signal=weekly_stock_analysis.indicators['MACD.signal']
    prev_stock_data.weekly_macd_histogram=weekly_stock_analysis.indicators['MACD.macd'] - weekly_stock_analysis.indicators['MACD.signal']
    prev_stock_data.stoch_rsi = daily_stock_analysis.indicators['Stoch.RSI.K']
    prev_stock_data.stoch_rsi_k = daily_stock_analysis.indicators['Stoch.RSI.K']
    prev_stock_data.williams_r_recommendation = daily_stock_analysis.indicators['Rec.WR']
    prev_stock_data.williams_r = daily_stock_analysis.indicators['W.R']
    prev_stock_data.bollinger_bands_recommendation = daily_stock_analysis.indicators['Rec.BBPower']
    prev_stock_data.bollinger_bands_power = daily_stock_analysis.indicators['BBPower']
    prev_stock_data.bollinger_bands_lower = daily_stock_analysis.indicators['BB.lower']
    prev_stock_data.bollinger_bands_upper = daily_stock_analysis.indicators['BB.upper']
    prev_stock_data.ultimate_oscillator_recommendation = daily_stock_analysis.indicators['Rec.UO']
    prev_stock_data.ultimate_oscillator = daily_stock_analysis.indicators['UO']
    prev_stock_data.ema_5 = daily_stock_analysis.indicators['EMA5']
    prev_stock_data.ema_10 = daily_stock_analysis.indicators['EMA10']
    prev_stock_data.ema_20 = daily_stock_analysis.indicators['EMA20']
    prev_stock_data.ema_30 = daily_stock_analysis.indicators['EMA30']
    prev_stock_data.ema_50 = daily_stock_analysis.indicators['EMA50']
    prev_stock_data.ema_100 = daily_stock_analysis.indicators['EMA100']
    prev_stock_data.ema_200 = daily_stock_analysis.indicators['EMA200']
    prev_stock_data.sma_5 = daily_stock_analysis.indicators['SMA5']
    prev_stock_data.sma_10 = daily_stock_analysis.indicators['SMA10']
    prev_stock_data.sma_20 = daily_stock_analysis.indicators['SMA20']
    prev_stock_data.sma_30 = daily_stock_analysis.indicators['SMA30']
    prev_stock_data.sma_50 = daily_stock_analysis.indicators['SMA50']
    prev_stock_data.sma_100 = daily_stock_analysis.indicators['SMA100']
    prev_stock_data.sma_200 = daily_stock_analysis.indicators['SMA200']
    prev_stock_data.ichimoku_recommendation = daily_stock_analysis.indicators['Rec.Ichimoku']
    prev_stock_data.ichimoku_base_line = daily_stock_analysis.indicators['Ichimoku.BLine']
    prev_stock_data.volume_weighted_moving_average_recommendation = daily_stock_analysis.indicators['Rec.VWMA']
    prev_stock_data.volume_weighted_moving_average = daily_stock_analysis.indicators['VWMA']
    prev_stock_data.hull_moving_average_recommendation = daily_stock_analysis.indicators['Rec.HullMA9']
    prev_stock_data.hull_moving_average = daily_stock_analysis.indicators['HullMA9']
    prev_stock_data.pivot_classic_s3 = daily_stock_analysis.indicators['Pivot.M.Classic.S3']
    prev_stock_data.pivot_classic_s2 = daily_stock_analysis.indicators['Pivot.M.Classic.S2']
    prev_stock_data.pivot_classic_s1 = daily_stock_analysis.indicators['Pivot.M.Classic.S1']
    prev_stock_data.pivot_classic_middle = daily_stock_analysis.indicators['Pivot.M.Classic.Middle']
    prev_stock_data.pivot_classic_r1 = daily_stock_analysis.indicators['Pivot.M.Classic.R1']
    prev_stock_data.pivot_classic_r2 = daily_stock_analysis.indicators['Pivot.M.Classic.R2']
    prev_stock_data.pivot_classic_r3 = daily_stock_analysis.indicators['Pivot.M.Classic.R3']
    prev_stock_data.pivot_fibonacci_s3 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.S3']
    prev_stock_data.pivot_fibonacci_s2 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.S2']
    prev_stock_data.pivot_fibonacci_s1 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.S1']
    prev_stock_data.pivot_fibonacci_middle = daily_stock_analysis.indicators['Pivot.M.Fibonacci.Middle']
    prev_stock_data.pivot_fibonacci_r1 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.R1']
    prev_stock_data.pivot_fibonacci_r2 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.R2']
    prev_stock_data.pivot_fibonacci_r3 = daily_stock_analysis.indicators['Pivot.M.Fibonacci.R3']
    prev_stock_data.pivot_camarilla_s3 = daily_stock_analysis.indicators['Pivot.M.Camarilla.S3']
    prev_stock_data.pivot_camarilla_s2 = daily_stock_analysis.indicators['Pivot.M.Camarilla.S2']
    prev_stock_data.pivot_camarilla_s1 = daily_stock_analysis.indicators['Pivot.M.Camarilla.S1']
    prev_stock_data.pivot_camarilla_middle = daily_stock_analysis.indicators['Pivot.M.Camarilla.Middle']
    prev_stock_data.pivot_camarilla_r1 = daily_stock_analysis.indicators['Pivot.M.Camarilla.R1']
    prev_stock_data.pivot_camarilla_r2 = daily_stock_analysis.indicators['Pivot.M.Camarilla.R2']
    prev_stock_data.pivot_camarilla_r3 = daily_stock_analysis.indicators['Pivot.M.Camarilla.R3']
    prev_stock_data.pivot_woodie_s3 = daily_stock_analysis.indicators['Pivot.M.Woodie.S3']
    prev_stock_data.pivot_woodie_s2 = daily_stock_analysis.indicators['Pivot.M.Woodie.S2']
    prev_stock_data.pivot_woodie_s1 = daily_stock_analysis.indicators['Pivot.M.Woodie.S1']
    prev_stock_data.pivot_woodie_middle = daily_stock_analysis.indicators['Pivot.M.Woodie.Middle']
    prev_stock_data.pivot_woodie_r1 = daily_stock_analysis.indicators['Pivot.M.Woodie.R1']
    prev_stock_data.pivot_woodie_r2 = daily_stock_analysis.indicators['Pivot.M.Woodie.R2']
    prev_stock_data.pivot_woodie_r3 = daily_stock_analysis.indicators['Pivot.M.Woodie.R3']
    prev_stock_data.pivot_demark_s1 = daily_stock_analysis.indicators['Pivot.M.Demark.S1']
    prev_stock_data.pivot_demark_middle = daily_stock_analysis.indicators['Pivot.M.Demark.Middle']
    prev_stock_data.pivot_demark_r1 = daily_stock_analysis.indicators['Pivot.M.Demark.R1']
    prev_stock_data.parabolic_sar = daily_stock_analysis.indicators['P.SAR']
    prev_stock_data.price_change = daily_stock_analysis.indicators['change']
    prev_stock_data.open=daily_stock_analysis.indicators['open']
    prev_stock_data.close=daily_stock_analysis.indicators['close']
    prev_stock_data.high=daily_stock_analysis.indicators['high']
    prev_stock_data.low=daily_stock_analysis.indicators['low']
    prev_stock_data.volume=daily_stock_analysis.indicators['volume']
    prev_stock_data.support = support
    prev_stock_data.resistance = resistance
    prev_stock_data.current_price = current_price
    prev_stock_data.support_resistance_score = support_resistance_score
    prev_stock_data.ma_100d_score  = ma_100d_score
    prev_stock_data.ma_200d_score  = ma_200d_score
    prev_stock_data.ma_50d_score = ma_50d_score
    prev_stock_data.daily_macd_velocity = daily_macd_velocity
    prev_stock_data.daily_macd_score = daily_macd_score
    prev_stock_data.weekly_macd_velocity = weekly_macd_velocity
    prev_stock_data.weekly_macd_score = weekly_macd_score       
    prev_stock_data.total_score = total_score
    prev_stock_data.direction = direction
    prev_stock_data.save()  # Save the updated record 
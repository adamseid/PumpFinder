from django.db import models

class Stock_List(models.Model):
    ticker = models.CharField(max_length=200)
    name = models.CharField(max_length=200, blank=True, null=True) 
    screener = models.CharField(max_length=200)
    exchange = models.CharField(max_length=200)
    category = models.CharField(max_length=200 , null=True,)
    sector = models.CharField(max_length=200 , null=True,)
    industry = models.CharField(max_length=200 , null=True,)
    image_url = models.CharField(max_length=500, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} ({self.exchange})"


class StockData(models.Model):
    stock_list = models.ForeignKey(
        Stock_List, 
        on_delete=models.CASCADE,  # Deletes related StockData when Stock_List is deleted
        related_name='stock_data'  # Enables reverse lookup: stock_list.stock_data.all()
    )
    date = models.DateTimeField()
    current_price = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    recommend_all = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    recommend_ma = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    recommend_other = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    rsi = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    yesterday_rsi = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    stoch_k = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    stoch_d =  models.DecimalField(max_digits=15, decimal_places=6, null=True)
    yesterday_stoch_k = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    yesterday_stoch_d =  models.DecimalField(max_digits=15, decimal_places=6, null=True)
    commodity_channel_index = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    yesterday_commodity_channel_index = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    adx = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    adx_di_positive = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    adx_di_negative = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    yesterday_adx_di_positive = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    yesterday_adx_di_negative = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    awesome_oscillator = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    yesterday_awesome_oscillator = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    two_days_ago_awesome_oscillator = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    momentum = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    yesterday_momentum = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    daily_macd_line = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    daily_macd_signal = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    daily_macd_histogram = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    weekly_macd_line = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    weekly_macd_signal = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    weekly_macd_histogram = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    stoch_rsi = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    stoch_rsi_k = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    williams_r_recommendation = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    williams_r = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    bollinger_bands_recommendation = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    bollinger_bands_power = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    bollinger_bands_lower = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    bollinger_bands_upper = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ultimate_oscillator_recommendation = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ultimate_oscillator = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    close = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ema_5 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ema_10 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ema_20 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ema_30 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ema_50 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ema_100 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ema_200 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    sma_5 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    sma_10 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    sma_20 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    sma_30 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    sma_50 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    sma_100 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    sma_200 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ichimoku_recommendation = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ichimoku_base_line = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    volume_weighted_moving_average = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    volume_weighted_moving_average_recommendation = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    hull_moving_average = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    hull_moving_average_recommendation = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_classic_s3 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_classic_s2 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_classic_s1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_classic_middle = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_classic_r1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_classic_r2 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_classic_r3 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_fibonacci_s3 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_fibonacci_s2 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_fibonacci_s1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_fibonacci_middle = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_fibonacci_r1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_fibonacci_r2 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_fibonacci_r3 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_camarilla_s3 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_camarilla_s2 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_camarilla_s1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_camarilla_middle = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_camarilla_r1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_camarilla_r2 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_camarilla_r3 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_woodie_s3 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_woodie_s2 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_woodie_s1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_woodie_middle = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_woodie_r1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_woodie_r2 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_woodie_r3 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_demark_s1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_demark_middle = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    pivot_demark_r1 = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    parabolic_sar = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    open = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    volume = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    low = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    high = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    price_change = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    support = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    resistance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    support_resistance_score = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ma_100d_score = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    ma_200d_score = models.DecimalField(max_digits=15, decimal_places=6, null=True) 
    ma_50d_score = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    daily_macd_velocity = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    daily_macd_score = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    weekly_macd_velocity = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    weekly_macd_score = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    total_score = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    direction = models.DecimalField(max_digits=15, decimal_places=6, null=True)

    def __str__(self):
        return f"Data for {self.stock_list.ticker} on {self.date}"

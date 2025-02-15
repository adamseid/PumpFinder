# Generated by Django 5.1.3 on 2025-01-07 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "StockViewerApp",
            "0009_stockdata_current_price_stockdata_daily_macd_score_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="stockdata",
            old_name="ma_score",
            new_name="ma_200d_score",
        ),
        migrations.AddField(
            model_name="stockdata",
            name="ma_100d_score",
            field=models.DecimalField(decimal_places=6, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name="stockdata",
            name="ma_50d_score",
            field=models.DecimalField(decimal_places=6, max_digits=15, null=True),
        ),
    ]

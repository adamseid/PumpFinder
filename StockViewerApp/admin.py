from django.contrib import admin
from .models import Stock_List, StockData

# Register your models here.

admin.site.register(Stock_List)
admin.site.register(StockData)
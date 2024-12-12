from django.urls import path
from .views import home_page, stock_detail, update_stock_data

urlpatterns = [
    path('', home_page, name='home'), 
    path('stocks/<str:ticker>/', stock_detail, name='stock_detail'),  # Individual Stock Page
    path('update_stock_data/', update_stock_data, name='update_stock_data'),
]

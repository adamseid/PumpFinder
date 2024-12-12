from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # For bypassing CSRF on AJAX requests if needed
from ..models import StockData
import json

@csrf_exempt  
def update_stock_data(request):
    if request.method == 'POST':
        # Check if the request contains JSON data
        try:
            data = json.loads(request.body)
            stock_data_id = data['id']
            field = data['field']
            value = data['value']

            # Get the StockData object
            stock_data = StockData.objects.get(id=stock_data_id)
            # Update the appropriate field
            setattr(stock_data, field, value)
            stock_data.save()

            # Return a success response
            return JsonResponse({'status': 'success'})

        except KeyError:
            return JsonResponse({'status': 'error', 'message': 'Missing fields in request data'}, status=400)
        except StockData.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'StockData not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

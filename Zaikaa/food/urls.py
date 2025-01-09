from django.urls import path
from .views import home, confirm_order, process_order

urlpatterns = [
    path('', home, name='home'),
    path('confirm-order/', confirm_order, name='confirm_order'),
    path('process-order/', process_order, name='process_order'),
]

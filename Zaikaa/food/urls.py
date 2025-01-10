from django.urls import path
from .views import home, confirm_order, settinguporder, check_order_status, success, waiting, adminapproval, allorders, approve_order, past_orders_page, past_orders, stall_login, bookings, update_order_status


urlpatterns = [
    path('', home, name='home'),
    path('confirm-order/', confirm_order, name='confirm_order'),
    path('settinguporder/', settinguporder, name='settinguporder'),  # For order setup
    path('check_order_status/', check_order_status, name='check_order_status'),
    path('success/<int:token_id>/', success, name='success'),  # For success page
    path('waiting/',waiting, name='waiting'),
    path('adminapproval/', adminapproval, name='adminapproval'),
    path('approve_order/<int:order_id>/', approve_order, name='approve_order'),
    path('allorders/', allorders, name='allorders'),
    path('past_orders/api/', past_orders, name='past_orders_api'),  # Updated API URL
    path('past_orders/', past_orders_page, name='past_orders_page'),
    path('stall/login/', stall_login, name='stall_login'),
    path('stall/bookings/', bookings, name='bookings'),
    path('stall/update/<int:order_id>/status=<str:status>/', update_order_status, name='update_order_status'),
]

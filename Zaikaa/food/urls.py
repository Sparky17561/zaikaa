from django.urls import path
from .views import home, confirm_order, settinguporder, check_order_status, success, waiting, adminapproval, allorders, approve_order

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
]

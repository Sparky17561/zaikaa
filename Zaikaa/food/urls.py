from django.urls import path
from .views import  home , confirm_order, settinguporder, check_order_status, success, waiting, adminapproval, allorders, approve_order, payment_success_view, past_orders_page, past_orders, stall_login, bookings, update_order_status, admin_login, admin_panel , admin_logout, add_shop, delete_shop, shop_listing, toggle_availability, generate_order_id, ulogin, usignup, urnp, ulogout, toggle_menu
from django.conf.urls import handler404, handler500, handler403, handler400
from food.views import custom_404, custom_500, custom_403, custom_400  # Import custom error views
# Custom error handlers
handler404 = 'food.views.custom_404'
handler500 = 'food.views.custom_500'
handler403 = 'food.views.custom_403'
handler400 = 'food.views.custom_400'

urlpatterns = [

    path('', home, name='home'),
    path('confirm-order/', confirm_order, name='confirm_order'),
    path('settinguporder/', settinguporder, name='settinguporder'),  # For order setup
    path('check_order_status/', check_order_status, name='check_order_status'),
    path('success/<int:token_id>/', success, name='success'),  # For success page
    path('waiting/',waiting, name='waiting'),
    path('admin/approval/', adminapproval, name='adminapproval'),
    path('admin/approve_order/<int:order_id>/', approve_order, name='approve_order'),
    path('admin/allorders/', allorders, name='allorders'),
    path('past_orders/api/', past_orders, name='past_orders_api'),  # Updated API URL
    path('past_orders/', past_orders_page, name='past_orders_page'),
    path('stall/login/', stall_login, name='stall_login'),
    path('stall/bookings/', bookings, name='bookings'),
    path('stall/update/<int:order_id>/status=<str:status>/', update_order_status, name='update_order_status'),
    path('admin/login/', admin_login, name='admin_login'),
    path('admin/panel/', admin_panel, name='admin_panel'),
    path('admin/logout/', admin_logout, name='admin_logout'),
    path('admin/add_shop/', add_shop, name='add_shop'),
    path('admin/delete_shop/<int:shop_id>/', delete_shop, name='delete_shop'),
    path('admin/shop_listing/', shop_listing, name='shop_listing'),
    path('admin/toggle_availability/<int:item_id>/', toggle_availability, name='toggle_availability'),
    path('pay_online/', generate_order_id, name='generate_order_id'),
    path('payment-success/', payment_success_view, name='payment-success'),
    path("ulogin/",ulogin,name="ulogin"),
    path("usignup/",usignup,name="usignup"),
    path("ulogout/",ulogout,name="ulogout"),    
    path("urnp/",urnp,name="urnp"),
    path('stall/toggle/',toggle_menu, name="toggle_menu")
    

]

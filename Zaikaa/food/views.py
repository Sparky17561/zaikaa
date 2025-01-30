from django.shortcuts import redirect, render
from django.http import JsonResponse
import json
from datetime import datetime
import random
from django.views.decorators.csrf import csrf_exempt
import logging
from django.db import connection, transaction
from django.http import HttpResponse
import re
# Home view to display all stalls and handle item selection

def home(request):
    if request.user.is_authenticated:

        # Execute raw SQL query
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s.shop_id, 
                    s.shop_name, 
                    m.id AS item_id, 
                    m.name AS item_name, 
                    m.price, 
                    'Available' AS availability
                FROM 
                    shops s
                LEFT JOIN 
                    menuitems m ON s.shop_id = m.shop_id
                WHERE 
                    m.availability = 1  -- Availability column has 0 or 1
                ORDER BY 
                    s.shop_name, m.name;
            """)

            # Fetch all results
            rows = cursor.fetchall()

        # Format the results into a dictionary by shop
        shops = {}
        for row in rows:
            shop_id = row[0]
            shop_name = row[1]
            item_id = row[2]
            item_name = row[3]
            price = row[4]
            availability = row[5]

            if shop_name not in shops:
                shops[shop_name] = {'shop_id': shop_id, 'items': []}

            # Add items to the respective shop
            if item_name:  # Only add items if they exist
                shops[shop_name]['items'].append({
                    'item_id': item_id,
                    'item_name': item_name,
                    'price': price,
                    'availability': availability,
                    'shop_id': shop_id
                })

        # If the form is submitted, process selected items
        if request.method == 'POST':
            selected_items = request.POST.getlist('selected_items')
            formatted_items = []
            for item in selected_items:
                # Parse the JSON string correctly
                item_data = json.loads(item)
                formatted_items.append({
                    'item_name': item_data['item_name'],
                    'price': float(item_data['price']),
                    'shop_id': int(item_data['shop_id']),
                })
            # request.session.clear()
            # Store formatted items in the session
            request.session['selected_items'] = formatted_items
            
            # # Store user details in session
            request.session['user_name'] = request.POST.get('name')
            request.session['user_email'] = request.POST.get('email')
            request.session['user_phone'] = request.POST.get('phone')
            # Print the entire session to see what is stored
            print(f"Session keys: {list(request.session.keys())}")

            # Print the entire session dictionary
            print(f"Full session data: {dict(request.session)}")
            # Redirect to confirmation page
            return redirect('confirm_order')

        # Pass the data to the template
        return render(request, 'home.html', {'shops': shops})
    else:
            return redirect('ulogin')






def confirm_order(request):
    if request.user.is_authenticated:
        # Retrieve the selected items from the session
        selected_items = request.session.get('selected_items', [])
        user_name = request.session['user_name'] 
        user_email = request.session['user_email'] 
        user_phone = request.session['user_phone'] 
        # If no items are selected, redirect to the home page
        if not selected_items:
            return redirect('home')

        # Pass the selected items and user details to the template
        return render(request, 'food/confirm_order.html', {
            'selected_items': selected_items,
            'user_name' : user_name,
            'user_email' : user_email,
            'user_phone' : user_phone
        })
    else:
        return redirect('ulogin')


import json
import logging
import re
from datetime import datetime
from django.db import connection, transaction
from django.shortcuts import redirect
from django.http import HttpResponse

# Set up logging
logger = logging.getLogger(__name__)
import json

def settinguporder(request):
    # Get form data (from the form submitted)
    user_name = request.POST.get('name')
    user_email = request.POST.get('email')
    mobile = request.POST.get('phone')

    # Update session with the new user details
    request.session['user_name'] = user_name
    request.session['user_email'] = user_email
    request.session['user_mobile'] = mobile

    # Log session data for debugging
    print(f"Session keys: {list(request.session.keys())}")
    print(f"Full session data: {dict(request.session)}")

    # Get selected items from session
    selected_items = request.session.get('selected_items', [])

    # Extract shop IDs from selected items (ensure no duplicates)
    shop_ids = list(set(item['shop_id'] for item in selected_items))

    # Get total amount and order items
    total_amount = float(request.POST.get('total'))  # Get the total amount from the form
    
    order_items_str = request.POST.get('order_items')
    print(f"Order Items (raw): {order_items_str}")  # Log the raw order items data

    try:
        items = json.loads(order_items_str)  # Get a list of items from the form
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for order_items: {e}")
        return HttpResponse("Invalid order items data", status=400)

    # Print the data for debugging
    print(f"User Name: {user_name}")
    print(f"User Email: {user_email}")
    print(f"Mobile: {mobile}")
    print(f"Shop IDs (based on selected items): {shop_ids}")
    print(f"Total Amount: {total_amount}")
    print(f"Items: {items}")

    # Print the selected items for debugging
    print("Selected Items:")
    for item in selected_items:
        print(f"Item Name: {item['item_name']}, Shop ID: {item['shop_id']}, Price: ₹{item['price']}")

    try:
        with transaction.atomic():  # Start a transaction block
            # Query 1: Add user to the "users" table (if not already added)
            with connection.cursor() as cursor:
                cursor.execute(""" 
                    SELECT "user_id" FROM "users" WHERE "mobile" = %s OR "email" = %s;
                """, [mobile, user_email])
                result = cursor.fetchone()

                if result:
                    user_id = result[0]
                    print(f"User ID already exists: {user_id}")
                else:
                    cursor.execute(""" 
                        INSERT INTO "users" ("name", "email", "mobile")
                        VALUES (%s, %s, %s);
                    """, [user_name, user_email, mobile])
                    print("Executed INSERT into users table")
                    cursor.execute('SELECT LASTVAL();')  # PostgreSQL equivalent for getting last inserted ID
                    user_id = cursor.fetchone()[0]
                    print(f"User ID: {user_id}")

            # Query 2: Check if items are available before inserting into "orderlist"
            with connection.cursor() as cursor:
                for shop_id in shop_ids:
                    shop_items = [item for item in items if re.search(r'\(Shop ID: (\d+)\)', item['item_name']) and int(re.search(r'\(Shop ID: (\d+)\)', item['item_name']).group(1)) == shop_id]
                    
                    for item in shop_items:
                        item_name = item['item_name']
                        quantity = item['quantity']
                        price = float(item['price'])
                        
                        match = re.match(r'^(.*?) \(Shop ID: \d+\)$', item_name)
                        item_name_without_shop = match.group(1) if match else item_name
                        
                        cursor.execute(""" 
                            SELECT "availability" FROM "menuitems" WHERE "shop_id" = %s AND "name" = %s;
                        """, [shop_id, item_name_without_shop])
                        result = cursor.fetchone()
                        
                        if result:
                            availability = result[0]
                            if availability == 1:
                                total_price = quantity * price
                                cursor.execute(""" 
                                    INSERT INTO "orderlist" ("email", "name", "contact_no", "shop_id", "item_name", "qty", "total_amt", "status")
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                                """, [user_email, user_name, mobile, shop_id, item_name_without_shop, quantity, total_price, 'Pending'])
                                print(f"Executed INSERT into orderlist table: User ID = {user_id}, Shop ID = {shop_id}, Item = {item_name_without_shop}, Quantity = {quantity}, Price = {price}, Total Price = {total_price}")
                            else:
                                error_message = f"The item '{item_name_without_shop}' is unavailable at Shop ID {shop_id}. Please check availability or remove the item."
                                raise Exception(error_message)
                        else:
                            error_message = f"The item '{item_name_without_shop}' was not found in the menu at Shop ID {shop_id}. Please check availability or remove the item."
                            raise Exception(error_message)

        print("Order processing completed successfully")
        return redirect('waiting')  # Redirect to a waiting page for further processing

    except Exception as e:
        print(f"Error while processing the order: {e}")
        transaction.rollback()  # Rollback the transaction if an error occurs
        error_message = f"""
        An error occurred while processing your order. This could be because:
        1. The item you selected is unavailable.
        2. The item was not found in the menu.
        
        Please visit the homepage and try again. <br>
        <a href="http://127.0.0.1:8000/food/">Go to Homepage</a>
        """
        return HttpResponse(error_message, status=500)






import json
import logging
import random
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

# Set up logging
logger = logging.getLogger(__name__)

import json
from random import randint
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

@csrf_exempt
def check_order_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'status': 'error', 'message': 'Email not provided'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM "orderlist" 
                    WHERE "email" = %s AND "status" = 'Pending';
                """, [email])
                pending_count = cursor.fetchone()[0]

            if pending_count > 0:
                return JsonResponse({
                    'status': 'pending',
                    'message': f'{pending_count} item(s) still pending approval',
                    'pending_count': pending_count
                })

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM "orderlist"
                    WHERE "email" = %s AND "status" = 'Approved' AND "tokenid" IS NULL;
                """, [email])
                approved_count = cursor.fetchone()[0]

            if approved_count == 0:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'No approved items found for this email.',
                    'pending_count': pending_count
                })

            token_id = randint(1000, 9999)
            timestamp = datetime.now()

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE "orderlist"
                    SET "tokenid" = %s, "timestamp" = %s, "mode_of_payment" = 'cash'
                    WHERE "email" = %s AND "status" = 'Approved' AND "tokenid" IS NULL;
                """, [token_id, timestamp, email])

            return JsonResponse({
                'status': 'success',
                'message': 'Order approved',
                'token_id': token_id,
                'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'pending_count': pending_count
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)




def success(request, token_id):
    # You can check if the token ID exists in the database or its status here if needed
    # For now, we will just pass the token_id to the success page
    return render(request, 'food/success.html', {'token_id': token_id})

# views.py
def waiting(request):
    # Retrieve user_email from session or another source
    user_email = request.session.get('user_email')  # Assuming it's passed from the form
    print(f"User email from session: {user_email}")
    return render(request, 'food/waiting.html', {
        'user_email': user_email
    })




from django.shortcuts import render
from django.db import connection

def adminapproval(request):
    # Get all orders where the status is 'Pending'
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "order_id", "email", "name", "contact_no", "item_name", "qty", "total_amt" 
            FROM "orderlist" 
            WHERE "status" = 'Pending';
        """)
        pending_orders = cursor.fetchall()
    
    # Render the adminapproval.html template and pass pending orders
    return render(request, 'food/adminapproval.html', {'pending_orders': pending_orders})


from django.shortcuts import redirect
from django.db import connection

def approve_order(request, order_id):
    # Approve the order by updating its status to 'Approved'
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE "orderlist" 
            SET "status" = 'Approved' 
            WHERE "order_id" = %s;
        """, [order_id])
    
    return redirect('adminapproval')  # Redirect back to the admin approval page




from django.shortcuts import render
from django.db import connection

def allorders(request):
    # Get all orders from the database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "order_id", "email", "name", "contact_no", "item_name", "qty", "total_amt", "status"
            FROM "orderlist";
        """)
        all_orders = cursor.fetchall()

    # Render the allorders.html template and pass all orders
    return render(request, 'food/allorders.html', {'all_orders': all_orders})




logger = logging.getLogger(__name__)

import json
from datetime import datetime
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import logging

logger = logging.getLogger(__name__)

@csrf_protect
def past_orders(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "Email not provided"}, status=400)

            with connection.cursor() as cursor:
                # Fetch distinct token IDs, timestamp, mode_of_payment, and status for orders
                cursor.execute("""
                    SELECT DISTINCT "tokenid", "timestamp", "mode_of_payment"
                    FROM "orderlist"
                    WHERE "email" = %s AND "tokenid" IS NOT NULL
                    ORDER BY "timestamp" DESC;
                """, [email])
                tokens = cursor.fetchall()

            if not tokens:
                return JsonResponse({"orders": []}, status=200)

            orders = []
            for token_id, timestamp, mode_of_payment in tokens:
                logger.info(f"Fetching order for token_id: {token_id}")  # Log token_id

                with connection.cursor() as cursor:
                    # Fetch items and their statuses for each token
                    cursor.execute("""
                        SELECT s."shop_name", o."item_name", o."qty", o."total_amt", o."status"
                        FROM "orderlist" o
                        JOIN "shops" s ON o."shop_id" = s."shop_id"
                        WHERE o."tokenid" = %s;
                    """, [token_id])
                    items = cursor.fetchall()

                grand_total = sum(item[3] for item in items)
                orders.append({
                    "token_id": token_id,
                    "timestamp": timestamp.strftime("%d %B %Y, %I:%M %p") if isinstance(timestamp, datetime) else "Unknown Date",
                    "mode_of_payment": mode_of_payment,
                    "items": [
                        {
                            "shop_name": item[0],
                            "item_name": item[1],
                            "quantity": item[2],
                            "total_amount": item[3],
                            "status": item[4]  # Item-specific status
                        }
                        for item in items
                    ],
                    "grand_total": grand_total
                })

            return JsonResponse({"orders": orders}, status=200)

        except Exception as e:
            logger.error(f"Error fetching past orders: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



from django.shortcuts import render

from django.shortcuts import render, redirect

def past_orders_page(request):
    if request.user.is_authenticated:
        # Get user data from session
        user_email = request.session.get('user_email', '')
        user_name = request.session.get('user_name', '')
        user_phone = request.session.get('user_phone', '')

        # Pass data to the template
        return render(request, 'food/past_orders.html', {
            'user_email': user_email,
            'user_name': user_name,
            'user_phone': user_phone
        })
    
    # Ensure redirect always returns a response
    return redirect('ulogin')






from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def stall_login(request):
    if request.method == "POST":
        shop_id = request.POST.get('shop_id')
        passkey = request.POST.get('passkey')

        if not shop_id or not passkey:
            messages.error(request, "Shop ID and passkey are required.")
            return redirect('stall_login')

        # Check if the shop exists and the passkey is correct
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT "passkey" FROM "shops" WHERE "shop_id" = %s;
            """, [shop_id])
            result = cursor.fetchone()

        if result and result[0] == passkey:
            request.session['shop_id'] = shop_id  # Store shop_id in session
            return redirect('bookings')  # Redirect to the bookings page
        else:
            messages.error(request, "Invalid shop ID or passkey.")
            return redirect('stall_login')

    return render(request, 'stall_login.html')



from django.shortcuts import render, redirect
from django.db import connection

def bookings(request):
    shop_id = request.session.get('shop_id')
    if not shop_id:
        return redirect('stall_login')

    # Fetch orders for the logged-in stall
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT o."tokenid", o."order_id", o."item_name", o."qty", o."name", o."contact_no", o."status", o."timestamp"
            FROM "orderlist" o
            WHERE o."shop_id" = %s AND o."status" IN ('Approved', 'Completed')
            ORDER BY o."timestamp" DESC;
        """, [shop_id])
        orders = cursor.fetchall()

    # Debugging: print out orders to check if data is being fetched correctly
    print("Orders:", orders)

    return render(request, 'bookings.html', {'orders': orders})





from django.shortcuts import redirect
from django.contrib import messages
from django.db import connection
from django.http import HttpResponse

def update_order_status(request, order_id, status):
    if status not in ['completed', 'delivered']:
        return HttpResponse("Invalid status", status=400)

    # Update the order status in the database
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE "orderlist"
            SET "status" = %s
            WHERE "order_id" = %s;
        """, [status.capitalize(), order_id])

    # Provide a success message
    messages.success(request, f"Order {order_id} marked as {status.capitalize()}!")

    # Redirect to the same stall bookings page
    return redirect('bookings')  # Redirecting to 'stall/bookings' URL instead of 'past_orders'



from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

# Dummy admin credentials
ADMIN_EMAIL = "saiprasad.jamdar17561@sakec.ac.in"
ADMIN_PASSWORD = "031004"

def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session['admin_logged_in'] = True
            return redirect('admin_panel')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('admin_login')

    return render(request, 'admin_login.html')


from django.shortcuts import render, redirect
from django.db import connection
from django.db import connection
from django.shortcuts import render, redirect

def admin_panel(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')

    # Fetch all shops and their menu items
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s."shop_id", s."shop_name", m."id", m."name", m."price", m."availability"
            FROM "shops" s
            LEFT JOIN "menuitems" m ON s."shop_id" = m."shop_id"
        """)
        data = cursor.fetchall()

    # Debugging: Print the raw data to see what's being fetched
    print("Fetched data:", data)

    # Organize data into a structured format
    shops = {}
    for row in data:
        shop_id, shop_name, item_id, item_name, price, availability = row
        print(f"Processing shop_id: {shop_id}, shop_name: {shop_name}")  # Debugging
        if shop_id not in shops:
            shops[shop_id] = {
                'shop_name': shop_name,
                'items': []
            }
        if item_id:  # Only append items if they exist
            shops[shop_id]['items'].append({
                'id': item_id,
                'name': item_name,
                'price': price,
                'availability': availability
            })

    # Debugging: Print the final structure of shops
    print("Shops structure:", shops)

    context = {
        'shops': shops
    }
    return render(request, 'admin_panel.html', context)




def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def add_shop(request):
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name')
        passkey = request.POST.get('passkey')
        item_names = request.POST.getlist('item_name[]')
        item_prices = request.POST.getlist('item_price[]')

        try:
            with connection.cursor() as cursor:
                # Insert shop and get the shop_id using RETURNING
                cursor.execute("""
                    INSERT INTO "shops" ("shop_name", "passkey")
                    VALUES (%s, %s)
                    RETURNING "shop_id"
                """, [shop_name, passkey])
                shop_id = cursor.fetchone()[0]  # Get the shop_id from the result

                # Insert menu items for the shop
                for name, price in zip(item_names, item_prices):
                    cursor.execute("""
                        INSERT INTO "menuitems" ("name", "price", "shop_id", "availability")
                        VALUES (%s, %s, %s, %s)
                    """, [name, price, shop_id, 1])

            return JsonResponse({'success': True, 'message': 'Shop and items added successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


from django.views.decorators.csrf import csrf_protect

from django.db import connection
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse

@csrf_protect
def delete_shop(request, shop_id):
    # Logic to delete shop and associated items
    if request.method == 'POST':
        try:
            # Delete all menu items related to the shop
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM "menuitems" WHERE "shop_id" = %s', [shop_id])

            # Delete the shop itself
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM "shops" WHERE "shop_id" = %s', [shop_id])

            return JsonResponse({"success": True, "message": "Shop and its items deleted successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request."})





def shop_listing(request):
    print(f"Session keys: {list(request.session.keys())}")  # Check the session keys
    print(f"Admin logged in status: {request.session.get('admin_logged_in')}")  # Check if admin is logged in

    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    
    return render(request, 'shop_listing.html')



from django.db import connection
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse

@csrf_protect
def toggle_availability(request, item_id):
    print(f"Session keys: {list(request.session.keys())}")  # Check the session keys
    print(f"Admin logged in status: {request.session.get('admin_logged_in')}")  # Check if admin is logged in

    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE "menuitems"
                    SET "availability" = CASE
                        WHEN "availability" = 1 THEN 0
                        WHEN "availability" = 0 THEN 1
                    END
                    WHERE "id" = %s
                    """, [item_id])

            # After updating availability, check session and redirect
            print(f"Updated availability for item_id: {item_id}")
            return redirect('admin_panel')

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request."})



def landing_page(request):
    return render(request, 'index.html')





from django.shortcuts import redirect

import razorpay
import json
import random
import re
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import redirect
from django.db import connection, transaction
from django.conf import settings

import json
import re
import random
from datetime import datetime
from django.db import connection, transaction
from django.http import HttpResponse
from django.shortcuts import redirect
import razorpay
from django.conf import settings

from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import re
from django.db import connection, transaction
import razorpay
from datetime import datetime
import random

from django.shortcuts import redirect
import razorpay
import random
import re
import logging
from datetime import datetime
from django.db import connection, transaction
from django.shortcuts import redirect
from django.http import JsonResponse

# Configure logging
logging.basicConfig(level=logging.DEBUG)

import re

import logging
from random import randint
import razorpay
import re
from datetime import datetime
from django.db import connection, transaction
from django.http import JsonResponse
from django.shortcuts import redirect

def payment_success_view(request):
    if request.method == 'GET':
        logging.debug("Received GET request for payment success.")
        
        payment_id = request.GET.get('payment_id')
        order_id = request.GET.get('order_id')

        if payment_id and order_id:
            try:
                # Fetch user details from session
                user_name = request.session.get('user_name')
                user_email = request.session.get('user_email')
                mobile = request.session.get('user_phone')

                logging.debug(f"Session Data: user_name={user_name}, user_email={user_email}, mobile={mobile}")

                # Check if session data exists
                if not all([user_name, user_email, mobile]):
                    return JsonResponse({'success': False, 'message': "Session data missing."})

                # Initialize Razorpay client
                client = razorpay.Client(auth=("rzp_test_x6EYO4W3NIqb6X", "XyLCQKkNiM9Mf5DIzRwReFEg"))

                # Verify payment with Razorpay
                payment = client.payment.fetch(payment_id)
                logging.debug(f"Fetched payment details: {payment}")

                if payment['status'] == 'captured':
                    logging.debug("Payment captured successfully.")

                    # Retrieve cart items
                    selected_items = request.session.get('selected_items', [])
                    if not selected_items:
                        return JsonResponse({'success': False, 'message': "No items in the session."})
                    
                    logging.debug(f"Selected Items: {selected_items}")

                    try:
                        with transaction.atomic():
                            logging.debug("Transaction started.")

                            # Query 1: Insert user into `users` table if not exists
                            with connection.cursor() as cursor:
                                cursor.execute(""" 
                                    SELECT "user_id" FROM "users" WHERE "mobile" = %s OR "email" = %s;
                                """, [mobile, user_email])
                                result = cursor.fetchone()

                                if result:
                                    user_id = result[0]
                                    logging.debug(f"User exists: user_id={user_id}")
                                else:
                                    cursor.execute(""" 
                                        INSERT INTO "users" ("name", "email", "mobile")
                                        VALUES (%s, %s, %s) RETURNING "user_id";
                                    """, [user_name, user_email, mobile])
                                    user_id = cursor.fetchone()[0]
                                    logging.debug(f"Inserted new user: user_id={user_id}")

                            # Query 2: Check availability and insert order into `orderlist`
                            with connection.cursor() as cursor:
                                for item in selected_items:
                                    item_name = item['item_name']
                                    quantity = item['quantity']
                                    price = float(item['price'])

                                    # Extract shop_id from item_name using regex
                                    match = re.match(r'^(.*?) \(Shop ID: (\d+)\)$', item_name)
                                    item_name_without_shop = match.group(1) if match else item_name
                                    shop_id = match.group(2) if match else None

                                    if not shop_id:
                                        raise Exception(f"Shop ID not found in item: {item_name}")

                                    logging.debug(f"Extracted Shop ID: {shop_id}, Item Name: {item_name_without_shop}")

                                    cursor.execute(""" 
                                        SELECT "availability" FROM "menuitems" WHERE "shop_id" = %s AND "name" = %s;
                                    """, [shop_id, item_name_without_shop])
                                    result = cursor.fetchone()

                                    if result:
                                        availability = result[0]
                                        if availability == 1:
                                            total_price = quantity * price
                                            cursor.execute(""" 
                                                INSERT INTO "orderlist" ("email", "name", "contact_no", "shop_id", "item_name", "qty", "total_amt", "status")
                                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                                            """, [user_email, user_name, mobile, shop_id, item_name_without_shop, quantity, total_price, 'Pending'])
                                            logging.debug(f"Inserted order for {item_name_without_shop} at shop_id={shop_id}")
                                        else:
                                            raise Exception(f"The item '{item_name_without_shop}' is unavailable at Shop ID {shop_id}.")
                                    else:
                                        raise Exception(f"The item '{item_name_without_shop}' was not found in the menu at Shop ID {shop_id}.")

                            # ✅ **Fix: Generate token ID correctly**
                            token_id = randint(1000, 9999)  # Ensure random module is not overridden
                            timestamp = datetime.now()
                            logging.debug(f"Generated token_id={token_id}, timestamp={timestamp}")

                            # Update orders with token ID and payment mode
                            with connection.cursor() as cursor:
                                cursor.execute(""" 
                                    UPDATE "orderlist" 
                                    SET "tokenid" = %s, "timestamp" = %s, "mode_of_payment" = 'Online'
                                    WHERE "email" = %s AND "status" = 'Pending' AND "tokenid" IS NULL;
                                """, [token_id, timestamp, user_email])
                                logging.debug("Updated orderlist with token ID and timestamp.")

                            # Update order status to 'Approved'
                            with connection.cursor() as cursor:
                                cursor.execute(""" 
                                    UPDATE "orderlist" 
                                    SET "status" = 'Approved'
                                    WHERE "email" = %s AND "status" = 'Pending' AND "tokenid" = %s;
                                """, [user_email, token_id])
                                logging.debug("Updated orderlist status to 'Approved'.")

                            logging.debug("Transaction committed successfully.")
                            return redirect('success', token_id=token_id)

                    except Exception as e:
                        logging.error(f"Database transaction failed: {str(e)}")
                        return JsonResponse({'success': False, 'message': f"Error occurred: {str(e)}"})
                else:
                    logging.debug("Payment status is not captured.")
                    return JsonResponse({'success': False, 'message': "Payment failed or not captured."})

            except Exception as e:
                logging.error(f"Payment verification failed: {str(e)}")
                return JsonResponse({'success': False, 'message': f"Payment verification failed: {str(e)}"})
        else:
            logging.debug("Missing payment_id or order_id.")
            return JsonResponse({'success': False, 'message': 'Invalid payment or order details.'})

    logging.debug("Invalid request method.")
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
import uuid

from django.shortcuts import render
import razorpay
import uuid

import uuid
import razorpay
def generate_order_id(request):
    # Fetching user details from session
    user_details = {
        'name': request.session.get('user_name'),
        'email': request.session.get('user_email'),
        'phone': request.session.get('user_phone')
    }
    
    # Fetching selected items from the form data (submitted as JSON string)
    selected_items = request.POST.get('order_items', '[]')  # Get the JSON string of items
    selected_items = json.loads(selected_items)  # Convert the JSON string back to a Python object

    print("Before updating quantities:", selected_items)  # Debugging line

    # Update total_price based on quantity
    for item in selected_items:
        item_quantity = item['quantity']  # Ensure 'quantity' is present
        print(f"Item quantity: {item_quantity}")  # Debugging line
        item['total_price'] = float(item['price']) * item_quantity  # Update total price

    print("After updating quantities:", selected_items)  # Debugging line

    # Recalculate total amount
    total_amount = sum(item['total_price'] for item in selected_items)
    
    # Store updated items in session
    request.session['selected_items'] = selected_items  
    request.session.modified = True  # Ensure session updates

    # Razorpay order creation logic
    client = razorpay.Client(auth=("rzp_test_x6EYO4W3NIqb6X", "XyLCQKkNiM9Mf5DIzRwReFEg"))
    razorpay_order = client.order.create(dict(
        amount=int(total_amount * 100),  # amount in paise
        currency='INR',
        receipt=str(uuid.uuid4())
    ))

    # Storing the Razorpay order ID in the session
    request.session['razorpay_order_id'] = razorpay_order['id']

    # Returning the response with updated data
    context = {
        'user_details': user_details,
        'selected_items': selected_items,
        'total_amount': total_amount,
        'razorpay_order_id': razorpay_order['id'],
    }
    print(context)
    return render(request, 'pay_online.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate;
from random import *
from django.core.mail import send_mail
from .models import Profile  # Assuming Profile model exists

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from random import choice

def urnp(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            un = request.POST.get("un")
            try:
                # Check if the user exists in the database
                usr = User.objects.get(username=un)
                
                # Generate a new secure password
                pw = "".join(choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&") for _ in range(8))
                usr.set_password(pw)  # Update the user's password
                usr.save()  # Save the updated user
                
                # Send an email with the new password
                subject = "Reset Password - Kamal Classes"
                text = f"Your new password is - {pw}"
                from_email = "sai.tester24jan24@gmail.com"
                send_mail(subject, text, from_email, [un])
                
                # Redirect to login after successful reset
                return redirect("ulogin")
            except User.DoesNotExist:
                # If the email does not exist in the database
                msg = "Email not registered"
                return render(request, "urnp.html", {"msg": msg})  # Render the reset password page with an error message
        else:
            return render(request, "urnp.html")  # Render the reset password page initially



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from random import choice

def ulogin(request):
    if request.user.is_authenticated:
        # Set session variable after successful login
        request.session['is_authenticated'] = True
        return redirect("home")
    else:
        if request.method == "POST":
            un = request.POST.get("un")
            pw = request.POST.get("pw")
            usr = authenticate(username=un, password=pw)
            
            if usr:
                login(request, usr)
                # Set session variable after successful login
                request.session['is_authenticated'] = True
                return redirect("home")
            else:
                msg = "Invalid email or password"
                return render(request, "ulogin.html", {"msg": msg})
        else:
            return render(request, "ulogin.html")


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from random import choice

def usignup(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            phone = request.POST.get("phone")
            un = request.POST.get("un")
            
            if User.objects.filter(username=un).exists():
                msg = "Email already registered"
                return render(request, "usignup.html", {"msg": msg})

            # Generate password securely
            pw = "".join(choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&") for _ in range(8))

            # Create user
            usr = User.objects.create_user(first_name=username, username=un, password=pw, email=un)
            usr.save()

            # Save phone number in Profile model
            Profile.objects.create(user=usr, phone=phone)

            # Send email with password
            subject = "Welcome to Kamal Classes"
            text = f"Your password is - {pw}"
            from_email = "sai.tester24jan24@gmail.com"
            send_mail(subject, text, from_email, [un])

            return redirect("ulogin")
        else:
            return render(request, "usignup.html")

	
from django.contrib.auth import logout
from django.shortcuts import redirect

def ulogout(request):
    # Clear the session when logging out
    logout(request)
    request.session.flush()  # This will clear the session
    return redirect("ulogin")



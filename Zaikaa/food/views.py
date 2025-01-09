from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.db import connection
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.db import connection
import json
def home(request):
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
                Shops s
            LEFT JOIN 
                MenuItems m ON s.shop_id = m.shop_id
            WHERE 
                m.availability = 1  -- Only include available items
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

        # Store formatted items in the session
        request.session['selected_items'] = formatted_items

        # Redirect to confirmation page
        return redirect('confirm_order')

    # Pass the data to the template
    return render(request, 'food/home.html', {'shops': shops})


def confirm_order(request):
    # Retrieve the selected items from the session
    selected_items = request.session.get('selected_items', [])

    # If no items are selected, redirect to the home page
    if not selected_items:
        return redirect('home')

    # Print the selected items to verify if they are being retrieved correctly
    print(f"Selected Items in session: {selected_items}")

    # Pass the selected items to the template
    return render(request, 'food/confirm_order.html', {'selected_items': selected_items})



from django.shortcuts import render, redirect
from django.db import connection, transaction
from django.http import HttpResponse
import json
import re

import json
import re
from django.db import connection, transaction
from django.http import HttpResponse
from django.shortcuts import redirect

from django.db import transaction, connection
from django.shortcuts import redirect
from django.http import HttpResponse
import json
import re

from django.shortcuts import render, redirect
from django.db import transaction
from django.db import connection
import json
import re
from django.http import HttpResponse

def settinguporder(request):
    # Get form data
    user_name = request.POST.get('name')
    user_email = request.POST.get('email')  # Get email from the form
    mobile = request.POST.get('mobile')
    
    # Get selected items from session (just in case you also need them)
    selected_items = request.session.get('selected_items', [])
    
    # Extract shop IDs from selected items
    shop_ids = list(set(item['shop_id'] for item in selected_items))  # Ensure no duplicates
    
    total_amount = float(request.POST.get('total'))  # Get the total amount from the form
    # Parse the JSON string into a Python object (list of items)
    items = json.loads(request.POST.get('order_items'))  # Get a list of items from the form
    
    # Print the data to check if they are being received properly
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
            # Query 1: Add user to the Users table (if not already added)
            with connection.cursor() as cursor:
                # Check if the user already exists by mobile number or email
                cursor.execute(""" 
                    SELECT user_id FROM Users WHERE mobile = %s OR email = %s;
                """, [mobile, user_email])
                result = cursor.fetchone()

                if result:
                    # If user exists, use the existing user_id
                    user_id = result[0]
                    print(f"User ID already exists: {user_id}")
                else:
                    # If user doesn't exist, insert a new record
                    cursor.execute(""" 
                        INSERT INTO Users (name, email, mobile)
                        VALUES (%s, %s, %s);
                    """, [user_name, user_email, mobile])
                    print("Executed INSERT into Users table")

                    # Get the last inserted user_id
                    cursor.execute("SELECT LAST_INSERT_ID();")
                    user_id = cursor.fetchone()[0]
                    print(f"User ID: {user_id}")

            # Query 2: Insert into OrderList for each shop_id in the selected items
            with connection.cursor() as cursor:
                for shop_id in shop_ids:
                    # Filter items by shop_id (ensure we match the shop_id of the item correctly)
                    shop_items = [item for item in items if re.search(r'\(Shop ID: (\d+)\)', item['item_name']) and int(re.search(r'\(Shop ID: (\d+)\)', item['item_name']).group(1)) == shop_id]
                    
                    for item in shop_items:
                        # Extract item details directly from the parsed JSON object
                        item_name = item['item_name']
                        quantity = item['quantity']
                        price = float(item['price'])  # Ensure price is treated as a float
                        
                        # Calculate the total price (quantity * price)
                        total_price = quantity * price

                        # Insert the item into OrderList table for the specific shop
                        cursor.execute(""" 
                            INSERT INTO OrderList (email, name, contact_no, shop_id, item_name, qty, total_amt, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        """, [user_email, user_name, mobile, shop_id, item_name, quantity, total_price, 'Pending'])
                        print(f"Executed INSERT into OrderList table: User ID = {user_id}, Shop ID = {shop_id}, Item = {item_name}, Quantity = {quantity}, Price = {price}, Total Price = {total_price}")

        # After completing the queries, redirect to the waiting page
        print("Order processing completed successfully")
        return redirect('waiting')  # Assuming you have a URL named 'waiting'

    except Exception as e:
        # If any error occurs, rollback the transaction
        print(f"Error while processing the order: {e}")
        transaction.rollback()  # Rollback the transaction if an error occurs
        # Optionally log the error
        # Redirect to an error page or show a message
        return HttpResponse("An error occurred while processing your order. Please try again.", status=500)

import random
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
import random

from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
import random

import random
from django.http import JsonResponse
from django.db import connection

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import random
import json
import random
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

# Set up logging
logger = logging.getLogger(__name__)

import random
from django.http import JsonResponse
from django.db import connection
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import random
@csrf_exempt  # For testing without CSRF issues (you may want to handle CSRF properly in production)
def check_order_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Load JSON body
            email = data.get('email')  # Get the email from the parsed JSON

            if not email:
                print("No email provided!")  # Debugging
                return JsonResponse({'error': 'Email not provided'}, status=400)

            print(f"Received email: {email}")  # Debugging

            # Check if all items in the order are approved
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM OrderList 
                    WHERE email = %s AND status = 'Pending';
                """, [email])
                result = cursor.fetchone()

            print(f"Query result: {result}")  # Debugging the result of the query

            if result:
                pending_count = result[0]
                print(f"Pending items count: {pending_count}")  # Debugging the count

                if pending_count == 0:
                    # All items have been approved, generate token_id
                    token_id = random.randint(1000, 9999)  # Example: Generate a random token ID
                    print(f"Generated token_id: {token_id}")  # Debugging the token_id

                    # Update the orders with the generated token ID
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE OrderList
                            SET tokenID = %s
                            WHERE email = %s AND status = 'Approved' AND tokenID IS NULL;
                        """, [token_id, email])

                    # Return success with token_id
                    return JsonResponse({'status': 'success', 'message': 'Order approved', 'token_id': token_id})

                else:
                    return JsonResponse({'status': 'pending', 'message': f'{pending_count} item(s) still pending approval'})

            return JsonResponse({'error': 'Order not found for the given email'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



def success(request, token_id):
    # You can check if the token ID exists in the database or its status here if needed
    # For now, we will just pass the token_id to the success page
    return render(request, 'food/success.html', {'token_id': token_id})

# views.py
def waiting(request):
    return render(request, 'food/waiting.html')


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection

def adminapproval(request):
    # Get all orders where the status is 'Pending'
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT order_id, email, name, contact_no, item_name, qty, total_amt 
            FROM OrderList 
            WHERE status = 'Pending';
        """)
        pending_orders = cursor.fetchall()
    
    # Render the adminapproval.html template and pass pending orders
    return render(request, 'food/adminapproval.html', {'pending_orders': pending_orders})

def approve_order(request, order_id):
    # Approve the order by updating its status to 'Approved'
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE OrderList 
            SET status = 'Approved' 
            WHERE order_id = %s;
        """, [order_id])
    
    return redirect('adminapproval')  # Redirect back to the admin approval page



def allorders(request):
    # Get all orders from the database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT order_id, email, name, contact_no, item_name, qty, total_amt, status
            FROM OrderList;
        """)
        all_orders = cursor.fetchall()

    # Render the allorders.html template and pass all orders
    return render(request, 'food/allorders.html', {'all_orders': all_orders})

from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.db import connection


from django.shortcuts import render
from django.db import connection

def home(request):
    # Execute raw SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.shop_name,                         
                oi.item_name AS item_name,            
                oi.price,                             
                IF(SUM(oi.quantity) > 0, 'Available', 'Unavailable') AS availability
            FROM 
                Shops s
            JOIN 
                Orders o ON s.shop_id = o.shop_id    
            JOIN 
                OrderItems oi ON o.order_id = oi.order_id  
            GROUP BY 
                s.shop_name, oi.item_name, oi.price    
            ORDER BY 
                s.shop_name, oi.item_name;
        """)
        
        # Fetch all results
        rows = cursor.fetchall()

    # Format the results into a dictionary by shop
    shops = {}
    for row in rows:
        shop_name = row[0]
        item_name = row[1]
        price = row[2]
        availability = row[3]

        if shop_name not in shops:
            shops[shop_name] = []

        shops[shop_name].append({
            'item_name': item_name,
            'price': price,
            'availability': availability
        })
    
    # Pass the data to the template
    return render(request, 'food/home.html', {'shops': shops})


from django.shortcuts import render
from django.http import JsonResponse
# Confirm the order by showing selected items stored in session
def confirm_order(request):
    # Retrieve the selected items from the session
    selected_items = request.session.get('selected_items', [])

    # If no items are selected, redirect to home page
    if not selected_items:
        return redirect('home')

    # Fetch prices and other item details from the database (or another source)
    items_with_details = []
    for item_name in selected_items:
        # Fetch item details such as price from the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT item_name, price FROM OrderItems WHERE item_name = %s
            """, [item_name])
            row = cursor.fetchone()

        if row:
            items_with_details.append({
                'item_name': row[0],
                'price': row[1],
            })

    # Pass the data to the template
    return render(request, 'food/confirm_order.html', {'selected_items': items_with_details})


def process_order(request):
    if request.method == 'POST':
        # Extract the selected items from the form data
        selected_items = request.POST.getlist('selected_items')

        # Store the selected items in the session
        request.session['selected_items'] = selected_items

        # Return a JSON response to indicate successful submission
        return JsonResponse({'status': 'success'})
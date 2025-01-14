 // Function to collect order items (item_name, qty, price)
 function collectOrderItems() {
  const items = [];
  const orderItems = document.querySelectorAll('.order-item');
  
  orderItems.forEach(item => {
      const itemName = item.querySelector('.item-name').textContent.trim();
      const quantity = parseInt(item.querySelector('.quantity-input').value);
      const price = parseFloat(item.querySelector('.item-price').textContent.replace('₹', ''));
      const totalPrice = price * quantity;

      // Add item details to the array
      items.push({
          item_name: itemName,
          quantity: quantity,
          price: price.toFixed(2),  // Store the unit price
          total_price: totalPrice.toFixed(2)  // Store the total price for this item
      });
  });

  return items;
}

// Calculate total price dynamically
function updatePrice() {
  let total = 0;
  const items = document.querySelectorAll('.order-item');
  items.forEach(item => {
      const price = parseFloat(item.querySelector('.item-price').textContent.replace('₹', ''));
      const quantity = parseInt(item.querySelector('.quantity-input').value);
      total += price * quantity;
  });
  document.getElementById('total-price').textContent = total.toFixed(2);
  document.getElementById('total-input').value = total.toFixed(2);  // Update hidden input field
}

// Event listener for form submission
document.getElementById('order-form').addEventListener('submit', function(event) {
  // Collect order items
  const orderItems = collectOrderItems();
  
  // Store order items in hidden input field as a JSON string
  document.getElementById('order-items-input').value = JSON.stringify(orderItems);

  // Optionally, you can log or debug the items
  console.log(orderItems);
});

// Update quantity and price dynamically
document.querySelectorAll('.increase').forEach(button => {
  button.addEventListener('click', function() {
      const input = document.querySelector(`.quantity-input[data-item="${this.dataset.item}"]`);
      let quantity = parseInt(input.value) + 1;
      input.value = quantity;
      updatePrice();
  });
});

document.querySelectorAll('.decrease').forEach(button => {
  button.addEventListener('click', function() {
      const input = document.querySelector(`.quantity-input[data-item="${this.dataset.item}"]`);
      let quantity = Math.max(1, parseInt(input.value) - 1);
      input.value = quantity;
      updatePrice();
  });
});

// Initialize the price on page load
updatePrice();
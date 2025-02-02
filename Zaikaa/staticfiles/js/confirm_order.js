document.addEventListener("DOMContentLoaded", function () {

  const ease = "power4.inOut";

// Page Load Animation (Hides Loader after Animation)
revealTransition().then(() => {
  gsap.set(".block", { visibility: "hidden" });
});

// Click Navigation Animation
document.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", (event) => {
      event.preventDefault();
      const href = link.getAttribute("href");

      if (href && !href.startsWith("#") && href !== window.location.pathname) {
          animateTransition().then(() => {
              window.location.href = href;
          });
      }
  });
});

// Reveal Animation (Runs on Page Load)
function revealTransition() {
  return new Promise((resolve) => {
      gsap.to(".block", { scaleY: 1 });
      gsap.to(".block", {
          scaleY: 0,
          duration: 1.5,
          ease: ease,
          onComplete: resolve
      });
  });
}

// Animate Loader when Navigating to a Different Page
function animateTransition() {
  return new Promise((resolve) => {
      gsap.set(".block", { visibility: "visible", scaleY: 0 });
      gsap.to(".block", {
          scaleY: 1,
          duration: 1.5,
          ease: ease,
          onComplete: resolve
      });
  });
}

// GSAP Animation for .user-details (coming from the bottom)
gsap.from(".user-details", {
y: 50, // Moves from 50px below
opacity: 0,
duration: 1,
delay:.5,
ease: "power3.out"
});

// GSAP Staggered Animation for .order-item in #order-list
gsap.from("#order-list .order-item", {
y: 50, // Moves from 50px below
opacity: 0,
duration: 1,
delay:.5,
ease: "power3.out",
stagger: 0.2 // Delays each item slightly
});
});

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

// Event listener for form submission (Pay by Cash)
document.getElementById('order-form').addEventListener('submit', function(event) {
  // Collect order items
  const orderItems = collectOrderItems();
  
  // Store order items in hidden input field as a JSON string
  document.getElementById('order-items-input').value = JSON.stringify(orderItems);

  // Optionally, you can log or debug the items
  console.log(orderItems);
});

// Event listener for form submission (Pay Online)
document.getElementById('online-payment-form').addEventListener('submit', function(event) {
  // Collect order items for Pay Online
  const orderItems = collectOrderItems();
  
  // Store order items in the hidden input field as a JSON string
  document.getElementById('online-order-items-input').value = JSON.stringify(orderItems);

  // Calculate total for Pay Online and store it in the hidden input field
  let total = 0;
  orderItems.forEach(item => {
      total += parseFloat(item.total_price);
  });
  document.getElementById('online-total-input').value = total.toFixed(2);
  let x = document.getElementById('online-total-input').value
  
  // Optionally, you can log or debug the items
  console.log(orderItems);
  console.log('Total:', total.toFixed(2));
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

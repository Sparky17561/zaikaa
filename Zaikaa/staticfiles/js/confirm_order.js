// Initialize variables
let totalPrice = 0;

// Update total price function
function updateTotalPrice() {
  totalPrice = 0;
  const orderItems = [];
  const items = document.querySelectorAll(".order-item");

  items.forEach((item) => {
    const quantity = parseInt(item.querySelector(".quantity-input").value);
    const price = parseFloat(
      item.querySelector(".item-price").textContent.replace("₹", "")
    );
    totalPrice += price * quantity;

    // Add item details to orderItems array
    orderItems.push({
      item_name: item.querySelector(".item-name").textContent.trim(),
      price: price,
      quantity: quantity,
    });
  });

  document.getElementById("total-price").textContent = totalPrice.toFixed(2);
  document.getElementById("total-input").value = totalPrice.toFixed(2);
  document.getElementById("order-items-input").value =
    JSON.stringify(orderItems);
}

// Event listeners for quantity buttons
document.querySelectorAll(".quantity-btn").forEach((btn) => {
  btn.addEventListener("click", (event) => {
    const item = event.target.closest(".order-item");
    const quantityInput = item.querySelector(".quantity-input");
    let quantity = parseInt(quantityInput.value);

    if (btn.classList.contains("increase")) {
      quantity++;
    } else if (btn.classList.contains("decrease") && quantity > 1) {
      quantity--;
    }

    quantityInput.value = quantity;
    updateTotalPrice();
  });
});

// Event listeners for quantity input changes
document.querySelectorAll(".quantity-input").forEach((input) => {
  input.addEventListener("input", () => {
    if (parseInt(input.value) < 1 || isNaN(input.value)) {
      input.value = 1;
    }
    updateTotalPrice();
  });
});

// Form validation
document.getElementById("order-form").addEventListener("submit", (event) => {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const phone = document.getElementById("phone").value.trim();

  let valid = true;

  // Name validation
  if (name === "") {
    valid = false;
    document.getElementById("name-error").textContent = "Name is required.";
  } else {
    document.getElementById("name-error").textContent = "";
  }

  // Email validation
  const emailRegex = /^[a-zA-Z0-9._%+-]+@sakec\.ac\.in$/;
  if (!emailRegex.test(email)) {
    valid = false;
    document.getElementById("email-error").textContent =
      "Enter a valid SAKEC email.";
  } else {
    document.getElementById("email-error").textContent = "";
  }

  // Phone validation
  const phoneRegex = /^[0-9]{10}$/;
  if (!phoneRegex.test(phone)) {
    valid = false;
    document.getElementById("phone-error").textContent =
      "Enter a valid 10-digit phone number.";
  } else {
    document.getElementById("phone-error").textContent = "";
  }

  if (!valid) {
    event.preventDefault();
  }
});

// Razorpay payment integration
document.getElementById("pay-online").addEventListener("click", () => {
  const options = {
    key: "rzp_test_xxxxxxxxxxxxxx", // Replace with your Razorpay API Key
    amount: (totalPrice * 100).toFixed(0),
    currency: "INR",
    name: "Food Fiesta",
    description: "Order Payment",
    handler: (response) => {
      alert("Payment Successful! Payment ID: " + response.razorpay_payment_id);
      // Optionally submit the form or handle post-payment logic here
    },
    prefill: {
      name: document.getElementById("name").value,
      email: document.getElementById("email").value,
      contact: document.getElementById("phone").value,
    },
    theme: {
      color: "#3399cc",
    },
  };

  const rzp = new Razorpay(options);
  rzp.open();
});

// Toggle theme
document.getElementById("themeToggle").addEventListener("click", () => {
  document.body.classList.toggle("dark-theme");
});

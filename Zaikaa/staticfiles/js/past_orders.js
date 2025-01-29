// Final Merged JavaScript with frontend and backend functionality combined
//without predefined datasets.

document.addEventListener("DOMContentLoaded", () => {
  const csrfToken = document.querySelector(
    '[name="csrfmiddlewaretoken"]'
  )?.value;
  const fetchOrdersButton = document.getElementById("fetch-orders-btn");
  const loadingElement = document.getElementById("loading");
  const ordersDiv = document.getElementById("orders");
  const orderInfo = document.getElementById("order-info");
  const orderDetails = document.getElementById("order-details");
  const totalAmountElement = document.getElementById("total-amount");

  fetchOrdersButton.addEventListener("click", () => {
    loadingElement.style.display = "block"; // Show loading indicator
    fetch("/food/past_orders/api/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken, // Ensure the token is passed here
      },
      body: JSON.stringify({ email: "{{ user_email }}" }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Received data:", data); // Print the received data in console
        loadingElement.style.display = "none"; // Hide loading indicator

        if (data.orders.length === 0) {
          ordersDiv.innerHTML = "<p>No past orders found.</p>";
          return;
        }

        ordersDiv.innerHTML = ""; // Clear any previous orders
        let totalAmount = 0;
        let orderHTML = "";

        data.orders.forEach((order) => {
          orderHTML += `
                    <div class="stall">
                        <h2 class="stall-name">Token ID: ${order.token_id}</h2>
                        <p>Date & Time: ${order.timestamp}</p>
                        <p>Mode of Payment: ${order.mode_of_payment}</p>
                        <div class="items-container">
                `;

          order.items.forEach((item) => {
            const itemTotal = item.total_amount;
            totalAmount += itemTotal;
            orderHTML += `
                        <div class="item">
                            <span>${item.quantity}x ${item.item_name}</span>
                            <span>₹${itemTotal.toFixed(2)}</span>
                        </div>
                    `;
          });

          orderHTML += `
                        </div>
                        <div class="order-footer">
                            Grand Total: ₹${order.grand_total.toFixed(2)}
                        </div>
                    </div>
                `;

          orderHTML += '<div class="separator"></div>';
        });

        orderDetails.innerHTML = orderHTML;
        totalAmountElement.textContent = `₹${totalAmount.toFixed(2)}`;
      })
      .catch((error) => {
        loadingElement.style.display = "none";
        console.error("Error fetching past orders:", error);
        alert("Failed to fetch past orders. Please try again later.");
      });
  });
});

function getStatusClass(status) {
  if (!status) return ""; // Handle undefined or null status
  status = status.trim().toLowerCase();
  if (status === "approved") return "status-approved";
  if (status === "completed") return "status-completed";
  if (status === "delivered") return "status-delivered";
  return ""; // Default if no status matches
}

function getStatusText(status) {
  if (!status) return "Unknown Status"; // Handle undefined or null status
  status = status.trim().toLowerCase();
  if (status === "approved") return "Cooking";
  if (status === "completed") return "Ready to Take";
  if (status === "delivered") return "Delivered";
  return "Unknown Status"; // Default text for unknown status
}

// Final Merged JavaScript with frontend and backend functionality combined
//without predefined datasets.

// const email = "{{ user_email }}"; // Using the passed email from the backend
// const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]')?.value;

// const fetchOrdersButton = document.getElementById("fetch-orders-btn");
// const loadingElement = document.getElementById("loading");
// const ordersDiv = document.getElementById("orders");
// const totalAmountElement = document.getElementById("total-amount");

// const order = {
//   id: "ORD-12345",
//   date: "2025-01-8",
//   stalls: [
//     {
//       name: "Burger Paradise",
//       items: [
//         { name: "Cheeseburger", quantity: 2, price: 8.99 },
//         { name: "Fries", quantity: 1, price: 3.49 },
//       ],
//     },
//     {
//       name: "Pizza Heaven",
//       items: [
//         { name: "Margherita Pizza", quantity: 1, price: 12.99 },
//         { name: "Garlic Bread", quantity: 1, price: 4.99 },
//       ],
//     },
//   ],
// };

// function formatCurrency(amount) {
//   return `\u20B9${amount.toFixed(2)}`;
// }

// function renderOrderDetails() {
//   const orderDetails = document.getElementById("order-details");
//   const orderInfo = document.getElementById("order-info");

//   orderInfo.textContent = `Order #${order.id} - ${order.date}`;

//   let totalAmount = 0;
//   let orderHTML = "";

//   order.stalls.forEach((stall, stallIndex) => {
//     orderHTML += `
//             <div class="stall">
//                 <h2 class="stall-name">${stall.name}</h2>
//                 <div class="items">
//         `;

//     stall.items.forEach((item) => {
//       const itemTotal = item.price * item.quantity;
//       totalAmount += itemTotal;
//       orderHTML += `
//                 <div class="item">
//                     <span>${item.quantity}x ${item.name}</span>
//                     <span>${formatCurrency(itemTotal)}</span>
//                 </div>
//             `;
//     });

//     orderHTML += `
//                 </div>
//             </div>
//         `;

//     if (stallIndex < order.stalls.length - 1) {
//       orderHTML += '<div class="separator"></div>';
//     }
//   });

//   orderDetails.innerHTML = orderHTML;
//   totalAmountElement.textContent = formatCurrency(totalAmount);
// }

// document.addEventListener("DOMContentLoaded", () => {
//   renderOrderDetails();

//   fetchOrdersButton.addEventListener("click", () => {
//     loadingElement.style.display = "block"; // Show loading indicator
//     fetch("/food/past_orders/api/", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         "X-CSRFToken": csrfToken, // Ensure the token is passed here
//       },
//       body: JSON.stringify({ email: email }),
//     })
//       .then((response) => response.json())
//       .then((data) => {
//         console.log("Received data:", data); // Print the received data in console
//         loadingElement.style.display = "none"; // Hide loading indicator

//         if (data.orders.length === 0) {
//           ordersDiv.innerHTML = "<p>No past orders found.</p>";
//           return;
//         }

//         ordersDiv.innerHTML = ""; // Clear any previous orders
//         data.orders.forEach((order) => {
//           const orderDiv = document.createElement("div");
//           orderDiv.className = "order-container";

//           orderDiv.innerHTML = `
//                         <div class="order-header">
//                             <h3>Token ID: ${order.token_id}</h3>
//                             <p>Date & Time: ${order.timestamp}</p>
//                             <p>Mode of Payment: ${order.mode_of_payment}</p>
//                         </div>
//                         <div class="items-container">
//                             ${order.items
//                               .map((item) => {
//                                 return `
//                                         <div class="item">
//                                             <div class="item-details">
//                                                 <p><strong>Shop:</strong> ${
//                                                   item.shop_name
//                                                 }</p>
//                                                 <p><strong>Item:</strong> ${
//                                                   item.item_name
//                                                 }</p>
//                                                 <p><strong>Quantity:</strong> ${
//                                                   item.quantity
//                                                 }</p>
//                                                 <p><strong>Total:</strong> ₹${(
//                                                   Number(item.total_amount) || 0
//                                                 ).toFixed(2)}</p>
//                                             </div>
//                                             <div class="status ${getStatusClass(
//                                               item.status
//                                             )}">
//                                                 ${getStatusText(item.status)}
//                                             </div>
//                                         </div>
//                                     `;
//                               })
//                               .join("")}
//                         </div>

//                         <div class="order-footer">
//                             Grand Total: ₹${(
//                               Number(order.grand_total) || 0
//                             ).toFixed(2)}
//                         </div>
//                     `;

//           ordersDiv.appendChild(orderDiv);
//         });
//       })
//       .catch((error) => {
//         loadingElement.style.display = "none";
//         console.error("Error fetching past orders:", error);
//         alert("Failed to fetch past orders. Please try again later.");
//       });
//   });
// });

// function getStatusClass(status) {
//   if (!status) return ""; // Handle undefined or null status
//   status = status.trim().toLowerCase();
//   if (status === "approved") return "status-approved";
//   if (status === "completed") return "status-completed";
//   if (status === "delivered") return "status-delivered";
//   return ""; // Default if no status matches
// }

// function getStatusText(status) {
//   if (!status) return "Unknown Status"; // Handle undefined or null status
//   status = status.trim().toLowerCase();
//   if (status === "approved") return "Cooking";
//   if (status === "completed") return "Ready to Take";
//   if (status === "delivered") return "Delivered";
//   return "Unknown Status"; // Default text for unknown status
// }

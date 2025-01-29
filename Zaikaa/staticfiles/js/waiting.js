const email = "{{ user_email }}"; // Email passed from the view
console.log(email)
const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  .getAttribute("content");

function debugLog(message, data = null) {
  console.log(message, data || "");
  // Optional fallback for visibility in case console logs don't show
  // alert(`${message} ${data ? JSON.stringify(data) : ""}`);
}

if (!email) {
  debugLog("Email is not provided");
  alert("Email is missing. Please log in again.");
} else {
  debugLog("Email found:", email); // Debugging email value

  let pollingInterval = null;

  function checkStatus() {
    debugLog("Starting status check..."); // Polling initiated

    fetch("/food/check_order_status/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ email: email }),
    })
      .then((response) => {
        debugLog("Response received:", response); // Log raw response object
        return response.json();
      })
      .then((data) => {
        debugLog("Data received from server:", data); // Log parsed server response

        const statusElement = document.getElementById("status");
        if (!statusElement) {
          debugLog("Status element not found in the DOM.");
          alert("Status element missing on the page.");
          return;
        }

        const status = data.status;
        debugLog("Order status:", status); // Log current status

        statusElement.textContent = `Status: ${
          status.charAt(0).toUpperCase() + status.slice(1)
        }`;

        if (status === "success") {
          debugLog("Order successfully processed. Redirecting...");
          clearInterval(pollingInterval); // Stop polling
          // Redirect to the success page with token_id
          window.location.href = `/food/success/${data.token_id}/`;
        } else if (status === "error") {
          debugLog("Server returned an error:", data.message);
          alert(data.message || "An error occurred. Please try again later.");
        } else if (status === "pending") {
          debugLog("Order is still pending approval.");
        } else {
          debugLog("Unexpected status received:", status);
        }
      })
      .catch((error) => {
        debugLog("Error fetching order status:", error);
        alert("Failed to fetch order status. Please check your connection.");
      });
  }

  // Start polling every 10 seconds
  debugLog("Starting polling every 10 seconds...");
  pollingInterval = setInterval(checkStatus, 10000);
  checkStatus(); // Initial call
}

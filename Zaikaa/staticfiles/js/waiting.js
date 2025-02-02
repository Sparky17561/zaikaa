// Fetch email passed from Django template
const email = "{{ user_email }}"; 
console.log("User Email:", email); // Debugging email value

// Fetch CSRF token from the meta tag
const csrfTokenElement = document.querySelector('meta[name="csrf-token"]');
const csrfToken = csrfTokenElement ? csrfTokenElement.getAttribute("content") : null;

function debugLog(message, data = null) {
  console.log(message, data || "");
}

if (!email || email.trim() === "") {
  debugLog("Email is missing");
  alert("Email is missing. Please log in again.");
} else if (!csrfToken) {
  debugLog("CSRF token is missing");
  alert("CSRF token is missing. Please refresh the page and try again.");
} else {
  debugLog("Email and CSRF token found:", { email, csrfToken });

  let pollingInterval = null;

  function checkStatus() {
    debugLog("Checking order status...");

    fetch("/food/check_order_status/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ email: email }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        debugLog("Server Response:", data);

        const statusElement = document.getElementById("status");
        if (!statusElement) {
          debugLog("Status element not found in DOM");
          alert("Status element is missing on the page.");
          return;
        }

        const status = data.status || "unknown"; // Default to "unknown" if undefined

        // Ensure `status` is a valid string before using `charAt`
        if (typeof status === "string" && status.length > 0) {
          statusElement.textContent = `Status: ${
            status.charAt(0).toUpperCase() + status.slice(1)
          }`;
        } else {
          statusElement.textContent = "Status: Unknown";
          debugLog("Invalid status received:", status);
        }

        if (status === "success") {
          debugLog("Order approved! Redirecting...");
          clearInterval(pollingInterval);
          window.location.href = `/food/success/${data.token_id}/`;
        } else if (status === "error") {
          debugLog("Error:", data.message);
          alert(data.message || "An error occurred. Please try again.");
        } else if (status === "pending") {
          debugLog("Order is still pending...");
        } else {
          debugLog("Unexpected status:", status);
        }
      })
      .catch((error) => {
        debugLog("Fetch error:", error);
        alert("Failed to fetch order status. Please check your internet connection.");
      });
  }

  debugLog("Starting polling every 10 seconds...");
  pollingInterval = setInterval(checkStatus, 10000);
  checkStatus(); // Initial call
}

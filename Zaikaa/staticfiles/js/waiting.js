const email = "{{ user_email }}"; // Email passed from the view
const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  .getAttribute("content");

if (!email) {
  console.error("Email is not provided");
  alert("Email is missing. Please log in again.");
} else {
  let pollingInterval = null;

  function checkStatus() {
    fetch("/food/check_order_status/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ email: email }),
    })
      .then((response) => response.json())
      .then((data) => {
        const statusElement = document.getElementById("status");
        const status = data.status;

        statusElement.textContent = `Status: ${
          status.charAt(0).toUpperCase() + status.slice(1)
        }`;

        if (status === "success") {
          clearInterval(pollingInterval); // Stop polling
          // Redirect to the success page with token_id
          window.location.href = `/food/success/${data.token_id}/`;
        } else if (status === "error") {
          alert(data.message || "An error occurred. Please try again later.");
          console.error("Error:", data.message);
        }
      })
      .catch((error) => {
        console.error("Error fetching order status:", error);
        alert("Failed to fetch order status. Please check your connection.");
      });
  }

  // Start polling every 10 seconds
  pollingInterval = setInterval(checkStatus, 10000);
  checkStatus(); // Initial call
}

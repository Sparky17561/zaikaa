// <!-- JavaScript for handling navigation and shop deletion -->
// Get CSRF token from the DOM
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

document
  .getElementById("show-pending-orders-button")
  .addEventListener("click", function () {
    window.location.href = "/admin/approval/";
  });

// Function to delete shop
function deleteShop(shopId) {
  if (
    confirm("Are you sure you want to delete this shop and all its menu items?")
  ) {
    fetch(`/food/admin/delete_shop/${shopId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken, // Include CSRF token
      },
      body: JSON.stringify({ shop_id: shopId }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message);
        location.reload();
      })
      .catch((error) => console.error("Error:", error));
  }
}

document
  .getElementById("show-all-orders-button")
  .addEventListener("click", function () {
    window.location.href = "{% url 'allorders' %}";
  });

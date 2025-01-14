function addMenuItem() {
  const container = document.getElementById("menuItemsContainer");
  const newItem = document.createElement("div");
  newItem.classList.add("form-group");
  newItem.innerHTML = `
                <input type="text" name="item_name[]" placeholder="Item Name" required>
                <input type="number" name="item_price[]" placeholder="Price" required>
            `;
  container.appendChild(newItem);
}

document.getElementById("addShopForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const formData = new FormData(this);

  fetch("/food/admin/add_shop/", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message);
      if (data.success) {
        location.href = "/food/admin/panel/";
      }
    })
    .catch((error) => console.error("Error:", error));
});

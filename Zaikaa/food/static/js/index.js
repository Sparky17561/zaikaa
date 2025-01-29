// // Fetch data from the Django API endpoint
// fetch("/food/api/get-shops-and-items/")
//   .then((response) => response.json())
//   .then((data) => {
//     // Get the container to display the shops
//     const container = document.getElementById("shops-container");

//     // Loop through each shop
//     for (let shopName in data) {
//       // Create a new shop section
//       const shopDiv = document.createElement("div");
//       shopDiv.classList.add("shop");

//       // Create shop name header
//       const shopHeader = document.createElement("div");
//       shopHeader.classList.add("shop-name");
//       shopHeader.textContent = shopName;
//       shopDiv.appendChild(shopHeader);

//       // Loop through each item in the shop
//       const items = data[shopName];
//       items.forEach((item) => {
//         const itemDiv = document.createElement("div");
//         itemDiv.classList.add("item");
//         itemDiv.textContent = `${item.item_name} - Rs${item.price} - ${item.availability}`;
//         shopDiv.appendChild(itemDiv);
//       });

//       // Append the shop to the container
//       container.appendChild(shopDiv);
//     }
//   })
//   .catch((error) => console.error("Error fetching data:", error));

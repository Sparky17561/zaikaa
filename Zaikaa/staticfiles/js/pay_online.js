 // Razorpay payment handling
 document.getElementById('pay-btn').onclick = function () {
    var order_id = this.getAttribute('data-order-id');

    var options = {
        "key": "rzp_test_x6EYO4W3NIqb6X",  // Razorpay Key ID
        "order_id": order_id,  // Order ID generated from backend
        "handler": function (response) {
            // Handle successful payment here
            

            // Redirect or trigger API call to complete the order
            window.location.href = "/food/payment-success/?payment_id=" + response.razorpay_payment_id + "&order_id=" + order_id;
        }
    };

    var rzp1 = new Razorpay(options);
    rzp1.open();
};
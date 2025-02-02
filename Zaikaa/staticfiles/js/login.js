document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".login-form");
    const emailInput = document.getElementById("email");
    const errorMessage = document.createElement("p");

    errorMessage.style.color = "red";
    errorMessage.style.fontSize = "14px";
    errorMessage.style.marginTop = "5px";
    errorMessage.style.display = "none"; // Initially hidden
    emailInput.parentNode.appendChild(errorMessage);

    function validateEmail() {
        const email = emailInput.value.trim();
        if (!email.endsWith("@sakec.ac.in")) {
            errorMessage.textContent = "Use @sakec.ac.in mail only";
            errorMessage.style.display = "block"; // Show error message
            return false;
        } else {
            errorMessage.style.display = "none"; // Hide error if valid
            return true;
        }
    }

    // Continuous validation on input
    emailInput.addEventListener("input", validateEmail);

    // Prevent form submission if email is invalid
    form.addEventListener("submit", function (event) {
        if (!validateEmail()) {
            event.preventDefault(); // Stop form submission
        }
    });
});

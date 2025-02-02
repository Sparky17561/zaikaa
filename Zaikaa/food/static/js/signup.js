document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".signup-form");
    const emailInput = document.getElementById("email");
    const usernameInput = document.getElementById("username");
    const phoneInput = document.getElementById("phone");

    // Error message elements
    const emailError = document.createElement("p");
    const usernameError = document.createElement("p");
    const phoneError = document.createElement("p");

    [emailError, usernameError, phoneError].forEach(error => {
        error.style.color = "red";
        error.style.fontSize = "14px";
        error.style.marginTop = "5px";
        error.style.display = "none";
    });

    emailInput.parentNode.appendChild(emailError);
    usernameInput.parentNode.appendChild(usernameError);
    phoneInput.parentNode.appendChild(phoneError);

    // Email validation function
    function validateEmail() {
        const email = emailInput.value.trim();
        if (!email.endsWith("@sakec.ac.in")) {
            emailError.textContent = "Use @sakec.ac.in mail only";
            emailError.style.display = "block";
            return false;
        } else {
            emailError.style.display = "none";
            return true;
        }
    }

    // Username validation function (only letters and numbers allowed)
    function validateUsername() {
        const username = usernameInput.value.trim();
        const usernamePattern = /^[A-Za-z]+$/; // Only letters 
        if (!usernamePattern.test(username)) {
            usernameError.textContent = "Username can only contain letters (no special characters and numbers)";
            usernameError.style.display = "block";
            return false;
        } else {
            usernameError.style.display = "none";
            return true;
        }
    }

    // Phone number validation function (must be exactly 10 digits)
    function validatePhone() {
        const phone = phoneInput.value.trim();
        const phonePattern = /^[0-9]{10}$/; // Exactly 10 digits
        if (!phonePattern.test(phone)) {
            phoneError.textContent = "Phone number must be exactly 10 digits";
            phoneError.style.display = "block";
            return false;
        } else {
            phoneError.style.display = "none";
            return true;
        }
    }

    // Continuous validation on input
    emailInput.addEventListener("input", validateEmail);
    usernameInput.addEventListener("input", validateUsername);
    phoneInput.addEventListener("input", validatePhone);

    // Prevent form submission if any validation fails
    form.addEventListener("submit", function (event) {
        if (!validateEmail() || !validateUsername() || !validatePhone()) {
            event.preventDefault(); // Stop form submission
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const ease = "power4.inOut";

        // Page Load Animation (Hides Loader after Animation)
        revealTransition().then(() => {
            gsap.set(".block", { visibility: "hidden" });
        });

        // Click Navigation Animation
        document.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", (event) => {
                event.preventDefault();
                const href = link.getAttribute("href");

                if (href && !href.startsWith("#") && href !== window.location.pathname) {
                    animateTransition().then(() => {
                        window.location.href = href;
                    });
                }
            });
        });

        // Reveal Animation (Runs on Page Load)
        function revealTransition() {
            return new Promise((resolve) => {
                gsap.to(".block", { scaleY: 1 });
                gsap.to(".block", {
                    scaleY: 0,
                    duration: 1.5,
                    ease: ease,
                    onComplete: resolve
                });
            });
        }

        // Animate Loader when Navigating to a Different Page
        function animateTransition() {
            return new Promise((resolve) => {
                gsap.set(".block", { visibility: "visible", scaleY: 0 });
                gsap.to(".block", {
                    scaleY: 1,
                    duration: 1.5,
                    ease: ease,
                    onComplete: resolve
                });
            });
        }

  // Page load animations
  gsap.fromTo('.shop-container', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, delay:1 });
  gsap.fromTo('nav', { y: -10 }, { opacity: 1, y: 0, duration: 0.5, delay:1 });

  // Animate shop items when the page loads
  gsap.fromTo('.shop-item', { opacity: 0, y: 20 }, { opacity: 1, y: 0, stagger: 0.2, duration: 0.5, delay:1 });

  // Stagger effect for shop names when page loads
  gsap.fromTo('.shop-name', { opacity: 0, y: -20 }, { opacity: 1, y: 0, stagger: 0.2, duration: 0.5 , delay:1});

  // Checkbox toggle functionality
  document.querySelectorAll(".shops li").forEach(item => {
    item.addEventListener("click", function () {
      const checkbox = this.querySelector("input[type='checkbox']");
      checkbox.checked = !checkbox.checked;
      this.classList.toggle("selected", checkbox.checked);
    });
  });

  // Shop name click to show/hide menu with GSAP animation
  document.querySelectorAll('.shop-name').forEach(function(shopName) {
    shopName.addEventListener('click', function() {
      const arrow = shopName.querySelector('.arrow');
      const menu = shopName.nextElementSibling; // Corresponding <ul> element

      menu.classList.toggle('show');
      
      if (menu.classList.contains('show')) {
        gsap.fromTo(menu.querySelectorAll('li'), { opacity: 0, y: -20 }, { opacity: 1, y: 0, stagger: 0.1 });
        arrow.style.transform = 'rotate(180deg)';
      } else {
        gsap.to(menu.querySelectorAll('li'), { opacity: 0, y: -20, stagger: 0.1 });
        arrow.style.transform = 'rotate(0deg)';
      }
    });
  });

  

  // Handle Form Submission and Popup Validation
  const form = document.querySelector("form");
  const popup = document.getElementById("popup-message");
  const closePopup = document.getElementById("close-popup");

  form.addEventListener("submit", function(event) {
    const selectedItems = document.querySelectorAll("input[name='selected_items']:checked");

    if (selectedItems.length === 0) {
      event.preventDefault(); // Prevent form submission

      // Show popup message with GSAP animation
      popup.style.display = "block";
      gsap.fromTo(popup, { y: -100, opacity: 0 }, { y: -270, opacity: 1, duration: 0.5 });

      return false; // Stop form submission
    }else {
            event.preventDefault(); // Prevent immediate submission
            animateTransition().then(() => {
                form.submit(); // Submit after animation
            });
        }
  });

  // Close the popup when the button is clicked
  closePopup.addEventListener("click", function() {
    gsap.to(popup, {y: -100, opacity: 0, duration: 0.5, onComplete: function() {
      popup.style.display = "none";
    }});
  });
});

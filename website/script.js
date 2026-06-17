const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");
const contactForm = document.getElementById("contactForm");
const formStatus = document.getElementById("formStatus");

if (menuToggle && navLinks) {
  menuToggle.addEventListener("click", () => {
    navLinks.classList.toggle("active");
  });

  document.querySelectorAll(".nav-links a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("active");
    });
  });
}

if (contactForm) {
  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const vehicle = document.getElementById("vehicle").value.trim();
    const message = document.getElementById("message").value.trim();
    const company = document.getElementById("company").value.trim();

    formStatus.className = "form-status";
    formStatus.textContent = "";

    if (!name || !phone || !message) {
      formStatus.classList.add("error");
      formStatus.textContent = "Please fill in your name, phone number and message.";
      return;
    }

    try {
      const response = await fetch("http://192.168.1.230:8011/api/contact", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          phone,
          vehicle,
          message,
          company,
        }),
      });

      if (!response.ok) {
        throw new Error("Form submission failed");
      }

      formStatus.classList.add("success");
      formStatus.textContent = "Thank you. Your enquiry has been sent.";

      contactForm.reset();
    } catch (error) {
      formStatus.classList.add("error");
      formStatus.textContent = "Sorry, something went wrong. Please try again later.";
    }
  });
}
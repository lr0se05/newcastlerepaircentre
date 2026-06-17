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

    const submitButton = contactForm.querySelector("button[type='submit']");
    const formData = new FormData(contactForm);
    const images = document.getElementById("images").files;

    formStatus.className = "form-status";
    formStatus.textContent = "";

    if (images.length > 5) {
      formStatus.classList.add("error");
      formStatus.textContent = "Please upload no more than 5 images.";
      return;
    }

    try {
      submitButton.disabled = true;
      submitButton.textContent = "Sending...";

      const response = await fetch("http://192.168.1.230:8011/api/contact", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Form submission failed");
      }

      formStatus.classList.add("success");
      formStatus.textContent = "Thank you. Your enquiry has been sent.";

      contactForm.reset();
    } catch (error) {
      formStatus.classList.add("error");
      formStatus.textContent =
        error.message || "Sorry, something went wrong. Please try again later.";
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Send Enquiry";
    }
  });
}
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
  contactForm.addEventListener("submit", (event) => {
    const images = document.getElementById("images").files;

    formStatus.className = "form-status";
    formStatus.textContent = "";

    if (images.length > 5) {
      event.preventDefault();
      formStatus.classList.add("error");
      formStatus.textContent = "Please upload no more than 5 images.";
      return;
    }

    const submitButton = contactForm.querySelector("button[type='submit']");
    submitButton.disabled = true;
    submitButton.textContent = "Sending...";
  });
}
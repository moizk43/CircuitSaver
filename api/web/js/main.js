document.addEventListener("DOMContentLoaded", () => {
  const navbar = document.querySelector(".navbar");
  if (navbar) {
    window.addEventListener("scroll", () => {
      navbar.classList.toggle("scrolled", window.scrollY > 20);
    });
  }

  const toggleBtn = document.querySelector(".mobile-toggle");
  const mobileMenu = document.querySelector(".mobile-menu");
  if (toggleBtn && mobileMenu) {
    toggleBtn.addEventListener("click", () => mobileMenu.classList.toggle("open"));
  }

  document.querySelectorAll(".toggle-pw").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = btn.previousElementSibling;
      input.type = input.type === "password" ? "text" : "password";
    });
  });

  const scrollBtn = document.querySelector(".scroll-hint");
  if (scrollBtn) {
    scrollBtn.addEventListener("click", () => {
      document.getElementById("mission")?.scrollIntoView({ behavior: "smooth" });
    });
  }

  if (document.getElementById("globe-canvas")) initGlobe("globe-canvas");
  if (typeof initCounters === "function") initCounters();
  if (typeof initImpactSlider === "function") initImpactSlider();
});
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

let connectedStat = document.querySelector(".stat-value-connected");
let savedStat = document.querySelector(".stat-value-saved");
let co2Stat = document.querySelector(".stat-value-co2");
let uptimeStat = document.querySelector(".stat-value-uptime");

connectedStat.textContent = "0";
savedStat.textContent = "0";
co2Stat.textContent = "0";
uptimeStat.textContent = "99.9%";

numUsers = 


function updateStats() {
    connectedStat = 

    // Loops the function safely on the next screen refresh
    requestAnimationFrame(updatePhysics); 
}

// Start the loop
requestAnimationFrame(updatePhysics);

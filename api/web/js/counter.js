function animateCounter(el, to, duration = 2000, prefix = "", suffix = "", decimals = 0) {
  const from = 0;
  const separator = ",";
  let startTime = null;

  function step(timestamp) {
    if (!startTime) startTime = timestamp;
    const elapsed = timestamp - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = from + (to - from) * eased;
    const formatted = value.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, separator);
    el.textContent = `${prefix}${formatted}${suffix}`;
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function initCounters() {
  document.querySelectorAll("[data-counter]").forEach((el) => {
    const to = parseFloat(el.dataset.counter);
    const prefix = el.dataset.prefix || "";
    const suffix = el.dataset.suffix || "";
    const duration = parseInt(el.dataset.duration || "2000");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(el, to, duration, prefix, suffix);
          observer.disconnect();
        }
      });
    }, { threshold: 0.3 });
    observer.observe(el);
  });
}
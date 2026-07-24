function initGlobe(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const SIZE = 340;
  canvas.width = SIZE;
  canvas.height = SIZE;
  const cx = SIZE / 2, cy = SIZE / 2, R = 130;
  let rotation = 0;
  let particles = [];

  function spawnParticle() {
    const angle = Math.random() * Math.PI * 2;
    const r = R + (Math.random() - 0.5) * 30;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    const speed = 0.2 + Math.random() * 0.4;
    const tangentAngle = angle + Math.PI / 2 + (Math.random() - 0.5) * 0.6;
    particles.push({
      x, y, vx: speed * Math.cos(tangentAngle), vy: speed * Math.sin(tangentAngle),
      alpha: 1, size: 1.5 + Math.random() * 2, life: 0, maxLife: 60 + Math.random() * 80,
    });
  }

  function drawGlobe(rot) {
    const glow = ctx.createRadialGradient(cx, cy, R * 0.5, cx, cy, R * 1.4);
    glow.addColorStop(0, "rgba(86,209,109,0.06)");
    glow.addColorStop(1, "rgba(86,209,109,0)");
    ctx.fillStyle = glow;
    ctx.beginPath(); ctx.arc(cx, cy, R * 1.4, 0, Math.PI * 2); ctx.fill();

    const grad = ctx.createRadialGradient(cx - R * 0.3, cy - R * 0.3, R * 0.1, cx, cy, R);
    grad.addColorStop(0, "#f0fdf4"); grad.addColorStop(0.5, "#dcfce7"); grad.addColorStop(1, "#bbf7d0");
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fillStyle = grad; ctx.fill();

    ctx.save();
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.clip();
    ctx.strokeStyle = "rgba(86,209,109,0.18)"; ctx.lineWidth = 0.8;
    for (let i = 0; i < 12; i++) {
      const theta = (i / 12) * Math.PI * 2 + rot;
      ctx.beginPath();
      for (let lat = -Math.PI / 2; lat <= Math.PI / 2; lat += 0.05) {
        const projX = cx + R * Math.cos(lat) * Math.cos(theta);
        const projY = cy + R * Math.sin(lat);
        lat === -Math.PI / 2 ? ctx.moveTo(projX, projY) : ctx.lineTo(projX, projY);
      }
      ctx.stroke();
    }
    for (let j = 1; j < 6; j++) {
      const phi = (j / 6) * Math.PI - Math.PI / 2;
      const r2 = Math.abs(R * Math.cos(phi));
      const yOff = cy + R * Math.sin(phi);
      ctx.beginPath(); ctx.arc(cx, yOff, r2, 0, Math.PI * 2); ctx.stroke();
    }
    ctx.restore();

    ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(86,209,109,0.35)"; ctx.lineWidth = 1.5; ctx.stroke();
  }

  function drawParticles() {
    particles.forEach((p) => {
      const a = p.alpha * (1 - p.life / p.maxLife);
      ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(86,209,109,${a * 0.8})`; ctx.fill();
    });
  }

  function animate() {
    ctx.clearRect(0, 0, SIZE, SIZE);
    rotation += 0.004;
    drawGlobe(rotation);
    if (Math.random() < 0.3) spawnParticle();
    particles = particles.filter((p) => {
      p.life++; p.x += p.vx; p.y += p.vy;
      return p.life < p.maxLife;
    });
    drawParticles();
    requestAnimationFrame(animate);
  }
  animate();
}
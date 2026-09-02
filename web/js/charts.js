window.CSCharts = {};

window.CSCharts.demandStory = function (canvas, captionEl, dotEls) {
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();
  window.addEventListener("resize", resize);

  const points = 60;
  const baseline = Array.from({ length: points }, (_, i) => {
    const t = i / points;
    const evening = Math.exp(-Math.pow((t - 0.72) / 0.07, 2)) * 0.85;
    const morning = Math.exp(-Math.pow((t - 0.32) / 0.09, 2)) * 0.3;
    return 0.28 + morning + evening;
  });
  const peakStart = 0.63, peakEnd = 0.82;

  const shaved = baseline.map((v, i) => {
    const t = i / points;
    if (t >= peakStart && t <= peakEnd) {
      const dip = Math.exp(-Math.pow((t - 0.72) / 0.07, 2)) * 0.32;
      return v - dip;
    }
    return v;
  });

  const captions = [
    { t: 0, text: 'Baseline demand is <span class="em">predicted</span> for every connected household throughout the day.' },
    { t: 0.35, text: 'As the afternoon peak approaches, Circuit Saver identifies the transformer under <span class="em">rising stress</span>.' },
    { t: 0.65, text: 'The Swarm Engine <span class="em">allocates</span> small, fair load shifts across flexible households.' },
    { t: 1, text: 'The peak is <span class="em">flattened</span> — no new plant needed, and every restart is staggered to prevent rebound.' },
  ];

  let frame = 0;
  const totalFrames = 260;

  function draw() {
    const w = canvas.getBoundingClientRect().width;
    const h = canvas.getBoundingClientRect().height;
    ctx.clearRect(0, 0, w, h);

    const progress = frame / totalFrames;
    const padX = 8, padY = 16;
    const plotW = w - padX * 2, plotH = h - padY * 2;
    const maxV = Math.max(...baseline) * 1.1;

    function xy(i, v) {
      const x = padX + (i / (points - 1)) * plotW;
      const y = padY + plotH - (v / maxV) * plotH;
      return [x, y];
    }

    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    for (let g = 0; g <= 4; g++) {
      const y = padY + (plotH / 4) * g;
      ctx.beginPath(); ctx.moveTo(padX, y); ctx.lineTo(w - padX, y); ctx.stroke();
    }

    const [xPeakStart] = xy(Math.floor(peakStart * points), 0);
    const [xPeakEnd] = xy(Math.floor(peakEnd * points), 0);
    if (progress > 0.25) {
      const alpha = Math.min(1, (progress - 0.25) / 0.2) * 0.16;
      ctx.fillStyle = `rgba(217,119,6,${alpha})`;
      ctx.fillRect(xPeakStart, padY, xPeakEnd - xPeakStart, plotH);
    }

    const visibleCount = Math.max(2, Math.floor(points * Math.min(1, progress / 0.9)));

    ctx.strokeStyle = "rgba(148,163,184,0.55)";
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < visibleCount; i++) {
      const [x, y] = xy(i, baseline[i]);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    if (progress > 0.5) {
      const shaveReveal = Math.min(1, (progress - 0.5) / 0.5);
      const grad = ctx.createLinearGradient(0, 0, w, 0);
      grad.addColorStop(0, "#34c759");
      grad.addColorStop(1, "#1fa34a");
      ctx.strokeStyle = grad;
      ctx.lineWidth = 3;
      ctx.beginPath();
      const shaveCount = Math.max(2, Math.floor(visibleCount * shaveReveal));
      for (let i = 0; i < shaveCount; i++) {
        const [x, y] = xy(i, shaved[i]);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.stroke();
    }

    if (visibleCount < points) {
      const [x, y] = xy(visibleCount - 1, baseline[visibleCount - 1]);
      ctx.fillStyle = "#94a3b8";
      ctx.beginPath(); ctx.arc(x, y, 3.5, 0, Math.PI * 2); ctx.fill();
    }

    frame += 1;
    if (frame > totalFrames) frame = 0;

    const activeCaption = [...captions].reverse().find((c) => progress >= c.t) || captions[0];
    if (captionEl && captionEl.dataset.current !== activeCaption.text) {
      captionEl.innerHTML = activeCaption.text;
      captionEl.dataset.current = activeCaption.text;
    }
    if (dotEls) {
      const activeIdx = captions.indexOf(activeCaption);
      dotEls.forEach((d, i) => d.classList.toggle("active", i === activeIdx));
    }

    requestAnimationFrame(draw);
  }

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) {
    frame = totalFrames;
    draw();
  } else {
    requestAnimationFrame(draw);
  }
};

window.CSCharts.priorityScatter = function (canvas, rows) {
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const w = rect.width, h = rect.height;
  ctx.clearRect(0, 0, w, h);

  if (!rows || !rows.length) return;

  const padL = 40, padB = 28, padT = 12, padR = 12;
  const plotW = w - padL - padR, plotH = h - padT - padB;
  const maxAlloc = Math.max(...rows.map((r) => r.allocated_kw || 0), 1);

  ctx.strokeStyle = "#e2e8f0";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padL, padT); ctx.lineTo(padL, padT + plotH); ctx.lineTo(padL + plotW, padT + plotH);
  ctx.stroke();

  ctx.fillStyle = "#94a3b8";
  ctx.font = "11px monospace";
  ctx.fillText("0", padL - 4, padT + plotH + 14);
  ctx.fillText("1.0", padL + plotW - 18, padT + plotH + 14);
  ctx.save();
  ctx.translate(12, padT + plotH / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("Allocated kW", -30, 0);
  ctx.restore();
  ctx.fillText("Priority score", padL + plotW / 2 - 30, padT + plotH + 14);

  rows.forEach((r) => {
    const x = padL + (r.priority_score || 0) * plotW;
    const y = padT + plotH - ((r.allocated_kw || 0) / maxAlloc) * plotH;
    ctx.beginPath();
    ctx.fillStyle = r.was_capped ? "#d97706" : "#34c759";
    ctx.globalAlpha = 0.85;
    ctx.arc(x, y, 4.5, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.globalAlpha = 1;
};

window.CSCharts.featureImportance = function (canvas, features) {
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const w = rect.width, h = rect.height;
  ctx.clearRect(0, 0, w, h);

  const sorted = [...features].sort((a, b) => b.importance - a.importance);
  const rowH = h / sorted.length;
  const maxImp = Math.max(...sorted.map((f) => f.importance));
  const labelW = 168;

  sorted.forEach((f, i) => {
    const y = i * rowH + rowH * 0.22;
    const barH = rowH * 0.56;
    const barMaxW = w - labelW - 50;
    const barW = (f.importance / maxImp) * barMaxW;

    ctx.fillStyle = "#475569";
    ctx.font = "12px Inter, sans-serif";
    ctx.textBaseline = "middle";
    ctx.fillText(f.label, 0, y + barH / 2);

    ctx.fillStyle = i === 0 ? "#34c759" : "#cbd5e1";
    ctx.fillRect(labelW, y, barW, barH);

    ctx.fillStyle = "#0f1520";
    ctx.font = "11px monospace";
    ctx.fillText(`${(f.importance * 100).toFixed(1)}%`, labelW + barW + 8, y + barH / 2);
  });
};

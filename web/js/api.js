window.CSFormat = {
  currency(n) {
    const v = Number(n) || 0;
    return v.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 });
  },
  kw(n, decimals = 1) {
    const v = Number(n) || 0;
    return `${v.toFixed(decimals)}`;
  },
  pct(n, decimals = 0) {
    const v = Number(n) || 0;
    return `${v.toFixed(decimals)}`;
  },
  co2(n) {
    const v = Number(n) || 0;
    return `${v.toFixed(1)}`;
  },
  priorityScore(n) {
    return Math.round((Number(n) || 0) * 100);
  },
  timeHHMMSS(date = new Date()) {
    return date.toLocaleTimeString("en-US", { hour12: false });
  },
  statusTone(status) {
    if (!status) return "normal";
    const s = String(status).toLowerCase();
    if (s.includes("crit")) return "critical";
    if (s.includes("high") || s.includes("elevat")) return "elevated";
    return "normal";
  },
};

window.renderLoadGauge = function (pct, opts = {}) {
  const clamped = Math.max(0, Math.min(100, Number(pct) || 0));
  let tone = "normal";
  if (clamped >= 85) tone = "critical";
  else if (clamped >= 65) tone = "elevated";
  const label = opts.label !== undefined ? opts.label : `${clamped.toFixed(1)}%`;
  return `
    <div class="load-gauge" role="img" aria-label="Transformer load ${clamped.toFixed(1)} percent, ${tone}">
      <div class="load-gauge-track">
        <div class="load-gauge-fill load-gauge-fill--${tone}" style="width:${clamped}%;"></div>
      </div>
      <span class="load-gauge-label">${label}</span>
    </div>`;
};

window.renderStatusBadge = function (status) {
  const tone = window.CSFormat.statusTone(status);
  const label = String(status || "normal").replace(/_/g, " ");
  return `<span class="badge badge-${tone}"><span class="badge-dot"></span>${label}</span>`;
};

window.showAlert = function (elId, type, message) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.className = `alert alert-${type} show`;
  const textEl = el.querySelector("[data-alert-text]");
  if (textEl) textEl.textContent = message;
  else el.textContent = message;
};
window.hideAlert = function (elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.classList.remove("show");
};

window.createLiveConnection = function ({ onMessage, onStatusChange, onFallbackPoll, pollIntervalMs = 15000 }) {
  let socket = null;
  let reconnectAttempts = 0;
  let pollTimer = null;
  let closedByUser = false;

  function setStatus(status) {
    if (onStatusChange) onStatusChange(status);
  }

  function startPolling() {
    if (pollTimer) return;
    if (onFallbackPoll) {
      onFallbackPoll();
      pollTimer = setInterval(onFallbackPoll, pollIntervalMs);
    }
  }
  function stopPolling() {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  }

  function connect() {
    if (closedByUser) return;
    setStatus(reconnectAttempts === 0 ? "connecting" : "reconnecting");
    let url;
    try {
      url = `${WS_BASE}/ws/dashboard`;
      socket = new WebSocket(url);
    } catch (e) {
      setStatus("offline");
      startPolling();
      return;
    }

    socket.onopen = () => {
      reconnectAttempts = 0;
      setStatus("live");
      stopPolling();
    };

    socket.onmessage = (event) => {
      let data;
      try { data = JSON.parse(event.data); } catch (e) { data = event.data; }
      if (onMessage) onMessage(data);
    };

    socket.onclose = () => {
      if (closedByUser) return;
      setStatus("reconnecting");
      startPolling();
      reconnectAttempts += 1;
      const delay = Math.min(1000 * 2 ** Math.min(reconnectAttempts, 5), 20000);
      setTimeout(connect, delay);
    };

    socket.onerror = () => {
      setStatus("offline");
    };
  }

  connect();

  return {
    close() {
      closedByUser = true;
      stopPolling();
      if (socket) socket.close();
    },
  };
};

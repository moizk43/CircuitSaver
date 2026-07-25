const API_BASE = window.API_BASE || "http://127.0.0.1:8000";
const SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY || "";

window.signUpUser = async function (email, password) {
  const res = await fetch(`${API_BASE}/api/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Signup failed.");
  return data;
};

window.signInUser = async function (email, password) {
  const res = await fetch(`${API_BASE}/api/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Sign in failed.");
  return data;
};

window.setSession = function (email, token) {
  localStorage.setItem("verdant_email", email || "");
  localStorage.setItem("verdant_token", token || "");
};

window.getSession = function () {
  return {
    email: localStorage.getItem("verdant_email"),
    token: localStorage.getItem("verdant_token"),
  };
};

window.clearSession = function () {
  localStorage.removeItem("verdant_email");
  localStorage.removeItem("verdant_token");
};

window.isAdminEmail = function (email) {
  if (!email) return false;
  const ADMIN_EMAILS = ["moizkothawala@gmail.com"];
  return ADMIN_EMAILS.includes(String(email).toLowerCase());
};

window.verifySession = async function () {
  const { email, token } = window.getSession();

  if (!email || !token) {
    return null;
  }

  if (!SUPABASE_ANON_KEY || SUPABASE_ANON_KEY === "your_supabase_anon_key_here") {
    return email;
  }

  try {
    const res = await fetch(`${API_BASE}/auth/v1/user`, {
      headers: {
        Authorization: `Bearer ${token}`,
        apikey: SUPABASE_ANON_KEY,
      },
    });

    if (!res.ok) {
      return email;
    }

    const user = await res.json();
    const verifiedEmail = user?.email || email;

    if (!verifiedEmail) {
      return email;
    }

    window.setSession(verifiedEmail, token);
    return verifiedEmail;
  } catch (err) {
    return email;
  }
};

window.authFetch = async function (path, options = {}) {
  const verifiedEmail = await window.verifySession();
  const { token } = window.getSession();

  if (!verifiedEmail || !token) {
    throw new Error("Your session has expired. Please sign in again.");
  }

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
    Authorization: `Bearer ${token}`,
  };

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed.");
  return data;
};

window.renderAuthNav = async function () {
  const slot = document.getElementById("nav-auth-slot");
  const mobileSlot = document.getElementById("nav-auth-slot-mobile");

  if (!slot && !mobileSlot) return;

  const verifiedEmail = await window.verifySession();

  const loggedOutHTML = `
    <a href="sign-in.html" class="btn btn-ghost btn-sm">Sign In</a>
    <a href="get-started.html" class="btn btn-primary btn-sm">Get Started</a>
  `;

  const loggedOutMobileHTML = `
    <a href="sign-in.html" class="btn btn-ghost btn-sm btn-full">Sign In</a>
    <a href="get-started.html" class="btn btn-primary btn-sm btn-full">Get Started</a>
  `;

  if (!verifiedEmail) {
    if (slot) slot.innerHTML = loggedOutHTML;
    if (mobileSlot) mobileSlot.innerHTML = loggedOutMobileHTML;
    return;
  }

  const destination = window.isAdminEmail(verifiedEmail) ? "admin.html" : "dashboard.html";

  if (slot) {
    slot.innerHTML = `
      <a href="${destination}" class="btn btn-secondary btn-sm">Dashboard</a>
      <a href="#" id="nav-sign-out" class="btn btn-ghost btn-sm">Sign out</a>
    `;
  }

  if (mobileSlot) {
    mobileSlot.innerHTML = `
      <a href="${destination}" class="btn btn-secondary btn-sm btn-full">Dashboard</a>
      <a href="#" id="nav-sign-out-mobile" class="btn btn-ghost btn-sm btn-full">Sign out</a>
    `;
  }

  const signOutHandler = (e) => {
    e.preventDefault();
    window.clearSession();
    window.location.href = "sign-in.html";
  };

  const signOutBtn = document.getElementById("nav-sign-out");
  if (signOutBtn) signOutBtn.addEventListener("click", signOutHandler);

  const signOutBtnMobile = document.getElementById("nav-sign-out-mobile");
  if (signOutBtnMobile) signOutBtnMobile.addEventListener("click", signOutHandler);
};

document.addEventListener("DOMContentLoaded", () => {
  if (window.renderAuthNav) {
    window.renderAuthNav();
  }
});
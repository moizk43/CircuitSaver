/**
 * auth.js — Circuit Saver authentication & session utilities
 *
 * Contract preserved from the original implementation:
 *   window.signUpUser(email, password)  -> POST /api/signup
 *   window.signInUser(email, password)  -> POST /api/signin
 *   window.setSession(email, token)
 *   window.getSession() -> { email, token }
 *   window.clearSession()
 *   window.verifySession() -> resolves to verified email, or redirects to sign-in.html
 *   window.authFetch(path, options) -> fetch() against API_BASE with Authorization header
 *   window.isAdminEmail(email) -> boolean
 *
 * NOTE: session storage keys were renamed from the legacy "verdant_*" keys to
 * "circuitsaver_*". This invalidates any existing local session (one-time
 * re-login) but does not change the API contract with the backend.
 */

const API_BASE = window.API_BASE || "http://127.0.0.1:8000";
const WS_BASE = window.WS_BASE || API_BASE.replace(/^http/, "ws");
const SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY || "";

const ADMIN_EMAILS = ["moizkothawala@gmail.com"];

window.isAdminEmail = function (email) {
  if (!email) return false;
  return ADMIN_EMAILS.includes(String(email).toLowerCase());
};

window.setSession = function (email, token) {
  localStorage.setItem("circuitsaver_email", email || "");
  localStorage.setItem("circuitsaver_token", token || "");
};

window.getSession = function () {
  return {
    email: localStorage.getItem("circuitsaver_email"),
    token: localStorage.getItem("circuitsaver_token"),
  };
};

window.clearSession = function () {
  localStorage.removeItem("circuitsaver_email");
  localStorage.removeItem("circuitsaver_token");
};

window.signUpUser = async function (email, password) {
  const res = await fetch(`${API_BASE}/api/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Signup failed. Please try again.");
  return data;
};

window.signInUser = async function (email, password) {
  const res = await fetch(`${API_BASE}/api/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Incorrect email or password.");
  return data;
};

window.signOut = function () {
  window.clearSession();
  window.location.href = "sign-in.html";
};

window.verifySession = async function () {
  const { email, token } = window.getSession();
  if (!email || !token) {
    window.location.href = "sign-in.html";
    return null;
  }
  return email;
};

window.authFetch = async function (path, options = {}) {
  const verifiedEmail = await window.verifySession();
  if (!verifiedEmail) return null;
  const { token } = window.getSession();

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    },
  });

  if (res.status === 401 || res.status === 403) {
    window.clearSession();
    window.location.href = "sign-in.html";
    return null;
  }

  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    const err = new Error(errBody.detail || `Request failed (${res.status})`);
    err.status = res.status;
    throw err;
  }

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res.text();
};

const API_BASE = "http://127.0.0.1:8000";

async function signUpUser(email, password) {
  const res = await fetch(`${API_BASE}/api/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Signup failed.");
  return data;
}

async function signInUser(email, password) {
  const res = await fetch(`${API_BASE}/api/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Sign in failed.");
  return data;
}

function setSession(email, token) {
  localStorage.setItem("verdant_email", email);
  localStorage.setItem("verdant_token", token || "");
}

function getSession() {
  return {
    email: localStorage.getItem("verdant_email"),
    token: localStorage.getItem("verdant_token"),
  };
}

function clearSession() {
  localStorage.removeItem("verdant_email");
  localStorage.removeItem("verdant_token");
}
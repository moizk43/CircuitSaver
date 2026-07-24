const USERS_KEY = "verdant_users";
const SESSION_KEY = "verdant_session";

function getUsers() {
  return JSON.parse(localStorage.getItem(USERS_KEY) || "{}");
}
function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}
function userExists(username) {
  return Object.keys(getUsers()).some(
    (u) => u.toLowerCase() === username.toLowerCase()
  );
}
function createUser(username, password) {
  const users = getUsers();
  users[username] = password;
  saveUsers(users);
}
function validateUser(username, password) {
  const users = getUsers();
  return users[username] === password;
}
function setSession(username) {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ username }));
}
function getSession() {
  const raw = localStorage.getItem(SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}
function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}
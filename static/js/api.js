const BASE = "/api/v1";

function getToken() {
  return localStorage.getItem("forzaToken");
}

function setToken(token) {
  localStorage.setItem("forzaToken", token);
}

function clearToken() {
  localStorage.removeItem("forzaToken");
}

function isLoggedIn() {
  return !!getToken();
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

async function fetchStats() {
  return apiFetch("/imagenes/stats");
}

async function fetchImagenes(juego = null, skip = 0, limit = 20) {
  const params = new URLSearchParams({ skip, limit });
  if (juego) params.set("juego", juego);
  return apiFetch(`/imagenes?${params}`);
}

async function fetchImagen(id) {
  return apiFetch(`/imagenes/${id}`);
}

async function uploadImagen(formData) {
  const token = getToken();
  const res = await fetch(`${BASE}/imagenes`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function deleteImagen(id) {
  return apiFetch(`/imagenes/${id}`, { method: "DELETE" });
}

async function login(username, password) {
  const body = new URLSearchParams({ username, password });
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error" }));
    throw new Error(err.detail || "Error de login");
  }
  const data = await res.json();
  setToken(data.access_token);
  return data;
}

async function register(username, email, password) {
  const res = await fetch(`${BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error" }));
    throw new Error(err.detail || "Error de registro");
  }
  const data = await res.json();
  setToken(data.access_token);
  return data;
}

async function fetchMe() {
  return apiFetch("/auth/me");
}

function requireAuth(redirectTo = "/login.html") {
  if (!isLoggedIn()) {
    window.location.href = redirectTo;
  }
}

function updateNavAuth() {
  const navAuth = document.getElementById("nav-auth");
  if (!navAuth) return;
  if (isLoggedIn()) {
    navAuth.innerHTML = `
      <a href="/subir.html">Subir</a>
      <a href="#" id="btn-logout">Cerrar sesión</a>
    `;
    document.getElementById("btn-logout")?.addEventListener("click", (e) => {
      e.preventDefault();
      clearToken();
      window.location.href = "/index.html";
    });
  } else {
    navAuth.innerHTML = `
      <a href="/login.html">Login</a>
      <a href="/registro.html" class="nav-cta">Registro</a>
    `;
  }
}

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

function extractDetail(err) {
  if (!err.detail) return "Error desconocido";
  if (typeof err.detail === "string") return err.detail;
  if (Array.isArray(err.detail)) return err.detail.map(e => e.msg).join(" · ");
  return "Error desconocido";
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(extractDetail(err));
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

async function updateImagen(id, data) {
  return apiFetch(`/imagenes/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

async function getLikes(imagenId) {
  return apiFetch(`/social/imagenes/${imagenId}/likes`);
}

async function toggleLike(imagenId) {
  return apiFetch(`/social/imagenes/${imagenId}/like`, { method: "POST" });
}

async function toggleGuardado(imagenId) {
  return apiFetch(`/social/imagenes/${imagenId}/guardar`, { method: "POST" });
}

async function getComentarios(imagenId) {
  return apiFetch(`/social/imagenes/${imagenId}/comentarios`);
}

async function addComentario(imagenId, contenido) {
  return apiFetch(`/social/imagenes/${imagenId}/comentarios`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contenido }),
  });
}

async function deleteComentario(comentarioId) {
  return apiFetch(`/social/comentarios/${comentarioId}`, { method: "DELETE" });
}

async function reportarComentario(comentarioId, motivo = null) {
  return apiFetch(`/social/comentarios/${comentarioId}/reportar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ motivo }),
  });
}

async function getMisGuardados() {
  return apiFetch("/social/mis-guardados");
}

async function reaccionar(comentarioId, emoji) {
  return apiFetch(`/social/comentarios/${comentarioId}/reaccionar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emoji }),
  });
}

function timeAgo(isoDate) {
  const diff = (Date.now() - new Date(isoDate)) / 1000;
  if (diff < 60)     return "ahora";
  if (diff < 3600)   return `${Math.floor(diff / 60)}min`;
  if (diff < 86400)  return `${Math.floor(diff / 3600)}h`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d`;
  return new Date(isoDate).toLocaleDateString("es-ES", { day: "2-digit", month: "short" });
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
    throw new Error(extractDetail(err));
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
    fetchMe().then(me => {
      navAuth.innerHTML = `
        <a href="/perfil.html?u=${me.username}" class="nav-avatar-link" title="Mi perfil">
          <img src="/img/default-avatar.svg" alt="Perfil" class="nav-avatar" id="nav-avatar-img" />
        </a>
        <a href="/subir.html">Subir</a>
        <a href="#" id="btn-logout">Cerrar sesión</a>
      `;
      apiFetch(`/usuarios/${me.username}`).then(perfil => {
        if (perfil.avatar_url) document.getElementById("nav-avatar-img").src = perfil.avatar_url;
      }).catch(() => {});
      document.getElementById("btn-logout")?.addEventListener("click", (e) => {
        e.preventDefault(); clearToken(); window.location.href = "/index.html";
      });
    }).catch(() => {
      navAuth.innerHTML = `
        <a href="/subir.html">Subir</a>
        <a href="#" id="btn-logout">Cerrar sesión</a>
      `;
      document.getElementById("btn-logout")?.addEventListener("click", (e) => {
        e.preventDefault(); clearToken(); window.location.href = "/index.html";
      });
    });
    return;
  } else {
    navAuth.innerHTML = `
      <a href="/login.html">Login</a>
      <a href="/registro.html" class="nav-cta">Registro</a>
    `;
  }
}

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

async function toggleSeguir(username) {
  return apiFetch(`/social/usuarios/${username}/seguir`, { method: "POST" });
}

async function getSeguidores(username) {
  return apiFetch(`/social/usuarios/${username}/seguidores`);
}

async function getSiguiendo(username) {
  return apiFetch(`/social/usuarios/${username}/siguiendo`);
}

async function toggleFavoritoUsuario(username) {
  return apiFetch(`/social/usuarios/${username}/favorito`, { method: "POST" });
}

async function getMisFavoritosUsuarios() {
  return apiFetch("/social/mis-favoritos-usuarios");
}

async function cambiarPassword(passwordActual, nuevaPassword) {
  return apiFetch("/auth/cambiar-password", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password_actual: passwordActual, nueva_password: nuevaPassword }),
  });
}

async function eliminarCuenta(password) {
  return apiFetch("/auth/cuenta", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
}

function requireAuth(redirectTo = "/login.html") {
  if (!isLoggedIn()) {
    window.location.href = redirectTo;
  }
}

async function getNotificaciones() {
  return apiFetch("/notificaciones");
}
async function countNotifNoLeidas() {
  return apiFetch("/notificaciones/no-leidas");
}
async function leerTodasNotificaciones() {
  return apiFetch("/notificaciones/leer-todas", { method: "POST" });
}
async function getConversaciones() {
  return apiFetch("/mensajes/conversaciones");
}
async function getMensajes(username) {
  return apiFetch(`/mensajes/${username}`);
}
async function enviarMensaje(username, contenido) {
  return apiFetch(`/mensajes/${username}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contenido }),
  });
}
async function getMensajesNoLeidos() {
  return apiFetch("/mensajes/no-leidos");
}

let _currentUsername = null;

function updateNavAuth() {
  const navAuth = document.getElementById("nav-auth");
  if (!navAuth) return;
  if (isLoggedIn()) {
    fetchMe().then(me => {
      _currentUsername = me.username;
      navAuth.innerHTML = `
        <li class="nav-msg-wrap">
          <a href="/mensajes.html" class="nav-msg-btn" title="Mensajes">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          </a>
          <span class="nav-msg-badge" id="nav-msg-badge" style="display:none"></span>
        </li>
        <li class="nav-bell-wrap">
          <button class="nav-bell-btn" id="nav-bell-btn" title="Notificaciones">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            <span class="nav-bell-badge" id="nav-bell-badge" style="display:none"></span>
          </button>
          <div class="nav-bell-dropdown" id="nav-bell-dropdown">
            <div class="nav-bell-header">Notificaciones</div>
            <div id="nav-bell-list"><div class="notif-empty">Cargando...</div></div>
          </div>
        </li>
        <li>
          <a href="/perfil.html?u=${me.username}" class="nav-avatar-link" title="Mi perfil">
            <img src="/img/default-avatar.svg" alt="Perfil" class="nav-avatar" id="nav-avatar-img" />
          </a>
        </li>
        <li><a href="/subir.html">Subir</a></li>
        <li><a href="#" id="btn-logout">Cerrar sesión</a></li>
      `;
      apiFetch(`/usuarios/${me.username}`).then(perfil => {
        if (perfil.avatar_url) document.getElementById("nav-avatar-img").src = perfil.avatar_url;
      }).catch(() => {});
      document.getElementById("btn-logout")?.addEventListener("click", (e) => {
        e.preventDefault(); clearToken(); window.location.href = "/index.html";
      });

      _initNavBell();
      _initNavMsgBadge();
      _initChatWidget();
    }).catch(() => {
      navAuth.innerHTML = `
        <li><a href="/subir.html">Subir</a></li>
        <li><a href="#" id="btn-logout">Cerrar sesión</a></li>
      `;
      document.getElementById("btn-logout")?.addEventListener("click", (e) => {
        e.preventDefault(); clearToken(); window.location.href = "/index.html";
      });
    });
    return;
  } else {
    navAuth.innerHTML = `
      <li><a href="/login.html">Login</a></li>
      <li><a href="/registro.html" class="nav-cta">Registro</a></li>
    `;
  }
}

function _initNavMsgBadge() {
  getMensajesNoLeidos().then(d => {
    const badge = document.getElementById("nav-msg-badge");
    if (!badge) return;
    if (d.count > 0) {
      badge.textContent = d.count > 9 ? "9+" : d.count;
      badge.style.display = "flex";
    }
  }).catch(() => {});
}

function _initNavBell() {
  const bellBtn = document.getElementById("nav-bell-btn");
  const dropdown = document.getElementById("nav-bell-dropdown");
  const badge = document.getElementById("nav-bell-badge");
  if (!bellBtn) return;

  countNotifNoLeidas().then(d => {
    if (d.count > 0) {
      badge.textContent = d.count > 9 ? "9+" : d.count;
      badge.style.display = "flex";
    }
  }).catch(() => {});

  bellBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = dropdown.classList.toggle("open");
    if (open) {
      badge.style.display = "none";
      leerTodasNotificaciones().catch(() => {});
      getNotificaciones().then(notifs => {
        const list = document.getElementById("nav-bell-list");
        if (!notifs.length) { list.innerHTML = '<div class="notif-empty">Sin notificaciones</div>'; return; }
        list.innerHTML = notifs.map(n => {
          const texto = n.tipo === "like"
            ? `<strong>${n.from_username}</strong> ha dado like a tu foto`
            : n.tipo;
          const href = n.imagen_id ? `/galeria.html?id=${n.imagen_id}` : "#";
          return `<a class="notif-item ${n.leida ? "" : "unread"}" href="${href}">
            <img class="notif-avatar" src="/img/default-avatar.svg" alt="" onerror="this.src='/img/default-avatar.svg'" />
            <div>
              <div class="notif-text">${texto}</div>
              <div class="notif-time">${timeAgo(n.created_at)}</div>
            </div>
          </a>`;
        }).join("");
        notifs.forEach((n, i) => {
          if (n.from_username) {
            apiFetch(`/usuarios/${n.from_username}`).then(p => {
              const imgs = document.querySelectorAll(".notif-avatar");
              if (imgs[i] && p.avatar_url) imgs[i].src = p.avatar_url;
            }).catch(() => {});
          }
        });
      }).catch(() => {});
    }
  });

  document.addEventListener("click", (e) => {
    if (!dropdown.contains(e.target) && e.target !== bellBtn) {
      dropdown.classList.remove("open");
    }
  });
}

function _initChatWidget() {
  if (document.getElementById("chat-widget")) return;

  const el = document.createElement("div");
  el.id = "chat-widget";
  el.className = "chat-widget";
  el.innerHTML = `
    <div class="chat-widget-header">
      <img class="cw-avatar" id="cw-avatar" src="/img/default-avatar.svg" alt="" />
      <a class="cw-username" id="cw-username" href="#"></a>
      <div class="cw-header-actions">
        <a id="cw-fullpage" class="cw-icon-btn" href="/mensajes.html" title="Ver en pantalla completa">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
        </a>
        <button class="cw-icon-btn" id="cw-close" title="Cerrar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </div>
    <div class="chat-widget-messages" id="cw-messages"><div class="cw-empty">Cargando...</div></div>
    <div class="chat-widget-input">
      <textarea id="cw-input" placeholder="Escribe un mensaje..." rows="1"></textarea>
      <button class="cw-send-btn" id="cw-send">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </button>
    </div>
  `;
  document.body.appendChild(el);

  let _cwUser = null;
  let _cwPollInterval = null;

  function escHtml(s) {
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g,"<br>");
  }

  function renderMessages(msgs) {
    const box = document.getElementById("cw-messages");
    if (!msgs || !msgs.length) {
      box.innerHTML = '<div class="cw-empty">Empieza la conversación</div>';
      return;
    }
    const atBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 60;
    box.innerHTML = msgs.map(m => {
      const mine = m.autor_username === _currentUsername;
      return `<div class="cw-bubble-wrap ${mine ? "mine" : "theirs"}"><div class="cw-bubble">${escHtml(m.contenido)}</div></div>`;
    }).join("");
    if (atBottom) box.scrollTop = box.scrollHeight;
  }

  async function loadMessages() {
    if (!_cwUser) return;
    try {
      const msgs = await getMensajes(_cwUser);
      renderMessages(msgs);
    } catch {}
  }

  async function sendMsg() {
    const input = document.getElementById("cw-input");
    const text = input.value.trim();
    if (!text || !_cwUser) return;
    input.value = "";
    input.style.height = "auto";
    try {
      await enviarMensaje(_cwUser, text);
      await loadMessages();
      const box = document.getElementById("cw-messages");
      box.scrollTop = box.scrollHeight;
    } catch {}
  }

  document.getElementById("cw-close").addEventListener("click", () => {
    el.classList.remove("open");
    clearInterval(_cwPollInterval);
    _cwPollInterval = null;
    _cwUser = null;
  });

  const input = document.getElementById("cw-input");
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMsg(); }
  });
  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 80) + "px";
  });
  document.getElementById("cw-send").addEventListener("click", sendMsg);

  window.openChatWidget = async function(username) {
    clearInterval(_cwPollInterval);
    _cwUser = username;

    document.getElementById("cw-username").textContent = username;
    document.getElementById("cw-username").href = `/perfil.html?u=${username}`;
    document.getElementById("cw-fullpage").href = `/mensajes.html?u=${username}`;
    document.getElementById("cw-avatar").src = "/img/default-avatar.svg";
    document.getElementById("cw-messages").innerHTML = '<div class="cw-empty">Cargando...</div>';
    document.getElementById("cw-input").value = "";
    document.getElementById("cw-input").style.height = "auto";

    el.classList.add("open");

    apiFetch(`/usuarios/${username}`).then(p => {
      if (p.avatar_url) document.getElementById("cw-avatar").src = p.avatar_url;
    }).catch(() => {});

    await loadMessages();
    const box = document.getElementById("cw-messages");
    box.scrollTop = box.scrollHeight;

    _cwPollInterval = setInterval(loadMessages, 4000);
  };
}

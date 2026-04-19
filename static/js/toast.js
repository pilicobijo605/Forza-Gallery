function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const icons = { success: "✅", error: "❌", info: "ℹ️", warning: "⚠️" };
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type] || "ℹ️"}</span><span>${message}</span>`;
  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add("toast-show"));

  const hide = () => {
    toast.classList.replace("toast-show", "toast-hide");
    toast.addEventListener("transitionend", () => toast.remove(), { once: true });
  };

  setTimeout(hide, 3500);
  toast.addEventListener("click", hide);
}

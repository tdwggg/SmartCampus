const apiBase = window.location.origin.includes("localhost") ||
                window.location.origin.includes("127.0.0.1")
  ? window.location.origin
  : "http://localhost:5000";

function imgPath(fileName) {
  if (window.location.protocol === "file:") {
    return "../Img/mp4/" + fileName;
  }
  return "/img/" + fileName;
}

async function apiGet(path) {
  const res = await fetch(apiBase + path);
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || "API error: " + res.status);
  }
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(apiBase + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function apiPut(path, body) {
  const res = await fetch(apiBase + path, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function apiDelete(path) {
  const res = await fetch(apiBase + path, { method: "DELETE" });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || "Request failed");
  }
  if (res.status !== 204) return res.json();
}

function showToast(message) {
  let el = document.getElementById("toastMsg");
  if (!el) {
    el = document.createElement("div");
    el.id = "toastMsg";
    el.className = "toastMsg";
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.classList.add("show");
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.remove("show"), 2500);
}

function applyPageBackground(fileName) {
  if (!fileName) return;
  document.body.classList.add("hasBgImage");
  document.body.style.backgroundImage = `url('${imgPath(fileName)}')`;
}

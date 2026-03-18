function getCookie(name) {
  const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return m ? m[2] : null;
}

async function ensureCsrf() {
  if (!getCookie("csrftoken"))
    await fetch("/api/auth/csrf/", { credentials: "include" });
}

async function req(method, path, body, isForm = false) {
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) await ensureCsrf();
  const headers = {};
  const tok = getCookie("csrftoken");
  if (tok) headers["X-CSRFToken"] = tok;
  if (!isForm && body) headers["Content-Type"] = "application/json";
  const res = await fetch("/api" + path, {
    method,
    headers,
    credentials: "include",
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error();
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

const api = {
  // Auth
  me: () => req("GET", "/auth/me/"),
  login: (u, p) => req("POST", "/auth/login/", { username: u, password: p }),
  logout: () => req("POST", "/auth/logout/"),
  register: (d) => req("POST", "/auth/register/", d),
  updateMe: (fd) => req("PATCH", "/auth/me/", fd, true),
  deleteMe: () => req("DELETE", "/auth/me/"),

  // User batches
  getBatches: (s) => req("GET", `/batches/${s ? "?status=" + s : ""}`),
  uploadBatch: (fd) => req("POST", "/batches/", fd, true),
  viewDoc: (id) => `/api/documents/${id}/view/`,

  // Admin
  adminBatches: (s, u) => {
    const p = new URLSearchParams();
    if (s) p.set("status", s);
    if (u) p.set("user", u);
    return req("GET", `/admin/batches/?${p}`);
  },
  approve: (id) => req("POST", `/admin/batches/${id}/approve/`),
  reject: (id, r) => req("POST", `/admin/batches/${id}/reject/`, { reason: r }),
  adminUpload: (fd) => req("POST", "/admin/batches/", fd, true),
  getUsers: (q) => req("GET", `/admin/users/${q ? "?q=" + q : ""}`),
  changeRole: (id, r) => req("PATCH", `/admin/users/${id}/`, { role: r }),
  // OCR
  ocr: (file) => {
    const fd = new FormData();
    fd.append("file", file);
    return req("POST", "/documents/ocr/", fd, true);
  },
};

export default api;

// app.js - logic phía trình duyệt cho dashboard Đề tài 42

function toast(msg, isErr = false) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = "show" + (isErr ? " err" : "");
  setTimeout(() => (t.className = ""), 3500);
}

// ---- Trạng thái module ----
async function refreshStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    document.querySelectorAll("#modules tr[data-name]").forEach((tr) => {
      const loaded = data[tr.dataset.name];
      const b = tr.querySelector(".badge");
      b.textContent = loaded ? "Loaded" : "Unloaded";
      b.className = "badge " + (loaded ? "loaded" : "unloaded");
    });
  } catch (e) {
    /* backend chưa sẵn sàng */
  }
}

async function mod(action, name) {
  const res = await fetch(`/api/module/${action}/${name}`, { method: "POST" });
  const data = await res.json();
  toast(`${name} ${action}: ${data.output}`, !data.ok);
  refreshStatus();
}

// ---- Bài 2: lọc IP ----
async function setFilter() {
  const ip = document.getElementById("ip").value.trim();
  if (!ip) return toast("Nhập IP cần chặn", true);
  const res = await fetch("/api/filter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "set", ip }),
  });
  const data = await res.json();
  toast(data.output, !data.ok);
}

async function clearFilter() {
  const res = await fetch("/api/filter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "clear" }),
  });
  const data = await res.json();
  toast(data.output, !data.ok);
}

// ---- Log dmesg realtime (SSE) ----
const MOD_NAMES = ["net_monitor", "net_filter", "ksock_tcp", "ksock_udp"];
const logEl = document.getElementById("log");

function appendLog(line) {
  const onlyMod = document.getElementById("onlyMod").checked;
  if (onlyMod && !MOD_NAMES.some((m) => line.includes(m))) return;
  logEl.textContent += line + "\n";
  logEl.scrollTop = logEl.scrollHeight;
}

function clearLog() {
  logEl.textContent = "";
}

function startLogStream() {
  const src = new EventSource("/api/dmesg/stream");
  src.onmessage = (e) => appendLog(e.data);
  src.onerror = () => {
    appendLog("[mất kết nối log — thử tải lại trang]");
    src.close();
  };
}

// ---- Khởi động ----
refreshStatus();
setInterval(refreshStatus, 3000);
startLogStream();

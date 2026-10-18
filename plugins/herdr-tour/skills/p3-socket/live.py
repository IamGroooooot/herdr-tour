#!/usr/bin/env python3
"""herdr live: socket 연결 하나를 열어 둔 채 pane 상태를 브라우저에 실시간으로 그리고, 브라우저에서 입력을 보낸다.

  session.snapshot   처음 상태 (요청 하나, 응답 하나)
  events.subscribe   상태 변화 (연결을 열어 둔 채 NDJSON이 계속 온다)
  agent.prompt       agent pane에 프롬프트
  pane.send_text     shell pane에 글자 + Enter

실행: herdr pane 안에서 python3 live.py, 브라우저로 http://127.0.0.1:8765
"""
import json, os, socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SOCKET = os.environ["HERDR_SOCKET_PATH"]
PORT = int(os.environ.get("PORT", "8765"))
RESYNC = {"pane_created", "pane_closed"}


def open_request(method, params):
    conn = socket.socket(socket.AF_UNIX)
    conn.connect(SOCKET)
    conn.sendall((json.dumps({"id": method, "method": method, "params": params}) + "\n").encode())
    return conn, conn.makefile(encoding="utf-8")


def call(method, params=None):
    conn, lines = open_request(method, params or {})
    with conn:
        return json.loads(lines.readline())


def subscribe(pane_ids):
    subs = [{"type": "pane.created"}, {"type": "pane.closed"}]
    subs += [{"type": "pane.agent_status_changed", "pane_id": p} for p in pane_ids]
    return open_request("events.subscribe", {"subscriptions": subs})


def send(pane, text):
    if pane.get("agent"):
        return call("agent.prompt", {"target": pane["pane_id"], "text": text})
    return call("pane.send_text", {"pane_id": pane["pane_id"], "text": text + "\r"})


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/events":
            return self.stream()
        self.reply(200, "text/html; charset=utf-8", PAGE.encode())

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.reply(200, "application/json", json.dumps(send(body["pane"], body["text"])).encode())

    def stream(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            while True:  # pane이 생기거나 닫히면 snapshot부터 다시
                snapshot = call("session.snapshot")["result"]["snapshot"]
                self.push("snapshot", snapshot)
                conn, lines = subscribe([p["pane_id"] for p in snapshot["panes"]])
                with conn:
                    for line in lines:
                        message = json.loads(line)
                        self.push("event", message)
                        if message.get("event") in RESYNC:
                            break
        except (BrokenPipeError, ConnectionResetError):
            pass

    def push(self, kind, data):
        self.wfile.write(f"event: {kind}\ndata: {json.dumps(data)}\n\n".encode())
        self.wfile.flush()

    def reply(self, code, kind, body):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


PAGE = """<!doctype html><meta charset="utf-8"><title>herdr live</title>
<style>
:root{--ink:#1d1d1f;--mute:#8a8a8e;--rule:#e4e4e7;--bg:#fff;--accent:#c2410c}
@media (prefers-color-scheme:dark){:root{--ink:#ececee;--mute:#8e8e93;--rule:#2c2c2e;--bg:#141416;--accent:#fb923c}}
body{font:500 14px/1.5 system-ui,sans-serif;color:var(--ink);background:var(--bg);max-width:760px;margin:32px auto;padding:0 16px}
h1{font-size:15px;margin:0}p{color:var(--mute);margin:2px 0 18px}
table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:5px 10px 5px 0;border-bottom:1px solid var(--rule)}
th{color:var(--mute);font-weight:500}tr{cursor:pointer}tr.on td{font-weight:700}tr.on td:first-child::before{content:"> "}
.blocked{color:var(--accent)}.unknown,.idle{color:var(--mute)}
form{display:flex;gap:8px;margin:18px 0 4px}input{flex:1;font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--rule);padding:6px}
button{font:inherit;color:var(--bg);background:var(--ink);border:0;padding:6px 14px;cursor:pointer}
pre{font:500 12px/1.45 ui-monospace,monospace;color:var(--mute);white-space:pre-wrap;word-break:break-all;margin-top:18px}
</style>
<h1>herdr live</h1><p>session.snapshot 한 번, 그다음은 events.subscribe가 계속 밀어 준다.</p>
<table><thead><tr><th>상태</th><th>이름</th><th>pane</th><th>바뀐 시각</th></tr></thead><tbody id=rows></tbody></table>
<form id=f><input id=t placeholder="행을 고르고 입력" autocomplete=off><button>보내기</button></form>
<p id=via></p><pre id=log></pre>
<script>
const ORDER = {blocked: 0, done: 1, working: 2, idle: 3, unknown: 4};
let panes = {}, picked = null;
const $ = id => document.getElementById(id);
const name = p => p.label || p.display_agent || p.agent || "shell";
function draw() {
  const list = Object.values(panes).sort((a, b) => ORDER[a.agent_status] - ORDER[b.agent_status] || a.pane_id.localeCompare(b.pane_id));
  $("rows").innerHTML = list.map(p => `<tr data-id="${p.pane_id}" class="${p.pane_id === picked ? "on" : ""}">
    <td class="${p.agent_status}">${p.agent_status}</td><td>${name(p)}</td><td>${p.pane_id}</td><td>${p.changed || ""}</td></tr>`).join("");
  const p = panes[picked];
  $("via").textContent = p ? `${p.agent ? "agent.prompt" : "pane.send_text"} -> ${name(p)} (${p.pane_id})` : "";
}
function log(line) { $("log").textContent = (line + "\\n" + $("log").textContent).split("\\n").slice(0, 12).join("\\n"); }
const es = new EventSource("/events");
es.addEventListener("snapshot", e => {
  const s = JSON.parse(e.data); panes = {};
  for (const p of s.panes) panes[p.pane_id] = Object.assign(p, {changed: (panes[p.pane_id] || {}).changed});
  log("session.snapshot: pane " + s.panes.length + "개"); draw();
});
es.addEventListener("event", e => {
  log(e.data); const m = JSON.parse(e.data), d = m.data || {}, p = panes[d.pane_id];
  if (m.event === "pane.agent_status_changed" && p) {
    Object.assign(p, {agent_status: d.agent_status, agent: d.agent || p.agent, changed: new Date().toTimeString().slice(0, 8)}); draw();
  }
});
$("rows").onclick = e => { const tr = e.target.closest("tr"); if (tr) { picked = tr.dataset.id; draw(); $("t").focus(); } };
$("f").onsubmit = async e => {
  e.preventDefault(); const p = panes[picked], text = $("t").value; if (!p || !text) return;
  const r = await (await fetch("/send", {method: "POST", body: JSON.stringify({pane: p, text})})).json();
  log(`${r.id}: ${r.error ? r.error.code : r.result.type}`); $("t").value = "";
};
</script>"""

if __name__ == "__main__":
    print(f"herdr live: http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

#!/usr/bin/env python3
"""
app.py - Dashboard demo cho Đề tài 42 (Networking).

Backend Flask chạy TRÊN chính máy Ubuntu, làm cầu nối giữa trình duyệt và
hệ thống: load/unload kernel module, stream log dmesg realtime, cấu hình
lọc IP (gọi filter_ctl), xem trạng thái module.

Chạy:   cd part4-web && python3 app.py
Mở:     http://127.0.0.1:5000

Yêu cầu: Flask  ->  pip3 install flask
         Một số lệnh cần sudo không mật khẩu (xem README.md, mục sudoers).
"""
import ipaddress
import os
import shlex
import subprocess
from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)

# Thư mục chứa các .ko và filter_ctl (mặc định: ../part3-kernel-module)
MODULE_DIR = os.path.abspath(
    os.environ.get("MODULE_DIR",
                   os.path.join(os.path.dirname(__file__), "..", "part3-kernel-module"))
)

# Whitelist module hợp lệ -> ngăn truyền tên tùy ý vào insmod/rmmod
MODULES = {
    "net_monitor": "Bài 1 - giám sát packet",
    "net_filter":  "Bài 2 - lọc theo IP đích",
    "ksock_tcp":   "Bài 3+4 - TCP trong kernel",
    "ksock_udp":   "Bài 5 - gửi UDP từ kernel",
}


def run(cmd):
    """Chạy lệnh, trả (ok, output)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        out = (r.stdout + r.stderr).strip()
        return r.returncode == 0, out
    except Exception as e:  # noqa: BLE001
        return False, str(e)


@app.route("/")
def index():
    return render_template("index.html", modules=MODULES)


@app.route("/api/status")
def status():
    """Trạng thái nạp của từng module (dựa vào lsmod)."""
    ok, out = run(["lsmod"])
    loaded = {name.split()[0] for name in out.splitlines()} if ok else set()
    return jsonify({name: (name in loaded) for name in MODULES})


@app.route("/api/module/<action>/<name>", methods=["POST"])
def module(action, name):
    if name not in MODULES:
        return jsonify(ok=False, output="Module không hợp lệ"), 400

    if action == "load":
        ko = os.path.join(MODULE_DIR, f"{name}.ko")
        if not os.path.exists(ko):
            return jsonify(ok=False, output=f"Chưa build: {ko} (chạy make)"), 400
        ok, out = run(["sudo", "insmod", ko])
    elif action == "unload":
        ok, out = run(["sudo", "rmmod", name])
    else:
        return jsonify(ok=False, output="Action không hợp lệ"), 400

    return jsonify(ok=ok, output=out or "(thành công)")


@app.route("/api/filter", methods=["POST"])
def filter_ip():
    """Gọi công cụ filter_ctl của Bài 2."""
    data = request.get_json(force=True)
    action = data.get("action")
    ctl = os.path.join(MODULE_DIR, "filter_ctl")

    if action == "set":
        ip = data.get("ip", "")
        try:
            ipaddress.IPv4Address(ip)
        except ValueError:
            return jsonify(ok=False, output="Địa chỉ IPv4 không hợp lệ"), 400
        ok, out = run(["sudo", ctl, "set", ip])
    elif action == "clear":
        ok, out = run(["sudo", ctl, "clear"])
    else:
        return jsonify(ok=False, output="Action không hợp lệ"), 400

    return jsonify(ok=ok, output=out)


@app.route("/api/dmesg/stream")
def dmesg_stream():
    """Stream log kernel realtime tới trình duyệt qua Server-Sent Events."""
    def generate():
        proc = subprocess.Popen(
            ["sudo", "dmesg", "--follow"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        try:
            for line in iter(proc.stdout.readline, ""):
                yield f"data: {line.rstrip()}\n\n"
        finally:
            proc.terminate()

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/processes")
def processes():
    """Top 20 tiến trình theo CPU (minh họa phần quản lý tiến trình)."""
    ok, out = run(["ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"])
    lines = out.splitlines()[:21] if ok else []
    return jsonify(lines=lines)


if __name__ == "__main__":
    # host 0.0.0.0 để mở được từ máy host khi chạy trong VM (nếu cần)
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)

# -*- coding: utf-8 -*-
"""
Item.json 管理器 - 本地服务 (双击 打开管理器.bat 自动启动, 无窗口)
- GET  /           返回 ItemManager.html
- GET  /api/items  读取 Item.json
- POST /api/items  保存 Item.json (自动备份 Item.json.bak, 原子写入, 按键数字排序)
- GET  /api/ping   页面保活心跳 (页面开着时服务不退出)
端口 8787; 若已被占用说明实例已在运行, 直接打开浏览器退出。
空闲自动退出: 超过 IDLE_SECONDS 秒无任何请求(含心跳)即自动关闭, 不留后台进程。
"""
import json
import os
import shutil
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ITEM_FILE = os.path.join(BASE_DIR, "Item.json")
BAK_FILE = ITEM_FILE + ".bak"
HTML_FILE = os.path.join(BASE_DIR, "ItemManager.html")
PORT = 8787
IDLE_SECONDS = int(os.environ.get("ITEM_MGR_IDLE_SECONDS", "300"))

last_active = time.time()


def load_items():
    with open(ITEM_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Item.json 根节点不是 JSON 对象")
    return data


def save_items(items):
    def key_sort(k):
        return (0, int(k)) if k.isdigit() else (1, k)

    ordered = {k: items[k] for k in sorted(items.keys(), key=key_sort)}
    text = json.dumps(ordered, ensure_ascii=False, indent=4) + "\n"
    if os.path.exists(ITEM_FILE):
        shutil.copy2(ITEM_FILE, BAK_FILE)
    tmp = ITEM_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, ITEM_FILE)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _touch(self):
        global last_active
        last_active = time.time()

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._touch()
        path = self.path.split("?")[0]
        if path == "/":
            if os.path.exists(HTML_FILE):
                with open(HTML_FILE, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            else:
                self._send(404, "ItemManager.html not found", "text/plain; charset=utf-8")
        elif path == "/api/items":
            try:
                self._send(200, json.dumps(load_items(), ensure_ascii=False))
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}))
        elif path == "/api/ping":
            self._send(200, json.dumps({"ok": True}))
        else:
            self._send(404, "not found", "text/plain; charset=utf-8")

    def do_POST(self):
        self._touch()
        if self.path.split("?")[0] != "/api/items":
            self._send(404, "not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            new_items = json.loads(raw)
            if not isinstance(new_items, dict):
                raise ValueError("数据不是 JSON 对象")
            for k, v in new_items.items():
                if not isinstance(k, str) or not k.strip():
                    raise ValueError("存在空 ID")
                if not isinstance(v, str):
                    raise ValueError(f"ID {k} 的名称不是字符串")
            save_items(new_items)
            self._send(200, json.dumps({"ok": True, "count": len(new_items)}))
        except Exception as e:
            self._send(400, json.dumps({"error": str(e)}))


def main():
    if not os.path.exists(ITEM_FILE):
        print(f"[error] Item.json not found: {ITEM_FILE}")
        sys.exit(1)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        # 端口被占用 = 已有实例在运行, 只需打开浏览器
        webbrowser.open(f"http://127.0.0.1:{PORT}/")
        sys.exit(0)
    url = f"http://127.0.0.1:{PORT}/"
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    # 空闲自动退出: 页面关闭后无心跳, 超时即自行关闭
    def idle_watchdog():
        global last_active
        while True:
            time.sleep(10)
            if time.time() - last_active > IDLE_SECONDS:
                try:
                    server.shutdown()
                except Exception:
                    pass
                return

    threading.Thread(target=idle_watchdog, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

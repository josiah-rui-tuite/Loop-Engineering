# 配置先: (生成物の例。skill で自分の環境向けに作り直す)
# 配布元: loop_engineering/tools/examples/gates/fault_mock.py
"""外部 API を模したフォールト注入モック。標準ライブラリのみ。

実 HTTP サーバを選んだ理由: 呼び出し側の timeout / Retry-After /
再試行をそのまま検査でき、HTTP 層を抽象化していない実装にも
base_url の差し替えだけで差し込めるため。
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODES = ("normal", "slow", "error", "ratelimit", "flaky")


class FaultConfig:
    """モードと seed から「決定論的な結果列」を先に作る。

    要点: 失敗の判定を時刻やスレッド順序でなく「何回目の要求か」に紐付ける。
    同じ seed なら毎回同じ失敗系列になる。
    """

    def __init__(self, mode="normal", seed=0, delay=2.0, retry_after=1,
                 flaky_rate=0.5, length=64):
        if mode not in MODES:
            raise ValueError(f"unknown mode: {mode}")
        self.mode, self.seed = mode, seed
        self.delay, self.retry_after = delay, retry_after
        rng = random.Random(seed)  # 無シードの random は使わない
        # outcomes[i] = i 回目の要求を失敗させるか
        self.outcomes = [rng.random() < flaky_rate for _ in range(length)]
        self._count = 0
        self._lock = threading.Lock()

    def next_result(self):
        """次の要求に返す (status, 遅延秒) を決める。"""
        with self._lock:
            i, self._count = self._count, self._count + 1
        if self.mode == "slow":
            return 200, self.delay
        if self.mode == "error":
            return 500, 0.0            # 常に 5xx。上限で諦めるかを見る
        if self.mode == "ratelimit":
            return (429, 0.0) if i == 0 else (200, 0.0)
        if self.mode == "flaky":
            return (503 if self.outcomes[i % len(self.outcomes)] else 200), 0.0
        return 200, 0.0


class _Handler(BaseHTTPRequestHandler):
    config: FaultConfig

    def _respond(self):
        status, delay = self.config.next_result()
        if delay:
            time.sleep(delay)
        body = json.dumps({"status": status, "path": self.path}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        if status == 429:
            self.send_header("Retry-After", str(self.config.retry_after))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = do_PUT = do_DELETE = _respond

    def log_message(self, *args):  # テスト出力を汚さない
        pass


class _Server(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # 呼び出し側が timeout で切った接続の traceback は出さない(正常な挙動)
        if not isinstance(sys.exc_info()[1], ConnectionError):
            super().handle_error(request, client_address)


def start_server(config, host="127.0.0.1", port=0):
    """モックを別スレッドで起動し (server, base_url) を返す。

    port=0 を渡すと空きポートを自動で選ぶ。
    """
    server = _Server((host, port), type("_H", (_Handler,), {"config": config}))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://{host}:{server.server_address[1]}"


def main():
    p = argparse.ArgumentParser(description="フォールト注入モック")
    p.add_argument("--mode", choices=MODES, default="normal")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--delay", type=float, default=2.0)
    a = p.parse_args()
    config = FaultConfig(a.mode, a.seed, a.delay)
    server, url = start_server(config, port=a.port)
    print(f"{url} mode={a.mode} seed={a.seed} (Ctrl-C で停止)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()

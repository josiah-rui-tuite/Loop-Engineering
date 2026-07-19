# 配置先: (生成物の例。skill で自分の環境向けに作り直す)
# 配布元: loop_engineering/tools/examples/gates/api_contract_test.py
"""境界の契約テスト。fault_mock の各モードで呼び出し側を検査する。

全通過で exit 0、違反で exit 1。--impl bad で「わざと壊した実装」を検査できる。
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request

from fault_mock import FaultConfig, start_server

IDEMPOTENT = {"GET", "HEAD", "PUT", "DELETE"}
RETRY_CAP = 5          # これを超えて叩き続けてはいけない
TIMEOUT_BUDGET = 1.5   # slow でこの秒数までに諦めること


def good_call(url, method="GET", timeout=0.5, max_retries=3):
    """契約を守る側。

    timeout / 上限付きリトライ / Retry-After 尊重 / 冪等のみ再試行。
    """
    attempts = 0
    for i in range(max_retries):
        attempts += 1
        req = urllib.request.Request(f"{url}/items", method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, attempts
        except urllib.error.HTTPError as e:
            if method not in IDEMPOTENT:
                return e.code, attempts               # 非冪等は再試行しない
            if e.code == 429:
                time.sleep(float(e.headers.get("Retry-After", 1)))
            elif 500 <= e.code < 600:
                time.sleep(0.05 * (i + 1))            # 少しずつ間隔を空ける
            else:
                return e.code, attempts
        except (TimeoutError, urllib.error.URLError):
            return 0, attempts                        # 待ち続けない
    return 0, attempts                                # 上限で諦める


def bad_call(url, method="GET", max_retries=10):
    """わざと壊した側。

    timeout 無し / Retry-After 無視 / 非冪等でも上限超過で再試行。
    """
    attempts = 0
    while attempts < max_retries:
        attempts += 1
        req = urllib.request.Request(f"{url}/items", method=method)
        try:
            with urllib.request.urlopen(req) as r:    # timeout を渡していない
                return r.status, attempts
        except urllib.error.HTTPError:
            continue
    return 0, attempts


def _run(mode, call, seed=0, **kw):
    """モックを立ててから1回呼び、(status, attempts, 経過秒) を返す。"""
    server, url = start_server(FaultConfig(mode=mode, seed=seed))
    try:
        t0 = time.monotonic()
        status, attempts = call(url, **kw)
        return status, attempts, time.monotonic() - t0
    finally:
        server.shutdown()


def sequence(seed, n=12):
    """flaky モードで観測される状態コード列(= 失敗系列)を返す。

    リトライ無しの素の観測。
    """
    def once(url):
        try:
            with urllib.request.urlopen(f"{url}/items", timeout=2) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code

    server, url = start_server(FaultConfig(mode="flaky", seed=seed))
    try:
        return [once(url) for _ in range(n)]
    finally:
        server.shutdown()


def checks(call):
    _, _, slow = _run("slow", call)
    _, err_n, _ = _run("error", call)
    rl_status, _, rl_wait = _run("ratelimit", call)
    _, post_n, _ = _run("error", call, method="POST")
    seq_a, seq_b = sequence(42), sequence(42)
    return [
        ("timeout を設定している", slow < TIMEOUT_BUDGET, f"{slow:.2f}s"),
        ("5xx でリトライし上限で諦める", 1 < err_n <= RETRY_CAP, f"{err_n} 回"),
        ("429 で Retry-After を尊重", rl_status == 200 and rl_wait >= 0.9,
         f"{rl_wait:.2f}s status={rl_status}"),
        ("非冪等(POST)を再試行しない", post_n == 1, f"{post_n} 回"),
        ("同じ seed で失敗系列が一致", seq_a == seq_b, str(seq_a)),
    ]


def main():
    p = argparse.ArgumentParser(description="API 境界の契約テスト")
    p.add_argument("--impl", choices=("good", "bad"), default="good")
    a = p.parse_args()
    results = checks(good_call if a.impl == "good" else bad_call)
    ng = 0
    for name, ok, detail in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} ({detail})")
        ng += not ok
    print(f"-- impl={a.impl}: {len(results) - ng} passed, {ng} failed")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())

# 配置先: (生成物の例。skill で自分の環境向けに作り直す)
# 配布元: loop_engineering/tools/examples/gates/mcp_gate.py
"""MCP サーバの契約テスト。

三観点 Checker(構造 / 利用 / エラー設計)を機械で回す。
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parent.parent / "minimal_server.py"
failures: list[str] = []


def check(label: str, ok: bool) -> None:
    """1件の判定を記録する。落ちても止めず、最後にまとめて報告する。"""
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        failures.append(label)


def ask(proc, method: str, params: dict | None = None,
        req_id: int = 1) -> dict:
    """リクエストを1行送って、応答を1行読む。"""
    request = {"jsonrpc": "2.0", "id": req_id,
               "method": method, "params": params or {}}
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def call(proc, name: str, arguments: dict, req_id: int) -> dict:
    return ask(proc, "tools/call",
               {"name": name, "arguments": arguments}, req_id)


def text_of(response: dict) -> str:
    return response["result"]["content"][0]["text"]


def main() -> int:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        text=True, encoding="utf-8", env=env,
    )
    try:
        init = ask(proc, "initialize", req_id=1)
        check("initialize が serverInfo を返す", "serverInfo" in init["result"])

        # (a) 構造: tools/list がスキーマ通りか
        tools = ask(proc, "tools/list", req_id=2)["result"]["tools"]
        check("tools/list が1個以上のツールを返す", len(tools) >= 1)
        for tool in tools:
            name = tool.get("name", "?")
            schema = tool.get("inputSchema", {})
            props = schema.get("properties")
            check(f"[{name}] name/description/inputSchema が揃う",
                  bool(tool.get("name"))
                  and bool(tool.get("description"))
                  and bool(schema))
            check(f"[{name}] inputSchema が object 型",
                  schema.get("type") == "object"
                  and isinstance(props, dict))
            check(f"[{name}] required が properties に実在する",
                  all(key in schema.get("properties", {})
                      for key in schema.get("required", [])))

        # (b) 利用: 正しい引数で通るか
        ok_sum = call(proc, "sum_range", {"start": 1, "end": 10}, 3)
        check("sum_range(1,10) が 55", text_of(ok_sum) == "55")
        check("成功時は isError=False", ok_sum["result"]["isError"] is False)
        ok_stats = call(proc, "text_stats", {"text": "a\nb"}, 4)
        check("text_stats が行数と文字数を返す",
              json.loads(text_of(ok_stats)) == {"lines": 2, "chars": 3})

        # (c) エラー設計: 失敗したとき「次の一手」まで返すか
        bad_cases = [
            ("型違い", call(proc, "sum_range", {"start": "1", "end": 10}, 5)),
            ("引数欠落", call(proc, "text_stats", {}, 6)),
            ("存在しないツール", call(proc, "no_such_tool", {}, 7)),
        ]
        for label, response in bad_cases:
            body = text_of(response)
            check(f"[{label}] isError=True で返る",
                  response["result"]["isError"] is True)
            check(f"[{label}] 次の一手を含む", "次の一手" in body)
            check(f"[{label}] 呼び直せる引数の実例を含む",
                  "{" in body and "}" in body)
    finally:
        if proc.stdin:  # 標準入力を閉じるとサーバのループが終わる
            proc.stdin.close()
        proc.wait(timeout=10)

    print(f"\n{'NG' if failures else 'OK'}: {len(failures)} 件の失敗")
    for label in failures:
        print(f"  - {label}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

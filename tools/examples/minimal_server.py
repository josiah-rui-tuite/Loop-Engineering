# 配置先: (生成物の例。skill で自分の環境向けに作り直す)
# 配布元: loop_engineering/tools/examples/minimal_server.py
"""最小の MCP サーバ。stdio + JSON-RPC 2.0、標準ライブラリのみ。"""

import json
import sys
from typing import TypeGuard

TOOLS = [
    {
        "name": "sum_range",
        "description": "start から end までの整数を合計する(両端を含む)。",
        "inputSchema": {
            "type": "object",
            "properties": {"start": {"type": "integer"},
                           "end": {"type": "integer"}},
            "required": ["start", "end"],
        },
    },
    {
        "name": "text_stats",
        "description": "テキストの行数と文字数を数える。",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]


def recovery(problem: str, example: str) -> str:
    """エラー文面。何が悪いかだけでなく「次の一手」を必ず添える。"""
    return (f"{problem}\n次の一手: 引数をこの形にして呼び直して"
            f"ください -> {example}")


def is_int(value: object) -> TypeGuard[int]:
    """整数かどうか。真偽値は整数として扱わない。"""
    return isinstance(value, int) and not isinstance(value, bool)


def call_tool(name: str, args: dict) -> str:
    if name == "sum_range":
        start, end = args.get("start"), args.get("end")
        if not is_int(start) or not is_int(end):
            raise ValueError(recovery(
                "sum_range の start と end は整数が必要です。",
                '{"start": 1, "end": 10}'))
        if end < start:
            raise ValueError(recovery(
                "sum_range は start <= end が前提です。",
                '{"start": 1, "end": 10}'))
        return str(sum(range(start, end + 1)))
    if name == "text_stats":
        text = args.get("text")
        if not isinstance(text, str):
            raise ValueError(recovery(
                "text_stats の text は文字列が必要です。",
                '{"text": "hello"}'))
        return json.dumps({"lines": len(text.splitlines()), "chars": len(text)})
    raise ValueError(recovery(
        f"{name!r} というツールはありません。",
        '{"name": "sum_range", "arguments": {"start": 1, "end": 10}}'))


def handle(request: dict) -> dict | None:
    method, params = request.get("method"), request.get("params") or {}
    if request.get("id") is None:  # 通知には応答しない
        return None
    result: dict
    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "minimal-server", "version": "1.0.0"},
        }
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        try:
            text = call_tool(params.get("name", ""),
                             params.get("arguments") or {})
        except ValueError as e:
            result = {"content": [{"type": "text", "text": str(e)}],
                      "isError": True}
        else:
            result = {"content": [{"type": "text", "text": text}],
                      "isError": False}
    else:
        return {"jsonrpc": "2.0", "id": request["id"],
                "error": {"code": -32601,
                          "message": f"未知のメソッド: {method}"}}
    return {"jsonrpc": "2.0", "id": request["id"], "result": result}


def main() -> None:
    """1行1メッセージで読み、応答を1行で返す。"""
    for line in sys.stdin:
        if not line.strip():
            continue
        response = handle(json.loads(line))
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

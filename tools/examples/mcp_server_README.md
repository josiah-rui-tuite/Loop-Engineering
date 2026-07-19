> 配置先: (生成物の例。skill で自分の環境向けに作り直す)
> 配布元: loop_engineering/tools/examples/mcp_server_README.md

# 第27章 付属ファイル: 最小の MCP サーバ

標準ライブラリだけで動く。`pip install` は不要。Python 3.12 と Windows / macOS / Linux で確認。

## ファイル

| ファイル | 配置先 |
| --- | --- |
| `minimal_server.py` | `loop_engineering/tools/examples/minimal_server.py` |
| `.mcp.json.example` | **`<リポジトリルート>/.mcp.json`** にリネームして置く |
| `../gates/mcp_gate.py` | `loop_engineering/tools/examples/gates/mcp_gate.py` |

`args` のパスはリポジトリルートからの相対。別の場所に置くなら絶対パスに書き換える。

## 動かす

```
cp ../templates/.mcp.json.example .mcp.json
```

置いたら Claude Code を再起動する。`/mcp` に `minimal` が出れば接続できている。

## 三観点 Checker を機械で回す

```
python gates/mcp_gate.py
```

サーバを subprocess で起動して、(a) 構造 (b) 利用 (c) エラー設計 の3観点を検査する。
全通過で exit 0、1つでも落ちれば exit 1。CI にそのまま置ける。

観点 (c) は「エラーが返ること」ではなく、**エラー文が次の一手を含むこと**を見る。
`次の一手:` と、コピーして呼び直せる引数の実例。これが章の主張であり、
落とすと「失敗したのは分かるが、どう直せばいいか分からない」応答が通ってしまう。

## 手で叩く

1行1 JSON で標準入力に流し込めば、依存なしで応答を確認できる。

```
echo {"jsonrpc":"2.0","id":1,"method":"tools/list"} | python minimal_server.py
```

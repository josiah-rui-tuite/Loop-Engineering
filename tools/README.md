# 付属ファイル ― 章 → ファイル → 置き場

『Loop Engineering』実践編（第22〜27章）の足場。

渡しているのは**手順**であって、完成したコードではない。
評価ゲートも契約テストも MCP サーバも、指標・言語・題材が読者ごとに違うので、
出来合いを配っても自分の題材には合わない。skill を入れて、自分の環境で書かせて回す。

## 置き場の見取り図

`.claude/skills/` に入る6つが本体。`templates/` は読者が埋める枠で、
プロジェクトのルートから見た普通の場所に置く。

```text
あなたのプロジェクト/
├── .mcp.json                        ← templates/.mcp.json.example
├── CLAUDE.md                        ← templates/CLAUDE.md.example
├── LOOP_CONTRACT.md                 ← templates/LOOP_CONTRACT.md
├── .claude/skills/
│   ├── loop-contract/SKILL.md       ← 22章 一周の回し方
│   ├── eval-gate-loop/SKILL.md      ← 23章 評価ゲートを書かせる
│   ├── two-stage-check/SKILL.md     ← 24章 機械と人間に仕分ける
│   ├── design-loop/SKILL.md         ← 25章 複数案を採点して決める
│   ├── contract-first-api/SKILL.md  ← 26章 境界の契約を先に凍結する
│   └── mcp-contract-loop/SKILL.md   ← 27章 ツール契約を公開する
├── contracts/
│   ├── serving.yaml                 ← templates/serving.yaml
│   ├── 〈API名〉.md                  ← templates/api_contract.md
│   └── tools.md                     ← templates/tool_contract.md
└── docs/
    ├── adr/NNNN-〈決定の要約〉.md    ← templates/ADR.md
    └── ui_human_gate.md             ← templates/ui_human_gate.md
```

SKILL.md の先頭は `---` で始まっている。ここを動かさないこと。
前に行を足すと frontmatter が読まれず、skill は一覧に出るのに発火しなくなる。
先頭の `> 配置先:` は frontmatter の後ろに置いてあるので、そのままコピーしてよい。

MCP の設定は **`.mcp.json`（リポジトリルート直下）** に置く。
`settings.json` の `mcpServers` に書いても黙って無視される。エラーが出ないので気づきにくい。
書き換えたら Claude Code の再起動が要る。

## 章ごとの対応

| 章 | 配布物 | 置き場 | 行数 |
| --- | --- | --- | --- |
| 22 タスクリスト | `templates/LOOP_CONTRACT.md` | `LOOP_CONTRACT.md` | 71 |
| | `claude/skills/loop-contract/SKILL.md` | `.claude/skills/loop-contract/SKILL.md` | 37 |
| | `templates/CLAUDE.md.example` | `CLAUDE.md` | 36 |
| 23 外観検査 | `claude/skills/eval-gate-loop/SKILL.md` | `.claude/skills/eval-gate-loop/SKILL.md` | 35 |
| 24 ダッシュボード | `claude/skills/two-stage-check/SKILL.md` | `.claude/skills/two-stage-check/SKILL.md` | 35 |
| | `templates/ui_human_gate.md` | `docs/ui_human_gate.md` | 32 |
| 25 データ基盤 | `claude/skills/design-loop/SKILL.md` | `.claude/skills/design-loop/SKILL.md` | 66 |
| | `templates/serving.yaml` | `contracts/serving.yaml` | 47 |
| | `templates/ADR.md` | `docs/adr/NNNN-〈要約〉.md` | 61 |
| 26 API 連携 | `claude/skills/contract-first-api/SKILL.md` | `.claude/skills/contract-first-api/SKILL.md` | 47 |
| | `templates/api_contract.md` | `contracts/〈API名〉.md` | 60 |
| 27 MCP サーバ | `claude/skills/mcp-contract-loop/SKILL.md` | `.claude/skills/mcp-contract-loop/SKILL.md` | 50 |
| | `templates/tool_contract.md` | `contracts/tools.md` | 60 |
| | `templates/.mcp.json.example` | `.mcp.json` | 8 |

## examples/ は答えではない

`examples/` には、上の skill を一度回して出てきた成果物を置いてある。
Python で書かれているが、それはこちらの手元がそうだっただけで、正解ではない。
自分の題材に合うものを skill で作らせてから、比べたいときに開くくらいでちょうどいい。
先に読むと、そこに書いてある指標や閾値をそのまま持ってきてしまう。

置いてあるもの。

- `examples/gates/` ― 評価ゲート・UIゲート・スキーマゲート・契約テスト・フォールト注入モック
- `examples/minimal_server.py` ― 最小の MCP サーバ
- `examples/gates/sample/`・`sample_ui/`・`examples/sample_contracts/` ― 上を動かすための入力

動かすなら、標準ライブラリだけで足りる。`pip install` は要らない。Python 3.12 で確認した。

```sh
cd examples/gates
python eval_gate.py sample/pass.csv --threshold 0.5 \
    --min-auroc 0.95 --max-miss 0.02 --max-fp 0.10   # 0
python eval_gate.py sample/fail.csv --threshold 0.5 \
    --min-auroc 0.95 --max-miss 0.02 --max-fp 0.10   # 1
python ui_gate.py sample_ui/pass.html                # 0
python ui_gate.py sample_ui/fail_contrast.html       # 1
python ui_gate.py sample_ui/fail_sum.html            # 1
python ui_gate.py sample_ui/fail_required.html       # 1
python mcp_gate.py                                   # 0
python api_contract_test.py --impl good              # 0
python api_contract_test.py --impl bad               # 1

cd ../sample_contracts
python ../gates/schema_gate.py serving_v1.yaml serving_v2_add.yaml   # 0
python ../gates/schema_gate.py serving_v1.yaml serving_v3_drop.yaml  # 1
python ../gates/schema_gate.py serving_v1.yaml serving_v4_type.yaml  # 1
```

失敗するはずのケースを必ず一緒に走らせてほしい。合格側だけ試して緑を確認するのは、
ゲートが本当に検知しているかを何も確かめていないのと同じになる。
skill 側でも、ゲートを作らせたら必ずわざと壊して落ちることを確かめさせている。

Windows でログをファイルに残すときは `PYTHONIOENCODING=utf-8` を指定する。
指定しないと日本語が cp932 で保存される。

## ゲートが見ていないもの

`examples/gates/ui_gate.py` は横スクロールの有無とスクリーンショット差分を判定しない。
静的な HTML を読むだけでは分からず、実ブラウザでの描画が要るからだ。
実行するとこの範囲外の項目を毎回表示する。合格したときにも表示する。
緑を見た人ほど「全部見てもらえた」と受け取るので、そこで黙らないようにしてある。

`examples/gates/fault_mock.py` の決定論チェックはモック側の性質を見るもので、
呼び出し側の契約ではない。壊れた呼び出し側でも、この項目だけは通る。

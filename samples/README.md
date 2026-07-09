# Loop Engineering 大全 ― 付属参考サンプル集

これは書籍「**Loop Engineering 大全**」(著: Josiah Rui Tuite, 2026)の付属参考サンプル集です。
本書に登場するスキル・テンプレート・設定ファイルを、GitHub 公開用の参考資料として実ファイルに起こしたものです。
各ファイル冒頭には、書籍付属の参考実装である旨を注記しています。

## 収録物

```
samples/
├── LICENSE                 MIT ライセンス本文
├── README.md               本ファイル
├── DISCLAIMER.md           免責事項・商標注記(単体で読める再掲)
├── .claude/
│   └── skills/
│       ├── loop-architect/SKILL.md    ループそのものを壁打ちで設計・運用・改善するメタSkill(第19章)
│       ├── commit-message/SKILL.md    Conventional Commits に沿うコミットメッセージ生成Skill(第2章)
│       ├── verify-gate/SKILL.md       lint→型→関連テストの3点ゲートSkill(第28章)
│       ├── parallel-loop/SKILL.md     WBS→worktree並列→順次マージの並列Skill(第28章)
│       └── loop-status/SKILL.md       現在のループ状態を要約するSkill(第28章)
├── templates/
│   ├── prompts/sparring-kickoff.md    人間と AI の「壁打ち」起動プロンプト(第19章)
│   ├── LOOP_CONTRACT.md               Loop Contract 雛形(Phase 0〜6 を1枚に、第20章)
│   ├── LOOPS.md                       ループ台帳の最小エントリと初回起動(第16・20章)
│   ├── AGENTS.md                      リポジトリ共通のAI作業規約テンプレ(第16章)
│   └── CLAUDE.md                      プロジェクト直下の常設規約テンプレ(第12章)
└── configs/
    ├── acceptance.yaml                入出力・受入基準を先に固定する契約(第5章)
    └── deny_commands.yaml             危険コマンドの拒否リスト=権限境界(第5・16章)
```

## 使い方の注意
- `.claude/skills/` 等はエージェント環境(Claude Code など)のプロジェクト配下に置いて使う想定です。
- `templates/` と `configs/` はプレースホルダ(`<...>` 等)を各自の値へ置き換えてから利用してください。
- 本書に完全なコードが無いもの(一部の config / skill)は、本書の説明文に忠実な**最小サンプル**として作成しています。過剰に発明していません。

## 免責事項
本サンプルは情報提供・学習を目的とした参考実装であり、現状有姿(AS IS)で提供されます。
正確性・完全性・特定目的適合性を保証しません。利用によって生じたいかなる損害についても
著者は責任を負いません。実運用の前に、各自の責任で検証してください。

## ライセンス
本リポジトリのコード/設定/テンプレートは **MIT License**(`LICENSE` 参照)で提供されます。
自由に利用・改変・再配布できます。

## 商標注記
Claude, Anthropic, Model Context Protocol(MCP)などは各社の商標です。
本サンプルは各権利者と提携・後援関係にありません。

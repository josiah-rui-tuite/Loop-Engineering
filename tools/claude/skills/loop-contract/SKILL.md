---
name: loop-contract
description: ループの一周を Loop Contract に従って回す。実装・修正・検証の前に毎回 LOOP_CONTRACT.md を読み戻し、許可パス・完了条件・予算・人間ゲートを確認する。完了を宣言する前にも使う。
---

> 配置先: .claude/skills/loop-contract/SKILL.md
> 配布元: loop_engineering/tools/claude/skills/loop-contract/SKILL.md

# Loop Contract に従って一周する

契約の中身はこの skill が持たない。単一の真実は常にプロジェクトルートの `LOOP_CONTRACT.md`。
記憶や要約で代用せず、毎周ファイルを読み直す。
**この skill が土台**で、周回・予算・人間ゲート・許可パスはここに一本化する。
題材別の skill(API 連携、MCP、評価、設計、画面受入など)は、この土台の上に手順を上乗せするものとして併せて使う。

## 手順

1. `LOOP_CONTRACT.md` を読む。`state.md` があれば併せて読み、前周までの現状を把握する。契約がまだ無いなら実装を始めず、人間に初版の作成を求める(Maker は契約を起こさない)。雛形は、配布物の `templates/LOOP_CONTRACT.md` を `LOOP_CONTRACT.md` に写して使う。
2. 今回の一手が `guardrails.paths_allowed` の中に収まるか確認する。収まらないなら**実装せず**、必要なパスを人間に申告する。`guardrails.paths_forbidden` は読むだけで書き換えない。
3. 実装する。`done_when` に無いものを足さない。
4. `verify.command` を実行し、終了コードを `expect_exit` と比べる。動いた気がする、では判定しない。ゲートが何件走ったかを `min_checks` と比べ、0件の緑を合格にしない。
5. 判定する。
   - 期待どおり: `done_when` を一つずつ照合する。全て緑でも `goal` に照らして未達なら完了にしない。
   - 不一致: 失敗の要点だけを `state.md` に書き、手順1へ戻る。
6. `budget`(周回・トークン・時間)の残りを確認する。尽きていたら完了を宣言せず人間に返す。
7. `human_gate` に該当したら、そこで止めて人間の承認を待つ。承認を代行しない。

## やってはいけない

- Contract を読まずに周を始めること。
- ゲートを実行せずに完了を宣言すること。ゲートが空振り(0件)のまま緑を根拠にすること。
- 未達を「概ね達成」と書き換えること。落ちたなら落ちたと報告する。
- Contract 自体を Maker が書き換えること(改訂は人間の権限)。

## 報告様式

done / 変更したパス / `verify` の終了コード / 未達の `done_when` / 残りの予算。

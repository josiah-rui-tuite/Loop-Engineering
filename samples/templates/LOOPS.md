<!-- 本サンプルは書籍「Loop Engineering 大全」付属の参考実装です(AS IS)。第20章 雛形② と 第16章の成果物一覧を統合。 -->
# LOOPS.md ― ループ一覧/目的/起動/停止条件の台帳
# どんなループが存在し、それぞれの目的・起動条件・停止条件は何かを一覧化する。
# これが無いと「野良ループ」が増え、コスト爆発と Drift の温床になる。

# ===== 最小エントリ =====
## <loop-name> (L1)
contract: LOOP_CONTRACT.md
trigger:  <手動 / 〜の変化 / cron>
gates:    <Phase 1 のコマンド>
report:   reports/<loop-name>_{date}.md

# ===== 初回起動(まず L1=提案のみ) =====
# 対話で:
#   /loop LOOP_CONTRACT.md に従って1周。変更は適用せず、提案とレポートだけ出して
# 条件達成まで(検証が緑になるまで):
#   /goal LOOP_CONTRACT.md の gates が全て緑になるまで小さな一歩を繰り返す(各歩で証拠を提示)

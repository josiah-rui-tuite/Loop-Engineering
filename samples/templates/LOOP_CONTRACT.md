<!-- 本サンプルは書籍「Loop Engineering 大全」付属の参考実装です(AS IS)。第20章 雛形①より。<loop-name> 等の <...> は各自の値に置き換える。 -->
# Loop Contract: <loop-name>
目的/完了の定義: <1文。「Xが緑になったら完了」の形で>        # Phase 0
gates:                                                      # Phase 1(機械判定)
  - <合否を返すコマンド1>
  - <合否を返すコマンド2>
allowed-paths:   [<触ってよい場所>]                          # Phase 2
read-only-paths: [<読むだけ>]
approval:        [<本番/削除/送信/課金など人間承認が要る操作>]
budget: { attempts_max: 6, minutes_max: 30, tokens_max: 500000 }   # Phase 3
stop:   [連続失敗2回, 予算超過, 範囲外への書込み試行]
state:  { dir: state/, log: state/decision_log.md, rollback: "git worktree/ブランチを破棄" }  # Phase 4
maker_checker: "Maker=実装 / Checker=別指示でgatesとリーク検査のみ採点(自己採点しない)"  # Phase 5
autonomy: L1   # Phase 6: まずL1。安定後にL2→低リスクのみL3

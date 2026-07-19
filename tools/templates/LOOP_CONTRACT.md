> 配置先: LOOP_CONTRACT.md  (プロジェクトルート直下)
> 配布元: loop_engineering/tools/templates/LOOP_CONTRACT.md

# Loop Contract

一周の約束を書き下した一枚。毎周これを読み戻す。書き換えるのは人間、参照するのは Maker と Checker。
各欄の `#` 行は書き方の例なので、埋めたら消してよい。

```yaml
goal: # 一文。何が動けば勝ちか。やらないことも一言添えて範囲を閉じる
  # 悪い: タスクリストをいい感じに作る
  # 良い: 追加/完了/削除ができ、再読み込み後も残る単一HTMLのToDo(検索と期限は作らない)

done_when: # 機械が真偽で返せる形で書く(曖昧な欄は自己採点の余地)。判定する文字列まで決める
  # 悪い: 品質が十分になったら
  # 良い: npm run check が exit 0(lint 0件・テスト全通過)
  - 
  - 

guardrails: # 触ってよい場所と触ってはいけない場所を、二つの欄に分けて名指しする
  paths_allowed: # ここに挙げた場所だけ書き換えてよい。verify が使うテストも忘れず入れる
    # 悪い: プロジェクト全体
    # 良い: todo.html / todo.test.js
    - 
  paths_forbidden: # 触られたら事故になる場所を名指しする
    # 悪い: 危ないところは避ける
    # 良い: package.json / .github/ / .env / todos.json(実データ。テストは一時ファイルへ)
    - 

data: # データの所在と分割。ホールドアウトは実装する側に見せない(人間が隔離し、最終確認の一度だけ使う)
  # 悪い: 手元の画像を使って精度を測る
  # 良い: source: data/images/(良品/不良品でフォルダ分け) / split: 学習70 ・判定しきい値の調整15 ・ホールドアウト15(%)
  source: # 場所とラベルの付き方(フォルダ分けか注釈ファイルか)まで書く
  split: # 割合と、ホールドアウトの隔離先パス(そのパスは paths_forbidden にも入れる)
  manifest: # どの事例がどの分割かを書き出した一覧ファイルの所在
  frozen: # 一覧ファイルと評価ゲートの内容ハッシュ。控えたら以後変更しない

artifacts: # 成果物と履歴の置き場。実行場所が変わっても散らばらないよう、ルート基点の固定パスで書く
  # 悪い: 結果は実行ごとの日時フォルダへ保存する(周回間で比較できなくなる)
  # 良い: history: artifacts/scores.csv(1周1行で追記)と artifacts/triage.md(仕分け表) / outputs: artifacts/model/
  history: # スコア履歴と仕分け表の固定パス
  outputs: # 生成物(モデル・推論結果・誤りの一覧)の置き場。paths_allowed にも入れる

verify: # 合否が終了コードで返るものを据える。空振りの緑に注意
  # 悪い: テストして動作を確認する(テスト0件でも exit 0 になり、未検証が緑で通る)
  # 良い: command: npm run check / expect_exit: 0(非0なら未達。直して次の周へ)
  command: 
  expect_exit: 0
  min_checks: # 最低これだけ検証が走っていること(例: テスト3件)。0件の緑を弾く

budget: # 尽きたら勝手に続けず人間へ戻す上限。いずれか一つでも尽きたら止める
  # 悪い: 無理のない範囲で
  # 良い: loops: 5 / tokens: 1周あたり入力2万 / time: 合計30分
  loops: 
  tokens: 
  time: 

human_gate: # 機械が判断してはいけない一点。ここで必ず止まる
  # 悪い: 最後に人間が確認する
  # 良い: done_when が全て緑になった後、画面の見た目とマージ可否を人間が承認
  - 
```

## 回し方

1. この一枚が無ければ実装を始めない。初版を書くのは人間で、Maker は起こさない。
2. Maker は `guardrails.paths_allowed` の中だけを直す。
3. `verify.command` を実行し、終了コードで合否を判定する(自己申告しない)。
4. `done_when` が全て緑でも、`goal` に照らして未達なら完了にしない。
5. 未達なら現状を `state.md` に書き、次の周はこの Contract と `state.md` だけを読み戻す。
6. `budget` を超えた、または `human_gate` に達したら、完了を宣言せず人間に判断を返す。

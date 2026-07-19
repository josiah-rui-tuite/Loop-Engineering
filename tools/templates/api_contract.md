> 配置先: contracts/〈API名〉.md
> 配布元: loop_engineering/tools/templates/api_contract.md

# 外部API連携の境界契約: 〈API名〉

外側の世界と自分のコードの境目に置く一枚。ここが空欄のまま実装を始めると、落ち方の設計が実装者の気分で決まる。各欄の `#` 行は書き方の例なので、埋めたら消してよい。

```yaml
provider: # 相手。名前と版に加え、仕様を読んだ日付まで書く(仕様は黙って変わる)
  # 悪い: 配送業者のAPI
  # 良い: name_version: Acme配送 追跡API v2 / spec_checked_on: 2026-07-19
  name_version: 
  spec_url: 
  spec_checked_on: 
operations: # 呼ぶ操作だけを列挙する。入出力はこちらの語彙に直して書く
  # 悪い: 追跡情報を取得する
  # 良い: get_tracking / in: 追跡番号(文字列) / out: 状態(enum)・最終更新時刻・履歴の配列
  - name: 
    in_out: 
timeout: # 接続と読み取りを分けて、1試行あたりの秒で書く。「適当に待つ」は無限待ちと同じ
  # 悪い: 十分な時間を待つ
  # 良い: connect: 3s / read: 10s(1試行ごとに適用。再試行を含む総時間は retry.policy で抑える)
  connect: 
  read: 
retry: # 再試行してよい条件と上限。条件を書かないと 4xx を叩き続ける
  # 悪い: 失敗したら再試行する
  # 良い: retry_on: タイムアウトと 5xx のみ / policy: 最大3回、間隔 1s,2s,4s に乱数を足す
  retry_on: 
  policy: 
idempotency: # どの操作なら再試行して安全か。安全でないものは名指しで禁じる(該当が無ければ「なし」。空欄にしない)
  # 悪い: だいたい安全
  # 良い: safe: get_tracking(読み取りのみ) / unsafe: create_shipment(冪等キー未対応。再試行は二重発送)
  safe_to_retry: 
  unsafe: 
rate_limit: # 429 は retry の対象に入れず、この欄だけで扱う(再試行回数を二箇所に書かない)。Retry-After を無視しない
  # 悪い: レート制限に気をつける
  # 良い: quota: 60req/分 / on_429: Retry-After 秒だけ待って1回だけ再試行し、以降は失敗にする
  quota: 
  on_429: 
on_failure: # 再試行を尽くしたときの既定動作。何を返し、何を残すか
  # 悪い: エラーにする
  # 良い: returns: 保存済みの直近状態と「更新できず」 / logs: 追跡番号・応答コード・所要時間
  returns: 
  logs: 
adapter: # 外部呼び出しを閉じ込める場所。契約テストはここに差す
  # 悪い: 必要な場所から直接呼ぶ
  # 良い: boundary: TrackingClient(この外へ HTTP を出さない) / contract_test: 記録済み応答で境界だけを検証する
  boundary: 
  contract_test: 
secrets: # 置き場だけを書く。値は書かない・コミットしない
  # 悪い: ACME_API_KEY=ak_live_9f3c... をこの欄に貼る
  # 良い: location: 環境変数 ACME_API_KEY(.env は .gitignore 済み) / rotation: 90日
  location: 
  rotation: 
```

## 使い方
1. 実装を始める前に人間がこの一枚を埋める。埋まっていない API は呼ばない。
2. 実装側はこの契約だけを見て `adapter.boundary` を書く。境界の外へ HTTP を漏らさない。
3. 仕様が変わったら `spec_checked_on` を更新し、契約テストを回してから実装を直す。落ち方(timeout / retry / on_failure)を緩めてよいのは人間だけ。

> 配置先: contracts/tools.md
> 配布元: loop_engineering/tools/templates/tool_contract.md

# MCP ツール契約: 〈サーバ名〉

モデルに渡す道具の仕様書。説明文と引数スキーマがモデルの選択根拠そのものなので、ここが曖昧だとモデルは違う道具を選ぶ。1ツール1ブロックで、公開する分だけ複製する。各欄の `#` 行は書き方の例なので、埋めたら消してよい。

```yaml
- name: # ツール名。動詞と目的語で、名前だけで何をするか分かるようにする
  # 悪い: query / do_it
  # 良い: search_inventory_items
  description: # モデルが選ぶ根拠。いつ使うか・いつ使わないかを書く
    # 悪い: 在庫を検索します
    # 良い: 商品名や型番から在庫の候補を探す。1件の詳細が要るときは get_inventory_item を使う
  input_schema: # 引数を「名前: 型 必須/任意(既定値・許される値)」の一行書式で並べる。曖昧な引数は誤用される
    # 悪い: query (文字列)
    # 良い: keyword: string 必須 / warehouse: string 任意(既定=省略時は全倉庫。有効値は list_warehouses が返す)
  returns: # 戻り値の形。件数と、次の一手に必要な識別子を必ず含める
    # 悪い: 在庫の情報
    # 良い: items[]: {item_id, name, qty} / total_matched: integer(打ち切り前の総数)
  on_error: # 失敗時の応答。原因と「次に何をすればよいか」を文章で返す
    # 悪い: Error: 500
    # 良い: 「倉庫コード 'XX' は存在しない。list_warehouses で有効なコードを確認せよ」
  max_items: # 件数の上限はここだけで決める(引数にも件数を持たせて二箇所に数字を書かない)。上限の無い一覧は文脈を焼き切る
    # 悪い: 全件返す
    # 良い: 20件で打ち切り、total_matched と絞り込みの指示を添える(1件取得のツールは「該当なし(常に1件)」)
  mutability: # read_only か destructive のどちらかを必ず書く。曖昧な third option を作らない
    # 悪い: たぶん安全
    # 良い: read_only(在庫ビューを参照するだけで書き込まない)
  approval: # destructive のときだけ承認の挟み方を書く。read_only なら「不要(read_only)」
    # 悪い: 慎重に実行する
    # 良い: 実行前に対象件数と差分の要約を提示し、人間が承認するまで書き込まない
```

## 二段に分ける(候補一覧と一件取得は別のツールにする)
一覧が全項目を返すと文脈が尽きる。**候補を絞るツール**と**一件を取るツール**に割り、一覧は識別子と最小限の項目だけを返す。

```yaml
- name: search_inventory_items
  description: 商品名や型番から在庫の候補を探す。詳細が要るときは get_inventory_item を使う
  input_schema: "keyword: string 必須 / warehouse: string 任意(既定=全倉庫)"
  returns: "items[]: {item_id, name, qty} / total_matched: integer"
  on_error: 「該当なし。keyword を短くするか warehouse を外して再試行せよ」
  max_items: 20件で打ち切り、total_matched を添える
  mutability: read_only
  approval: 不要(read_only)

- name: get_inventory_item
  description: item_id を指定して1件の全項目を取る。id が未知なら先に search_inventory_items を使う
  input_schema: "item_id: string 必須(search_inventory_items が返した値)"
  returns: "{item_id, name, qty, warehouse, updated_at, supplier, storage_condition}"
  on_error: 「item_id が存在しない。search_inventory_items で有効な id を確認せよ」
  max_items: 該当なし(常に1件)
  mutability: read_only
  approval: 不要(read_only)
```

## 使い方
1. 公開する全ツールをこの一枚に書く。欄が埋まっていないツールと、`destructive` なのに `approval` が空のツールは公開しない。
2. `description` と `input_schema` は実装の説明文でなく**この契約が真実**。実装を変える前にここを直す。

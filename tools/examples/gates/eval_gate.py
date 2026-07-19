# 配置先: (生成物の例。skill で自分の環境向けに作り直す)
# 配布元: loop_engineering/tools/examples/gates/eval_gate.py
"""ホールドアウト評価ゲート。基準を1つでも下回れば exit 1 を返す。

    python gates/eval_gate.py preds.csv --threshold 0.5 --min-auroc 0.95

CSV は id,score,label の3列。label は 1=不良 / 0=良品。
score は「不良らしさ」で、大きいほど不良と判定する。
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path


def load(path):
    """CSV を読み、不良側と良品側のスコアに分ける。"""
    with open(path, newline="", encoding="utf-8") as f:
        rows = [(float(r["score"]), int(r["label"])) for r in csv.DictReader(f)]
    pos = [s for s, y in rows if y == 1]
    neg = [s for s, y in rows if y == 0]
    if not pos or not neg:
        raise SystemExit(
            f"不良と良品の両方が要る(片方しか無い、または空): {path}")
    return pos, neg


def auroc(pos, neg):
    """全ての(不良,良品)ペアを総当たりで比べる定義どおりの実装。

    同点は 0.5 点として数える。
    """
    # O(件数の2乗)だが、ホールドアウトが数千件ならこれで足りる。
    win = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return win / (len(pos) * len(neg))


def rates(pos, neg, threshold):
    """運用閾値での見逃し率(FN率)と過検知率(FP率)。"""
    miss = sum(1 for s in pos if s < threshold) / len(pos)
    fp = sum(1 for s in neg if s >= threshold) / len(neg)
    return miss, fp


def main():
    p = argparse.ArgumentParser(description="ホールドアウト評価ゲート")
    p.add_argument("csv_path", help="id,score,label の3列のCSV")
    p.add_argument("--threshold", type=float, required=True, help="運用閾値")
    p.add_argument("--min-auroc", type=float, default=0.95)
    p.add_argument("--max-miss", type=float, default=0.02)
    p.add_argument("--max-fp", type=float, default=0.10)
    p.add_argument("--history", default="",
                   help="履歴の追記先(既定はこのスクリプトと同じ場所)")
    a = p.parse_args()

    pos, neg = load(a.csv_path)
    au = auroc(pos, neg)
    miss, fp = rates(pos, neg, a.threshold)
    checks = [
        ("AUROC", ">=", au, a.min_auroc, au >= a.min_auroc),
        ("見逃し率", "<=", miss, a.max_miss, miss <= a.max_miss),
        ("過検知率", "<=", fp, a.max_fp, fp <= a.max_fp),
    ]
    ok = all(c[4] for c in checks)

    print(f"{a.csv_path}: 不良{len(pos)}件 / 良品{len(neg)}件  "
          f"閾値={a.threshold}")
    for name, op, got, want, passed in checks:
        mark = "OK" if passed else "NG"
        print(f"  {name} {got:.4f}  基準 {op} {want}  {mark}")
    print("PASS" if ok else "FAIL")

    # 履歴を追記する。1回の合否ではなく、推移で劣化に気づくため。
    record = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "csv": a.csv_path,
        "threshold": a.threshold,
        "auroc": round(au, 4),
        "miss_rate": round(miss, 4),
        "fp_rate": round(fp, 4),
        "result": "PASS" if ok else "FAIL",
    }
    # 既定を cwd 相対にすると、実行場所ごとに履歴が散らばる。
    default = Path(__file__).with_name("history.jsonl")
    hist = Path(a.history) if a.history else default
    hist.parent.mkdir(parents=True, exist_ok=True)
    with hist.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

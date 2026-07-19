# 配置先: (生成物の例。skill で自分の環境向けに作り直す)
# 配布元: loop_engineering/tools/examples/gates/ui_gate.py
"""ダッシュボードの前段(機械ゲート)。標準ライブラリのみ。

判定するのは答えが一意に決まる 3 系統だけ。(a) コントラスト比
(b) 合計と内訳の整合 (c) 単位とタイムスタンプの有無。

【このゲートが判定していない項目】
本文が機械ゲートとして挙げる 4 点のうち、「横スクロール無し」と
「スクリーンショット差分」はこのゲートの範囲外。どちらも静的な
HTML 解析では判定できず、実ブラウザでの描画が要るため。
緑(exit 0)のときこそ「4 点すべて見てくれた」と誤解しやすいので、
合否によらず OUT_OF_SCOPE を必ず出力する。欠落を exit 0 の裏に
隠さないための出力なので、消してはいけない。

見やすさ、わかりやすさ、情報の優先順位、視線の流れも、機械では
満点を出せないので後段の人間ゲート
(tools/templates/ui_human_gate.md) に残す。ここへ足してはいけない。

HTML 側の記法(規約):
  カード: class="metric" id=.. data-value=.. data-unit=..
          data-updated=..
  合計  : 上に data-sum-of="id1,id2"。自身の data-value が
          内訳の和と誤差 1% 以内であること。
  色    : 同じ要素の style に color と background-color を両方
          書く(16進のみ。継承は追わず、書かれた組だけを検査する)。
"""
import argparse
import re
import sys
from html.parser import HTMLParser

TOLERANCE, MIN_RATIO = 0.01, 4.5  # 合計の許容誤差 1% / WCAG AA の下限
HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
FG = re.compile(r"(?<![-\w])color\s*:\s*([^;]+)")
BG = re.compile(r"background(?:-color)?\s*:\s*([^;]+)")

# このゲートが見ていない項目と、その理由。
# 静的 HTML 解析の原理的な限界であって、実装の手抜きではない。
OUT_OF_SCOPE = [
    ("横スクロール無し",
     "静的HTMLでは判定不能。実ブラウザでの幅計算が要る"),
    ("スクリーンショット差分",
     "静的HTMLでは判定不能。実ブラウザでの描画が要る"),
]


def ratio(fg: str, bg: str) -> float:
    """2 色のコントラスト比(WCAG 2.x の相対輝度から求める)。"""
    def lum(code: str) -> float:
        h = code.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        ch = [v / 12.92 if v <= 0.03928
              else ((v + 0.055) / 1.055) ** 2.4 for v in ch]
        return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]
    lo, hi = sorted((lum(fg), lum(bg)))
    return (hi + 0.05) / (lo + 0.05)


class Collector(HTMLParser):  # 指標カードと、色の組を書いた要素を集める
    def __init__(self) -> None:
        super().__init__()
        self.cards: list[dict[str, str]] = []
        self.pairs: list[tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        style = a.get("style", "")
        fg, bg = FG.search(style), BG.search(style)
        f, b = (m.group(1).strip() if m else "" for m in (fg, bg))
        if HEX.match(f) and HEX.match(b):  # 両方 16進の組だけ検査する
            self.pairs.append((f, b))
        if "metric" in a.get("class", "").split():
            self.cards.append(a)


def check(html: str) -> list[tuple[str, bool, str]]:
    """項目別に (名前, 合否, 説明) を返す。ここに主観の項目を足さない。"""
    c = Collector()
    c.feed(html)
    bad = [f"{f} on {b} = {ratio(f, b):.2f}:1"
           for f, b in c.pairs if ratio(f, b) < MIN_RATIO]
    by_id = {x["id"]: x for x in c.cards if x.get("id")}
    sums: list[str] = []
    for k in (x for x in c.cards if x.get("data-sum-of")):
        parts = [p.strip() for p in k["data-sum-of"].split(",") if p.strip()]
        if any(p not in by_id for p in parts):
            sums.append(f"{k.get('id', '?')}: 内訳の id が見つからない")
            continue
        total = float(k.get("data-value", "nan"))
        got = sum(float(by_id[p].get("data-value", "nan")) for p in parts)
        if abs(total - got) > abs(total) * TOLERANCE:
            sums.append(
                f"{k.get('id', '?')}: 合計 {total} だが内訳の和は {got}")
    lack = [f"{x.get('id', '?')}: {n} が無い" for x in c.cards
            for n in ("data-unit", "data-updated") if not x.get(n)]
    return [
        ("contrast", not bad,
         "; ".join(bad) or f"{len(c.pairs)} 組が基準以上"),
        ("sum", not sums, "; ".join(sums) or "合計と内訳が一致"),
        ("required", not lack,
         "; ".join(lack) or f"カード {len(c.cards)} 件に単位と時刻"),
    ]


def print_out_of_scope() -> None:
    """範囲外の項目を知らせる。PASS でも省略しない(誤解を防ぐため)。"""
    print("[このゲートが判定していない項目]")
    for name, why in OUT_OF_SCOPE:
        print(f"  - {name}: {why}")
    print("  上記は合否に含まれない。実ブラウザでの確認が別に要る。")


def main() -> int:
    ap = argparse.ArgumentParser(description="ダッシュボードHTMLの機械ゲート")
    ap.add_argument("html", help="検査対象の HTML ファイル")
    with open(ap.parse_args().html, encoding="utf-8") as fp:
        results = check(fp.read())
    for name, ok, msg in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {msg}")
    print_out_of_scope()  # exit 0 のときも必ず出す
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())

# 配置先: (生成物の例。skill で自分の環境向けに作り直す)
# 配布元: loop_engineering/tools/examples/gates/schema_gate.py
"""提供層スキーマ契約の凍結ゲート。旧契約と新契約を比べ、
非互換変更があれば exit 1。

使い方:
  python tools/gates/schema_gate.py 〈旧 serving.yaml〉 〈新 serving.yaml〉

YAML のまま扱う理由: 第25章の contracts/serving.yaml と名前を
揃えるため。PyYAML は標準に無いので、この契約が使う最小サブセット
(トップレベルの key: value と `- { ... }` の列定義)だけ自前で読む。
"""

import sys
from pathlib import Path


def _split_top(text: str) -> list[str]:
    """括弧の外側のカンマだけで分割する(decimal(12,2) を壊さないため)。"""
    parts, buf, depth = [], "", 0
    for ch in text:
        depth += (ch in "([") - (ch in ")]")
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return parts


def parse(path: Path) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """契約を (トップレベルのスカラ, 列名 -> 列属性) に読む。"""
    top: dict[str, str] = {}
    cols: dict[str, dict[str, str]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        body = line.strip()
        if not body:
            continue
        if body.startswith("- {") and body.endswith("}"):
            items = _split_top(body[3:-1])
            pairs = (p.split(":", 1) for p in items if ":" in p)
            attrs = {k.strip(): v.strip() for k, v in pairs}
            if "name" in attrs:
                cols[attrs["name"]] = attrs
        elif ":" in body and line[0] not in " -":
            k, v = body.split(":", 1)
            top[k.strip()] = v.strip()
    return top, cols


def diff(old: Path, new: Path) -> list[str]:
    """非互換変更を列挙する。

    粒度/契約名の変更、列の削除、型やキーの変更、必須列の追加。
    """
    (otop, ocols), (ntop, ncols) = parse(old), parse(new)
    issues = []
    for key in ("contract", "grain"):
        if otop.get(key) and otop.get(key) != ntop.get(key):
            issues.append(
                f"非互換: {key} の変更 "
                f"[{otop.get(key)} -> {ntop.get(key)}]")
    for name, attr in ocols.items():
        if name not in ncols:
            issues.append(f"非互換: 列の削除または改名 [{name}]")
            continue
        for key in ("type", "pk"):
            a = attr.get(key, "なし")
            b = ncols[name].get(key, "なし")
            if a != b:
                issues.append(
                    f"非互換: 列 {name} の {key} 変更 [{a} -> {b}]")
    for name, attr in ncols.items():
        if name not in ocols and attr.get("nullable") == "false":
            issues.append(
                f"非互換: nullable でない列の追加 [{name}] "
                "既存の書き手が壊れる")
    return issues


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(
            f"usage: python {Path(argv[0]).name} old.yaml new.yaml",
            file=sys.stderr)
        return 2
    issues = diff(Path(argv[1]), Path(argv[2]))
    if issues:
        tail = f"NG: 非互換変更 {len(issues)} 件。再凍結の承認が必要。"
        print("\n".join([*issues, tail]), file=sys.stderr)
        return 1
    print("OK: 互換な変更のみ。凍結は保たれている。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

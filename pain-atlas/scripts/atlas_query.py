#!/usr/bin/env python3
"""按关键词、类别、四型、引证等级检索 references/genealogy.md。

只读操作：仅读取本 Skill 目录内的谱系表，不联网、不写文件、不调用子进程。

用法:
    python atlas_query.py --list
    python atlas_query.py --keyword 畏
    python atlas_query.py --type 存在性 --level A
    python atlas_query.py --category 现象学
    python atlas_query.py --id G27

退出码:
    0 有匹配
    1 无匹配
    2 文件缺失或格式错误
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FIELDS = ("类别", "命题", "著作", "篇目", "术语", "等级", "四型", "误引")
ENTRY_RE = re.compile(r"^###\s+(G\d+)\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+([^:：]+)[:：]\s*(.*)$")


def load_entries(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw in text.splitlines():
        line = raw.rstrip()
        match = ENTRY_RE.match(line)
        if match:
            current = {"ID": match.group(1), "名称": match.group(2)}
            entries.append(current)
            continue
        if current is None:
            continue
        if line.startswith("## ") or line.startswith("---"):
            current = None
            continue
        field = FIELD_RE.match(line)
        if field:
            key = field.group(1).strip()
            if key in FIELDS:
                current[key] = field.group(2).strip()

    return entries


def matches(entry: dict[str, str], args: argparse.Namespace) -> bool:
    if args.id and entry.get("ID", "").upper() != args.id.upper():
        return False
    if args.category and args.category not in entry.get("类别", ""):
        return False
    if args.type and args.type not in entry.get("四型", ""):
        return False
    if args.level and entry.get("等级", "").strip().upper() != args.level.upper():
        return False
    if args.keyword:
        needle = args.keyword.lower()
        haystack = " ".join(entry.get(key, "") for key in ("名称",) + FIELDS).lower()
        if needle not in haystack:
            return False
    return True


def print_entry(entry: dict[str, str]) -> None:
    print(f"### {entry.get('ID', '?')} {entry.get('名称', '')}")
    for key in FIELDS:
        value = entry.get(key)
        if value:
            print(f"- {key}: {value}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检索痛苦谱系表（只读，不联网，不写文件）",
        add_help=True,
    )
    parser.add_argument("--keyword", "-k", help="全文关键词，忽略大小写")
    parser.add_argument("--type", "-t", help="按四型过滤，如 存在性、关系性")
    parser.add_argument("--category", "-c", help="按类别过滤，如 现象学、宗教学")
    parser.add_argument("--level", "-l", help="按引证等级过滤：A、B、C 或 —")
    parser.add_argument("--id", help="按条目 ID 精确匹配，如 G27")
    parser.add_argument("--list", "-s", action="store_true", help="只输出 ID 与名称")
    parser.add_argument("--path", help="谱系表路径，默认取 ../references/genealogy.md")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass

    root = Path(__file__).resolve().parent.parent
    table = Path(args.path) if args.path else root / "references" / "genealogy.md"
    if not table.is_file():
        print(f"找不到谱系表：{table}", file=sys.stderr)
        return 2

    try:
        entries = load_entries(table)
    except (OSError, UnicodeError) as exc:
        print(f"读取失败：{exc}", file=sys.stderr)
        return 2

    if not entries:
        print(f"谱系表未解析出任何条目，请检查格式：{table}", file=sys.stderr)
        return 2

    hits = [entry for entry in entries if matches(entry, args)]
    if not hits:
        print("无匹配条目。可去掉部分条件，或用 --list 查看全部。", file=sys.stderr)
        return 1

    if args.list:
        for entry in hits:
            print(
                f"{entry.get('ID', '?'):<4} {entry.get('名称', ''):<14}"
                f"[{entry.get('类别', '')}] [{entry.get('等级', '')}] {entry.get('四型', '')}"
            )
        print(f"\n共 {len(hits)} 条 / 全表 {len(entries)} 条")
        return 0

    for entry in hits:
        print_entry(entry)
    print(f"共 {len(hits)} 条 / 全表 {len(entries)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())

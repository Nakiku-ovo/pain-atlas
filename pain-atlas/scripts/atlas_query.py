#!/usr/bin/env python3
"""按关键词、类别、四型、引证等级检索 references/genealogy.md，并校验资料表完整性。

只读操作：仅读取本 Skill 目录内的谱系表，不联网、不写文件、不调用子进程。

用法:
    python atlas_query.py --list
    python atlas_query.py --keyword 畏
    python atlas_query.py --type 存在性 --level A
    python atlas_query.py --category 现象学
    python atlas_query.py --id G27 --id G34
    python atlas_query.py --verify

退出码:
    0 有匹配 / 校验通过
    1 无匹配
    2 文件缺失或解析失败
    3 校验不通过
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = ("类别", "命题", "著作", "篇目", "术语", "等级", "四型", "误引")
OPTIONAL_FIELDS = ("覆盖",)
ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

CONTROLLED_TYPES = ("肉身性", "认知性", "存在性", "关系性")
ALLOWED_LEVELS = ("A", "B", "C", "—")
MIN_ENTRIES = 50

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
            if key in ALL_FIELDS:
                current[key] = field.group(2).strip()

    return entries


def parse_types(value: str) -> list[str]:
    return [token.strip() for token in value.split("/") if token.strip()]


def verify_entries(entries: list[dict[str, str]]) -> list[str]:
    """校验资料表结构，返回问题清单。空清单表示通过。"""
    issues: list[str] = []

    if len(entries) < MIN_ENTRIES:
        issues.append(f"条目数 {len(entries)} 少于下限 {MIN_ENTRIES}，资料表可能被截断")

    ids = [entry.get("ID", "") for entry in entries]
    if len(set(ids)) != len(ids):
        duplicated = sorted({value for value in ids if ids.count(value) > 1})
        issues.append(f"ID 重复：{', '.join(duplicated)}")
    expected = [f"G{index:02d}" for index in range(1, len(entries) + 1)]
    if ids != expected:
        issues.append(f"ID 不连续：期望从 G01 到 G{len(entries):02d} 顺序排列")

    for entry in entries:
        label = entry.get("ID", "?")
        for field in REQUIRED_FIELDS:
            if not entry.get(field, "").strip():
                issues.append(f"{label} 缺少必填字段「{field}」")

        level = entry.get("等级", "").strip()
        if level and level not in ALLOWED_LEVELS:
            issues.append(f"{label} 等级「{level}」不在 A/B/C/— 之内")

        raw_types = entry.get("四型", "").strip()
        if raw_types:
            tokens = parse_types(raw_types)
            if not tokens:
                issues.append(f"{label} 四型为空或无法解析")
            for token in tokens:
                if token not in CONTROLLED_TYPES:
                    issues.append(f"{label} 四型含非法取值「{token}」，只允许四个受控词")

    return issues


def matches(entry: dict[str, str], args: argparse.Namespace) -> bool:
    if args.id:
        wanted = {value.upper() for value in args.id}
        if entry.get("ID", "").upper() not in wanted:
            return False
    if args.category and args.category not in entry.get("类别", ""):
        return False
    if args.type and args.type not in parse_types(entry.get("四型", "")):
        return False
    if args.level and entry.get("等级", "").strip().upper() != args.level.upper():
        return False
    if args.keyword:
        needle = args.keyword.lower()
        haystack = " ".join(entry.get(key, "") for key in ("名称",) + ALL_FIELDS).lower()
        if needle not in haystack:
            return False
    return True


def print_entry(entry: dict[str, str]) -> None:
    print(f"### {entry.get('ID', '?')} {entry.get('名称', '')}")
    for key in ALL_FIELDS:
        value = entry.get(key)
        if value:
            print(f"- {key}: {value}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检索痛苦谱系表并校验完整性（只读，不联网，不写文件）",
        add_help=True,
    )
    parser.add_argument("--keyword", "-k", help="全文关键词，忽略大小写")
    parser.add_argument("--type", "-t", help="按四型过滤：肉身性 / 认知性 / 存在性 / 关系性")
    parser.add_argument("--category", "-c", help="按类别过滤，如 现象学、宗教学")
    parser.add_argument("--level", "-l", help="按引证等级过滤：A、B、C 或 —")
    parser.add_argument("--id", action="append", default=[], help="按条目 ID 精确匹配，可重复使用")
    parser.add_argument("--list", "-s", action="store_true", help="只输出 ID 与名称")
    parser.add_argument("--verify", action="store_true", help="只校验资料表结构，不做检索")
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
        print("谱系表未解析出任何条目。条目须以 `### G01 名称` 起头，字段行须为 `- 字段: 值`", file=sys.stderr)
        return 2

    if args.verify:
        issues = verify_entries(entries)
        print(f"## 资料表校验：{table.name}")
        print(f"- 条目数：{len(entries)}（下限 {MIN_ENTRIES}）")
        if issues:
            print(f"- 结果：不通过，共 {len(issues)} 项")
            for issue in issues:
                print(f"  - {issue}")
            return 3
        print("- 必填字段：齐全")
        print("- 等级取值：合法")
        print("- 四型取值：全部落在受控词表内")
        print("- 结果：通过")
        return 0

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

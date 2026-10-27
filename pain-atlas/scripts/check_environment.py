#!/usr/bin/env python3
"""只读环境检查：确认本 Skill 的资料表完整且结构合法、检索脚本可运行。

不联网、不写文件、不安装、不修改配置、不读取凭据。

用法:
    python check_environment.py

输出四种状态之一:
    ready         全部就绪，直接进入正常流程
    partial       可选能力缺失，核心流程照常
    needs_setup   资料表损坏或不完整，必须先修复
    unavailable   Skill 目录损坏

退出码:
    0 ready
    1 partial
    2 needs_setup
    3 unavailable
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_REFERENCES = (
    "genealogy.md",
    "typology.md",
    "paths.md",
    "citation-rules.md",
    "crisis-boundary.md",
)
OPTIONAL_SCRIPTS = ("atlas_query.py",)
MIN_PYTHON = (3, 8)

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from atlas_query import MIN_ENTRIES, load_entries, verify_entries
except ImportError:  # 检索脚本缺失时降级为只检查文件存在
    load_entries = None
    verify_entries = None
    MIN_ENTRIES = 50


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass

    root = Path(__file__).resolve().parent.parent
    refs = root / "references"
    scripts = root / "scripts"

    print("## 环境检查")
    print(f"- Skill 目录：{root.name}")

    if not (root / "SKILL.md").is_file():
        print("- 总体状态：unavailable")
        print("- 故障项：SKILL.md 缺失，Skill 目录不完整")
        print("- 下一步：停止，重新获取完整 Skill 包")
        return 3

    version = sys.version_info
    print(f"- Python：{version.major}.{version.minor}.{version.micro}")
    python_ok = (version.major, version.minor) >= MIN_PYTHON

    missing = [name for name in REQUIRED_REFERENCES if not (refs / name).is_file()]
    print(f"- 必需资料表：{len(REQUIRED_REFERENCES) - len(missing)}/{len(REQUIRED_REFERENCES)} 就绪")
    for name in missing:
        print(f"  - 缺失：references/{name}")

    if missing:
        print("- 总体状态：unavailable")
        print("- 故障项：核心资料表缺失，判型与对位无法依据任何数据完成")
        print("- 下一步：停止。不要凭记忆替代缺失的资料表，那会直接导致编造引文")
        return 3

    # 资料表结构校验：截断、字段缺失、等级或四型取值非法都会在这里被拦住
    entries = None
    issues: list[str] = []
    if load_entries is not None and verify_entries is not None:
        try:
            entries = load_entries(refs / "genealogy.md")
            issues = verify_entries(entries)
        except (OSError, UnicodeError) as exc:
            issues = [f"资料表无法读取：{exc}"]

        if issues:
            print(f"- 资料表校验：不通过，共 {len(issues)} 项")
            for issue in issues[:12]:
                print(f"  - {issue}")
            if len(issues) > 12:
                print(f"  - 另有 {len(issues) - 12} 项未列出，运行 atlas_query.py --verify 查看全部")
            print("- 总体状态：needs_setup")
            print("- 故障项：谱系表结构损坏或不完整，检索结果会漏条或错配")
            print("- 下一步：修复 references/genealogy.md 后重新运行本检查；修复前不要拿它做对位")
            return 2

        print(f"- 资料表校验：通过（{len(entries)} 条，下限 {MIN_ENTRIES}）")
    else:
        print("- 资料表校验：未执行（atlas_query.py 不可用）")

    absent_scripts = [name for name in OPTIONAL_SCRIPTS if not (scripts / name).is_file()]

    if not python_ok:
        print("- 总体状态：partial")
        print(f"- 缺失可选项：Python 需 {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+，当前不满足")
        print("- 受影响功能：谱系检索需改用目视读表")
        print("- 降级：直接读 references/genealogy.md，按「类别」「四型」两栏筛选，结果等价")
        print("- 下一步：照常执行分析，检索走人工读表")
        return 1

    if absent_scripts:
        print("- 总体状态：partial")
        print("- 受影响功能：谱系检索与资料表校验脚本不可用")
        print("- 降级：直接读 references/genealogy.md，按「类别」「四型」两栏筛选，结果等价")
        print("- 下一步：照常执行分析")
        return 1

    print("- 已通过：SKILL.md、五份资料表、资料表结构校验、检索脚本、Python 运行时")
    print("- 缺失必需项：无")
    print("- 缺失可选项：无（联网核验不属本次检查范围）")
    print("- 总体状态：ready")
    print("- 下一步：直接进入判型与对位流程")
    return 0


if __name__ == "__main__":
    sys.exit(main())

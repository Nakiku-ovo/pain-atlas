#!/usr/bin/env python3
"""只读环境检查：确认本 Skill 的资料表完整、检索脚本可运行。

不联网、不写文件、不安装、不修改配置、不读取凭据。

用法:
    python check_environment.py

输出四种状态之一:
    ready         全部就绪，直接进入正常流程
    partial       可选能力缺失，核心流程照常
    needs_setup   必需项缺失
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

    absent_scripts = [name for name in OPTIONAL_SCRIPTS if not (scripts / name).is_file()]
    if absent_scripts:
        print(f"- 可选脚本缺失：{', '.join(absent_scripts)}")

    if missing:
        print("- 总体状态：unavailable")
        print("- 故障项：核心资料表缺失，判型与对位无法依据任何数据完成")
        print("- 下一步：停止。不要凭记忆替代缺失的资料表，那会直接导致编造引文")
        return 3

    if not python_ok:
        print(f"- 总体状态：partial")
        print(f"- 缺失可选项：Python 需 {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+，当前不满足")
        print("- 受影响功能：谱系检索需改用目视读表")
        print("- 降级：直接读 references/genealogy.md，按「类别」「四型」两栏筛选，结果等价")
        print("- 下一步：照常执行分析，检索走人工读表")
        return 1

    if absent_scripts:
        print("- 总体状态：partial")
        print("- 受影响功能：谱系检索脚本不可用")
        print("- 降级：直接读 references/genealogy.md，按「类别」「四型」两栏筛选，结果等价")
        print("- 下一步：照常执行分析")
        return 1

    print("- 已通过：SKILL.md、五份资料表、检索脚本、Python 运行时")
    print("- 缺失必需项：无")
    print("- 缺失可选项：无（联网核验不属本次检查范围）")
    print("- 总体状态：ready")
    print("- 下一步：直接进入判型与对位流程")
    return 0


if __name__ == "__main__":
    sys.exit(main())

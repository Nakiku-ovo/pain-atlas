# 配置指南

本 Skill 的核心流程（判型、对位、引证、给路）只依赖资料表本身，不需要任何账号、密钥或联网。仅"谱系检索"这一项能力依赖本地 Python。

未配置时不会阻断核心流程，只是检索要改成目视读表。

## python-runtime

- **用途**：运行 `scripts/atlas_query.py`，按四型、类别、引证等级、关键词过滤谱系表。不配置时改为直接读 `references/genealogy.md`，结果等价，只是慢。
- **类型与必要性**：本地运行时，可选。缺失时状态为 `partial`。
- **支持版本**：Python 3.8 及以上。3.8 以下语法不保证兼容。
- **官方主页**：https://www.python.org/
- **官方文档**：https://docs.python.org/3/
- **登录网址**：不需要
- **Token / Key / OAuth 入口**：不需要
- **登录后路径**：不适用
- **权限与 scope**：仅需读取本 Skill 目录内的文件；不需要网络、不需要写入、不需要管理员权限。

### 配置步骤

1. 打开 https://www.python.org/downloads/ 下载对应平台的最新稳定版。
2. Windows 安装时勾选 "Add python.exe to PATH"；macOS 用官方安装包或 `brew install python`。
3. 新开一个终端，运行下面"验证方式"中的命令。
4. 回到本 Skill 目录，运行 `python scripts/check_environment.py`，看到 `总体状态：ready` 即配置完成。

Linux 发行版一般自带 Python 3，可先跳过第 1—2 步直接验证。

### 验证方式

```bash
python --version
python scripts/check_environment.py
python scripts/atlas_query.py --list
```

第三条应输出 50 行条目清单。若报"找不到谱系表"，说明 Skill 目录不完整，而不是 Python 的问题。

### 凭据与安全

本依赖不涉及任何凭据。`atlas_query.py` 与 `check_environment.py` 均只读本 Skill 目录内的 Markdown 与自身代码，不联网、不写文件、不调用子进程、不读取环境变量。

### 轮换与撤销

不适用（无凭据）。卸载时删除整个 Skill 目录即可，系统不会残留配置。

如已全局安装 Python 而希望移除，Windows 走"设置 → 应用 → 卸载"；macOS 用官方卸载脚本或 `brew uninstall python`；Linux 用发行版的包管理器移除。移除前请确认其他工具不依赖它。

**核验日期：2026-10-27。**

## 联网核验（不属于依赖项）

`references/citation-rules.md` 要求在三种情况下联网核对：用户问具体译本或版次、用户质疑出处真实性、需要确认术语中译惯例。

联网能力由宿主对话环境提供，不需要在本 Skill 内配置。没有联网时，按规则明说"未联网核对"，不猜测版本与页码。

## 不需要配置的东西

以下常见项在本 Skill 中均不涉及，出现相关引导即为多余：MCP 服务、CLI 工具、第三方 API、账号登录、OAuth、付费额度、模型选择、代理设置。

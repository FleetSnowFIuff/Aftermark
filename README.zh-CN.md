# Aftermark

**收藏好方法，让你的 Agent 下次用上。**

[English](README.md) · [下载当前版本](https://github.com/FleetSnowFIuff/Aftermark/releases/latest) · [MIT](LICENSE)

给 Coding Agent 的本地收藏夹：保留来源、收藏意图、适用项目，以及实际使用后的纠正。浏览器、CLI 和支持 MCP 的 Agent 共用一份收藏库。

## 三步开始

需要 **Python 3.11+**。[下载源码 ZIP](https://github.com/FleetSnowFIuff/Aftermark/releases/latest/download/Aftermark-source.zip)，解压后运行：

| 平台 | 首次安装 | 打开应用 |
| --- | --- | --- |
| Windows | 双击 `setup.cmd` | 双击 `start-aftermark.cmd` |
| macOS / Linux | `sh setup.sh` | `sh start-aftermark.sh` |

1. 打开 **http://127.0.0.1:43821**，保存一条经验，或导入三个示例。
2. 在「连接 Agent」复制 Codex 接入命令，或其他客户端的 MCP 配置。
3. 选择准确的项目名，生成项目指引，放入 Agent 的项目规则，再用一个真实任务检查它如何使用收藏。

项目留空只使用个人通用收藏。生成指引不会修改客户端文件。是否主动检索仍取决于客户端与工作指引。

Aftermark 无需注册或额外模型 API Key。首次安装、抓取网页需要联网；安装后笔记、PDF 和本地关键词检索可离线使用。尚未发布到 PyPI，请使用源码或发布页安装包。

## 可以收藏什么

| 来源 | 已支持 |
| --- | --- |
| 自己的经验 | 笔记、Markdown、TXT、收藏意图和项目纠正 |
| 网页 | 普通网页正文，或明确标注为仅链接的收藏 |
| 论文 | 文本 PDF、原文件保留、页码定位与引用 |
| 视频 | 链接、用户提供的 SRT/VTT 字幕和时间段定位 |

检索会查找正文及当前项目适用的纠正。你和 Agent 阅读来源，判断是否适用、是否已经实现，再记录「仅参考、已采用、已验证、未采用」。资料更新后，旧使用记录不会冒充当前版本的验证结果。

## 接入与使用

激活虚拟环境后执行：

```sh
aftermark --data-dir .local/library config --project my-game
aftermark --data-dir .local/library connect codex
aftermark --data-dir .local/library connect codex --apply
```

第一条生成带项目名的指引；第二条预览 Codex 注册；第三条通过 Codex CLI 注册，冲突配置不会被覆盖。其他支持 MCP 的客户端可使用生成的 JSON。

[Codex 接入与实际调用记录](docs/CODEX.md) · [CLI 与来源读取](docs/USAGE.md)

## 是否真的可用

真实 Codex CLI 和桌面对话已完成检索、按版本读取、使用记录写入与读回。带项目指引的新任务读到了追加纠正，但没有自动写使用记录。这些是合成资料的接入验收，尚未证明真实工程收益；其他客户端及日常主动调用的稳定性仍待验证。[完整验证范围](docs/VALIDATION.md)。

## 数据与边界

启动脚本使用工程内 `.local/library`；CLI 访问同一份数据时加 `--data-dir .local/library`。不指定时，Windows 默认使用 `%LOCALAPPDATA%\Aftermark`，其他平台见英文说明。也可通过 `AFTERMARK_HOME` 指定。多个客户端须指向同一个库。

JSON 备份包含原文件和历史，导入时跳过已有 ID。升级前建议备份；本版仍使用 schema 2、JSON 备份格式 1。本地服务面向个人使用，不应公开暴露。

目前是关键词检索，不是语义搜索；不提供 OCR、自动转录、视频画面理解或云同步。网页提取不执行 JavaScript 或绕过登录。采用和验证要有证据，但系统不替你验证证据；参考资料不会自动变成更高优先级的指令。

[架构](docs/ARCHITECTURE.md) · [短期计划](docs/ROADMAP.md) · [更新记录](CHANGELOG.md)

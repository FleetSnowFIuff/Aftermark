# Aftermark

[GitHub](https://github.com/FleetSnowFIuff/Aftermark) · [MIT](LICENSE) · [Changelog](CHANGELOG.md)

**收藏好方法，让你的 Agent 下次用上。**

[English](README.md) · [版本计划](docs/ROADMAP.md) · [架构说明](docs/ARCHITECTURE.md) · [验证范围](docs/VALIDATION.md)

给 Coding Agent 的本地收藏夹：保存来源、你为什么收藏、适用项目，以及用错之后的纠正。浏览器、命令行和支持 MCP 的 Agent 共用一份本地知识库。

第一版实现完整的「收藏 → 检索 → 阅读 → 记录使用 → 纠正 → 再检索」链路。它不训练模型、不把检索命中当成适用性结论，也不假装读懂了只有链接的视频。

## 启动

需要 **Python 3.11+**。[下载 v0.1.1 源码](https://github.com/FleetSnowFIuff/Aftermark/archive/refs/tags/v0.1.1.zip) 并解压，或克隆本仓库。

| 平台 | 首次安装 | 打开应用 |
| --- | --- | --- |
| Windows | 双击 `setup.cmd` | 双击 `start-aftermark.cmd` |
| macOS / Linux | `sh setup.sh` | `sh start-aftermark.sh` |

启动脚本统一使用工程内的 `.local/library`。连接 Agent 时，请从界面复制这个收藏库的配置。命令行访问同一份数据时，Windows 使用 `.venv\Scripts\aftermark --data-dir .local/library ...`，macOS/Linux 使用 `.venv/bin/aftermark --data-dir .local/library ...`。直接运行不带 `--data-dir` 的 `aftermark` 会访问下文说明的系统默认库，两者不会自动合并。

也可以手动创建虚拟环境，然后在其中执行 `python -m pip install -e .`。项目尚未发布到 PyPI，请使用源码安装。

访问 **http://127.0.0.1:43821**。macOS/Linux 将 `.venv\Scripts\` 换为 `.venv/bin/`。

首次安装需要联网；安装后，笔记、PDF 文本提取、检索和本地界面可离线使用。无需注册、下载模型或提供额外模型 API Key。抓取网页时才访问你提供的来源地址。

先点击「导入三个示例」，再在「带入任务」中输入「改善跳跃输入容错」。可以查看原文、补充纠正、记录实际使用结果。示例为项目自写内容，不冒充外部论文或视频。

## 首版能力

| 入口 | 已实现 | 边界 |
| --- | --- | --- |
| 笔记 | 手写内容、Markdown、TXT | 保留原文，不自动生成摘要 |
| 网页 | 普通 HTML/文本抓取，或仅收藏链接 | 不渲染 JavaScript，不登录或绕过付费墙 |
| PDF | 文本提取、页码标记、保存原文件 | 无 OCR，扫描件会明确提示 |
| 视频 | 收藏链接，导入 SRT/VTT 或手动粘贴字幕 | 不自动下载、转录或理解画面 |
| 检索 | 英文词与中文双字关键词匹配 | 不是语义搜索；适用性由你和 Agent 判断 |
| 记忆 | 意图、个人/项目范围、纠正、版本号 | 项目名精确匹配，不擅自修改用户要求 |
| 记录 | 仅参考、已采用、已验证、未采用 | 采用和验证必须附证据；系统不替你验证证据 |
| 迁移 | JSON 导入/导出，包括原文件和历史 | 已存在 ID 跳过，不隐式覆盖 |

## 连接 Agent

在「连接 Agent」复制配置与工作指引，或执行：

```sh
aftermark config
```

生成配置使用当前 Python 的绝对路径与当前数据目录。手动添加到支持 MCP 的客户端，不会覆盖已有配置。也可以让 Agent 使用 CLI。

建议指引已经包含：任务前检索、先阅读来源与纠正、检查项目是否适用或已实现、真实记录结果。**提供 MCP 工具不等于每个 Agent 都会自动调用**；客户端实际表现需要逐一验证。

工具为 `recall`、`read_bookmark`、`save_bookmark`、`add_correction`、`record_usage`，另提供显式调用的 `use_my_knowledge` 提示模板。

## 数据与维护

默认数据位置为 Windows 的 `%LOCALAPPDATA%\Aftermark`；其他平台见英文 README。可用 `aftermark --data-dir 路径 ...` 指定，也可设置 `AFTERMARK_HOME`。多个客户端须使用同一目录。

数据库、上传内容和个人设置不应提交 GitHub；项目已忽略数据库及本地开发数据。归档可恢复。修改收藏或添加纠正会提升版本，旧记录仍保留原版本，不会自动变成新版本的验证结果。

## 后续只做短线打磨

v0.1 完成总体框架；v0.1.x 处理真实试用问题；v0.2 重点打磨导入与客户端接入。首轮不扩展到云协作、自动科研、多模型调度或大规模视频基础设施。具体验收标准见 [版本计划](docs/ROADMAP.md)。

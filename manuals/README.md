# dsh-python 开发手册总目录

> DeepSeek Harness 的 Python 重实现 —— 每个模块的开发手册，覆盖到函数级技术细节。
> 各手册均由源码逐函数提取（签名经 `inspect` 验证），与代码同步。
> wanter 专题（四法则/机制/量化指标/图表）见仓库根目录 **[WANTER.md](../WANTER.md)**。

| 编号 | 手册 | 覆盖模块 | 源码 |
|---|---|---|---|
| 00 | [总览与架构](00-总览与架构.md) | 全局心智模型、架构线对应表 | — |
| 01 | [插件内核](01-kernel-插件内核.md) | Context / EventBus / Service / Loader / PluginTree | `dsh/kernel/` |
| 02 | [会话日志](02-session-会话日志.md) | SessionEventMap / surface / derive / SessionStore | `dsh/session/` |
| 03 | [工具系统](03-tools-工具系统.md) | schema / define_tool / 五段管线 / 展示词汇 | `dsh/tools/` |
| 04 | [LLM 接缝](04-llm-模型接缝.md) | 消息词汇 / 流协议 / 适配器 / DeepSeek / mock | `dsh/llm/` |
| 05 | [Agent 与循环](05-agent-智能体与循环.md) | Agent / Inbox / 注册表 / 审批 / 驱动循环 | `dsh/agent/` |
| 06 | [System Prompt](06-prompt-系统提示词.md) | 分节 / 变量 / 工具 provider / 组装 | `dsh/prompt/` |
| 07 | [持久化与执行](07-持久化与执行-持久化-文件系统-子进程.md) | JSONL / 崩溃修复 / fs 围栏 / bash 工具 | `dsh/persistence/` `dsh/fs/` `dsh/subprocess/` |
| 08 | [高级能力](08-高级能力-子代理-目标-压缩-命令-任务-计划.md) | subagent / goal / compaction / commands / jobs / plan / todo | 对应目录 |
| 09 | [组合与启动](09-组合与启动-Profile-Bundle-Patch-Boot-CLI.md) | Profile / Bundle / Patch / boot / CLI | `dsh/config/` `dsh/boot.py` `dsh/cli/` |
| 10 | [服务端与 Web UI](10-服务端-Web界面.md) | FastAPI REST / SSE / 前端协议 | `dsh/server/` |
| 11 | [快速开始与 PyCharm 指南](11-快速开始与PyCharm指南.md) | 安装、运行、密钥、自定义、排障 | — |
| 12 | [新增子系统](12-新增子系统-设置-遥测-存储-技能-Hooks-Preset-Schedule-沙箱-Web.md) | 补齐批次新增缝（函数级） | 对应目录 |
| 13 | [与 TS 版差异对照](13-与TS版差异对照与补齐记录.md) | 逐条差异对照 + 补齐实施记录 | — |
| 14 | [第二批补齐](14-第二批-凭据-计量-指令-修剪-查询-反馈-工作流.md) | credentials / token-meter / agent-instructions / pruner / session-query / feedback / workflow | `dsh/credentials/` `dsh/llm/token_meter.py` `dsh/context/instructions.py` `dsh/compaction/pruner.py` `dsh/session/query.py` `dsh/feedback/` `dsh/workflow/` |
| 15 | [MCP 与 Cron](15-MCP与Cron-模型上下文协议客户端与定时表达式.md) | MCP stdio 客户端 / cron 表达式 | `dsh/mcp/` `dsh/schedule/cron.py` `dsh/schedule/schedule.py` |
| 16 | [wanter 架构设计](16-wanter架构设计手册.md) | 四法则数学建模 / 落层决策 / 实验证据 | `dsh/wanter/` |
| 17 | [第六批补齐](17-第六批-记忆-预设换绑-结构化工作流-请求观测.md) | memory / preset recompose / workflow 结构化输出 / agent/request-done | `dsh/memory/` `dsh/preset/presets.py` `dsh/workflow/workflow.py` `dsh/agent/loop.py` |
| 18 | [Code Mode](18-CodeMode-代码模式.md) | run_code 传输 / Python SDK / 代码执行 seam / 派发桥 / code-only 强制 | `dsh/code/` `dsh/tools/registry.py` |
| 19 | [自指 cordis](19-自指cordis-动态插件运行器.md) | 动态 Cordis Plugin 运行器 / host 沙箱 / inspect 目录 / cordis_* 工具 / 事件四件套 | `dsh/cordis/` |
| 20 | [读写投影类](20-读写投影-会话投影-工作区-会话引用.md) | sessionProjections / workspaceRegistry / sessionReferenceResolver | `dsh/projection/` `dsh/workspace/` `dsh/context/session_reference.py` |

## 阅读顺序建议

- 全局理解：00 → 01 → 05 → 09
- 扩展开发：03（加工具）、04（加 provider）、08（加能力）、examples/my_plugin.py
- 界面改造：10
- 排障与运行：11

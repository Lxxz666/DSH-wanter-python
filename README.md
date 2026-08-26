# dsh-python

**DeepSeek Harness 的 Python 重实现** —— 一切皆插件的智能体框架。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![Tests](https://img.shields.io/badge/tests-230%20passed%20%C2%B7%201%20skipped-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Manuals](https://img.shields.io/badge/manuals-21%20%E7%AB%A0-orange)]()
[![Lines](https://img.shields.io/badge/dsh%20%E5%8C%85-13k%2B%20%E8%A1%8C-blueviolet)]()

用纯 Python 完整复刻 dsh 的架构线：**Cordis 式插件内核**（Context 服务仓库、四种事件派发、
可逆效应、YAML 配置树 + 热重载）、**事件溯源会话日志**、**五段工具管线**、**LLM 接缝**、
**Agent 驱动循环**、持久化、Profile/Bundle/Patch、子代理/目标/压缩/命令/后台任务/工作流/
MCP/Code Mode/自指 cordis/会话投影/工作区，以及 FastAPI + 原生 JS 的流式 Web UI。

> 🌟 **明星特性 wanter**（water+ant）：把 agent 会话变成在「经验势能地形」上流动的水滴——
> 纯梯度 0% 逃逸、加噪声 0% 逃逸，**wanter 100% 逃逸**；路径复用 ≈30 倍加速。
> 详见 **[WANTER.md](WANTER.md)** 与实时 Web 地形面板。

> 每个模块 docstring 都标注对应 TypeScript 版概念；完整架构说明见 `manuals/`（21 章函数级手册）。

## ✨ 为什么值得看

| 能力 | 说明 |
|---|---|
| 插件内核 | Cordis 式：服务仓库 + emit/waterfall/parallel/serial + 可逆效应（`ctx.effect`） |
| 配置热重载 | 改 `cordis.patch.yml` 不重启生效（HMR：替换/插入/禁用 + reconfigure） |
| 事件溯源会话 | 只追加日志 = 单一事实来源；崩溃修复、fork/resume、JSONL/SQLite 双后端 |
| 工具管线 | pre-execute(allow/deny/ask) → 单调 guard → execute → post-execute → result；JSON Schema 子集强制 |
| Agent 循环 | turn/step 状态机、重试上限、审批（事件化）、runMaintenance、request-done 观测 |
| Code Mode | `run_code` 保留传输 + Python SDK 生成 + 子调用派发桥（原生并发契约） |
| 自指 cordis | `cordis_define/run/stop/undefine`：模型定义并运行动态插件（不可变包 + 审批门控） |
| MCP | stdio + Streamable HTTP 双传输（JSON/SSE、会话头） |
| 真沙箱 | Windows Job Object（kill-on-close + 内存上限）+ Linux Landlock（只读 FS + 工作区可写），不可用如实降级 |
| hooks 兼容桥 | 直接读 Claude Code `settings.json` / Codex `config.toml`（matcher/stdin JSON/$VAR 替换） |
| wanter | 势能地形 + 水迹蒸发 + 定向侵蚀：物理启发的经验层，量化指标见 WANTER.md |
| 会话投影/工作区/引用 | sessionProjections（框架驱动）+ workspaceRegistry + 跨会话有界快照 |

## 架构

```mermaid
graph TD
    CLI[CLI run.py] --> Boot[boot: Profile/Bundle/Patch → PluginTree 拓扑挂载]
    Boot --> K[Kernel: Context/EventBus/effects]
    K --> S[Session: 事件溯源日志]
    K --> T[Tools: 五段管线 + Code Mode]
    K --> L[LLM: 适配器接缝]
    L --> A[Agent Loop: turn/step 状态机]
    A --> S
    A --> T
    K --> Sub[subagent/goal/compaction/workflow/cordis/MCP]
    K --> Wanter[wanter: 势能地形/侵蚀]
    A -.tools/result & turn-stopping.-> Wanter
    K --> Web[FastAPI + JS SPA: REST/SSE + 地形面板 + 会话树]
```

## 快速开始（PyCharm）

1. **环境**：Python ≥ 3.10（已在 3.11 验证）。
2. **依赖**：
   ```sh
   pip install -r requirements.txt
   ```
3. **运行**：直接运行 `run.py`（或终端）：

```sh
python run.py web                              # Web UI → http://127.0.0.1:3080
python run.py headless "总结这个目录" --mock     # 一次性运行（无密钥用 --mock）
python run.py --dump-config                    # 查看组合后的配置树
python run.py plugin init myprofile            # 初始化自定义 profile
```

**模型密钥**：支持两种方式（按优先级）：

1. **项目 `.env`**（推荐，密钥不入 git）：仓库根目录建 `.env`，boot 时自动加载：
   ```sh
   # 火山方舟 Agent Plan（dpv4flash）
   DEEPSEEK_API_KEY=ark-xxxxxxxx
   DEEPSEEK_BASE_URL=https://ark.cn-beijing.volces.com/api/plan/v3
   DEEPSEEK_MODEL=deepseek-v4-flash
   DEEPSEEK_DISABLE_THINKING=1     # 推理模型 content 直出的关键开关（见下）
   ```
2. **环境变量**：`DEEPSEEK_API_KEY`（必需）、`DEEPSEEK_BASE_URL`（默认官方地址）、
   `DEEPSEEK_MODEL`（默认 `deepseek-chat`）、`DEEPSEEK_DISABLE_THINKING`（默认关）。

未设置密钥时回退内置 **mock 适配器**（离线、确定性），开箱即可运行。

> ⚠️ **推理模型坑（dpv4flash 等）**：火山方舟的 deepseek-v4-flash 等推理模型在流式响应里
> `delta.content` 为空、内容全在 `delta.reasoning_content`。设 `DEEPSEEK_DISABLE_THINKING=1`
> 后适配器注入 `thinking:{"type":"disabled"}`，content 直出、响应更快。更多排错见
> [openai-compatible-llm-integration](https://github.com/Lxxz666) 相关技能。

**验证**：

```sh
python -m pytest tests -q      # 期望 230 passed, 1 skipped（Linux-only）
```

## wanter 一分钟

```python
from dsh.boot import boot
ctx, tree = await boot(profile="headless", mock_llm=True)
# agent 每次成功工具调用 → 沉积；停滞 → 侵蚀 + steer（零循环侵入）
# 实时可视化：GET /api/wanter/terrain（SVG）· /static/wanter.html
```

![wanter 量化指标](examples/wanter_showcase.svg)

| 指标 | 纯梯度 | +噪声 | **wanter** |
|---|---|---|---|
| 双势阱逃逸率 | 0% | 0% | **100%**（386.5 步 / 9.8 次侵蚀） |
| 路径复用斜率 | — | −0.67 | **−21.76（≈30×）** |
| 语义匹配（oracle vs hash） | — | 0% | **100%（1 步）** |

完整四法则数学、运行机制与全部图表 → **[WANTER.md](WANTER.md)**。

## 目录结构

```
dsh_python/
├── run.py                # PyCharm 快速启动入口
├── WANTER.md             # wanter 专题（四法则/机制/量化指标/图表）
├── dsh/
│   ├── kernel/           # 插件内核：Context/EventBus/Service/Loader/PluginTree
│   ├── session/          # 事件溯源会话（SessionEventMap/surface/derive/store/query）
│   ├── tools/            # 工具系统（define_tool/schema/五段管线/展示词汇/Code Mode）
│   ├── llm/              # LLM 接缝（消息词汇/流协议/适配器/DeepSeek/mock/token-meter）
│   ├── prompt/           # System Prompt 组装（分节/变量/工具 provider）
│   ├── agent/            # Agent 句柄/Inbox/注册表/审批/驱动循环
│   ├── persistence/      # 会话持久化（JSONL/SQLite 后端 + 崩溃修复）
│   ├── fs/ subprocess/   # 文件系统/子进程缝（fs_*、bash/pwsh 工具）
│   ├── jobs/ todo/       # 后台任务 / todo_write
│   ├── subagent/ goal/   # 子代理 / 目标域（续轮驱动）
│   ├── compaction/       # 上下文压缩（压力检测 + replace 摘要）
│   ├── commands/ plan/   # 斜杠命令 / 计划模式
│   ├── skill/ hooks/     # Skills / Hooks 桥 + Claude Code·Codex 兼容
│   ├── preset/           # Agent Presets（作用域挂载 + recompose）
│   ├── schedule/         # 定时任务（interval + cron 表达式）
│   ├── sandbox/          # Windows Job Object + Linux Landlock 真沙箱
│   ├── web/ interaction/ # web_fetch·web_search / ask_user
│   ├── context/          # 上下文注入（time-context / AGENTS.md / 会话引用）
│   ├── settings/ storage/ telemetry/ credentials/ feedback/
│   ├── memory/           # 原生记忆（Jaccard 检索 + storage 持久化）
│   ├── code/             # Code Mode（run_code 传输 + Python 代码执行 + SDK）
│   ├── cordis/           # 自指 cordis（动态 Cordis Plugin 运行器）
│   ├── projection/ workspace/  # 会话投影 / 工作区实体注册表
│   ├── workflow/         # 工作流引擎（结构化输出强制）
│   ├── mcp/              # MCP 客户端（stdio + Streamable HTTP）
│   ├── wanter/           # wanter 动力学（引擎/插件/校准/可视化）
│   ├── config/ boot.py cli/   # 组合与启动
│   └── server/           # FastAPI Web 服务（REST/SSE/地形面板/会话树）
├── tests/                # pytest 套件（231 用例 + fixtures；Windows 上 230 passed + 1 skipped）
├── examples/             # 示例插件 + wanter 实验/图表（SVG 产出）
└── manuals/              # 21 章中文开发手册（函数级技术细节）
```

## 核心概念速览

| 概念 | 说明 |
|---|---|
| **Context** | 服务仓库：`ctx.tools` / `ctx.llm` / `ctx.sessions`…按 key 解析，provider 可换 |
| **事件** | `emit`（广播）/ `waterfall`（洋葱中间件）/ `parallel` / `serial` |
| **可逆效应** | 一切注册经 `ctx.effect(disposer)`，卸载逆序回滚（HMR 基础） |
| **Session** | 只追加事件日志（单一事实来源），模型历史由 `derive_messages()` 派生 |
| **工具管线** | pre-execute → 单调 guard → execute → post-execute → result |
| **Profile/Bundle/Patch** | `~/.dsh/profiles/<name>/cordis.patch.yml` 按 id 覆盖任意插件行 |
| **turn/step** | step = 一次模型请求 + 其工具调用；turn = 零或多个 step |

## 自定义（扩展四层次）

1. **改配置**：编辑 profile 的 `cordis.patch.yml` 按 id 覆盖/禁用/插入行（热重载生效）；
2. **装插件**：把你的插件模块放进 profile 的 `bundles/` 或 insert 行指向它；
3. **写插件**（推荐）：继承 `dsh.kernel.Service`，声明 `provides/inject`，在 `apply(ctx)` 里
   注册工具/事件/分节（示例见 `examples/my_plugin.py`）；
4. **改内核**：`dsh/` 下任何服务都是可替换的 provider（能力缝）。

## 文档

- 架构总览与模块手册：[`manuals/README.md`](manuals/README.md)（21 章，函数级）；
- 与 TS 版差异对照与补齐记录：[`manuals/13`](manuals/13-%E4%B8%8ETS%E7%89%88%E5%B7%AE%E5%BC%82%E5%AF%B9%E7%85%A7%E4%B8%8E%E8%A1%A5%E9%BD%90%E8%AE%B0%E5%BD%95.md)；
- wanter 专题：[`WANTER.md`](WANTER.md)。

## 🔍 最新审计与架构问题修复（2026-08 全面审计批次）

双路审计（代码 bug 猎杀 11 个高危模块 + 手册逐模块对照 135 文件 / 744 公开符号），
**10 项真实 bug 全部修复**并配回归测试，详见
[`manuals/13` §15](manuals/13-%E4%B8%8ETS%E7%89%88%E5%B7%AE%E5%BC%82%E5%AF%B9%E7%85%A7%E4%B8%8E%E8%A1%A5%E9%BD%90%E8%AE%B0%E5%BD%95.md#15-第十二批全面审计代码-bug-猎杀--手册对照实施记录)：

| 级别 | 问题 | 修复 |
|---|---|---|
| 🔴 严重 | **surface replace 顺序**：压缩摘要被追加到末尾，派生历史顺序错乱 | 新节点插入被替换区间原位置 |
| 🔴 严重 | **Linux Landlock 后端整体失效**：读/执行进了 handled 却无放行规则 | 补根路径只读放行规则 |
| 🟡 中等 | **schema 假校验**：properties 缺 `type:"object"` 时任何值静默通过 | fail loud 强制声明 |
| 🟡 中等 | **`temperature=0` 被默认值覆盖**（确定性采样失效） | `is not None` 判断 |
| 🟡 中等 | **fork 边界漏检**「前缀结束于 turn 中段」 | turn 深度平衡扫描 |
| 🟢 轻微 | flush 契约恒 True · ApprovalService 空配置崩溃 · `_cancel_cause` 跨 turn 泄漏 · MCP 写失败 pending 泄漏 · **wanter 子任务完成用错坐标**（移除错误目标） | 全部修复 |

✅ 审计结论：kernel / 工具三段调度 / Code Mode 调度器 / cordis 审批竞态 / wanter
数值稳定性 / 投影·工作区·会话引用 —— **无问题**；40 个能力缝全挂载、131 模块
导入零失败、手册与代码三方对齐。回归：`tests/test_audit_fixes.py`（8 项）。

## 🔍 火山方舟接入与框架优化（2026-08-25）

把 LLM 接缝切到**火山方舟 Agent Plan（deepseek-v4-flash）**，并借真实调用审计出
一批「只跑 mock 永远发现不了」的框架 bug，全部修复 + 回归测试；Web UI 全面对标
Hermes 网页端标准重做。

### LLM 接缝（方舟 dpv4flash）

| 改动 | 说明 |
|---|---|
| `DEEPSEEK_MODEL` | 适配器默认模型走环境变量（默认 `deepseek-chat` 向后兼容），不再硬编码 |
| `DEEPSEEK_DISABLE_THINKING` | 注入 `thinking:{"type":"disabled"}`，规避推理模型流式 content 空坑 |
| `dsh/_env.py` | 无依赖 `.env` loader（boot 最先加载，已有环境变量优先） |
| `.gitignore` | `.env` / `.env.*` 入黑名单，密钥绝不提交 |
| `run.py headless` | 真实跑通：普通问答 + **多轮工具调用**（模型调工具 → 执行 → 回复） |

### 框架 bug 修复（方舟真实调用暴露）

| 级别 | 问题 | 修复 |
|---|---|---|
| 🔴 严重 | **多轮工具调用 400**：`messages_to_openai` 把 tool-call 塞进 `content:[{"type":"tool_call"}]`，方舟拒绝（只认顶层 `tool_calls`） | 投影到 assistant 消息顶层 `tool_calls` 数组 + 4 个回归测试（`tests/test_llm_messages.py`） |
| 🔴 严重 | **`loop._default_config` 硬编码 `deepseek-chat`**：自定义端点（方舟）模型名被覆盖 | 尊重适配器 `default_model`（读 `DEEPSEEK_MODEL`） |
| 🟡 中等 | **schedule 垃圾污染**：storage 里 223 条 `interval=0.2s` 同义任务，每次 boot 每秒向所有 agent 注入 223 条消息淹没会话 | 清理 + `register` 去重 + `interval≥1s` 下限校验 |
| 🟢 轻微 | **bash 工具 Windows 无 pwsh 崩溃**（本机只有 git-bash） | `_shell_command` 平台回退：pwsh → bash → powershell |
| 🟢 基建 | **tests 缺 `__init__.py`**：3 failed + 3 errors 全因模块导入失败 | 补齐，全绿 |
| 🟢 生产 | **storage 不随 workspace 隔离**：测试（tmp_path）污染 `~/.dsh/storage.json`，schedule 垃圾任务再次淹会话 | `build_patches` 传 workspace 时同步隔离 storage + settings 到工作区 |
| 🟢 生产 | **JobsService 缺 `timeout` 属性崩溃**（模型调后台任务时） | `_run` 改用 `job.timeout` |

### Web UI（沉浸式极光工作台 · 无侧栏）

| 维度 | 标准 |
|---|---|
| 布局 | **彻底去侧栏**：全屏沉浸式消息流 + 极简玻璃顶栏；会话切换为**顶部下拉浮层**（不常驻）；输入区为**悬浮玻璃输入坞**（聚焦发光上浮） |
| 视觉 | **动态极光背景**：电光青/紫罗兰/品红三色光斑慢速漂移 + Raycast 式斜向流动光带 + 工程网格；深空蓝黑底；玻璃拟态（blur+saturate）；渐变 accent 发光按钮 |
| 交互 | **鼠标光晕跟随**（青蓝径向光晕随 mousemove 移动）、输入坞聚焦光环、卡片 hover 微浮、会话项 hover 位移、发送按钮按压回弹 |
| 主题 | 默认「极光深空」暗色；「雪白晨曦」浅色；设置可调**极光背景强度**（0-100%） |
| Markdown | 自研渲染器：标题/列表/表格/引用/代码块+复制/行内码/粗斜体/链接/hr |
| 思考过程 | reasoning 块 → 「思考过程」折叠面板（默认收起） |
| 设置 | ⚙ 抽屉：provider/模型/温度/max_tokens/主题/字体/密度/极光强度/AGENTS.md·CLAUDE.md·附加md/压缩阈值/自动标题；`GET`/`PUT /api/settings` 持久化 |
| 响应式 | ≤820px 自动抽屉侧栏 |

## 🔍 Web 会话持久化与 UI Bug 修复（2026-08-26 验收通过）

用户实测 Web UI 时发现三连 bug：**对话数据存不了 / 没返回结果 / 报错只看见提示框看不到原因**。
逐层挖出 **6 个连环根因**，全部修复并配回归测试（`tests/test_lazy_resume.py`），
端到端实测通过后已推送 GitHub。

| # | 根因 | 后果 | 修复 |
|---|---|---|---|
| 1 | **Web 服务器模式从不触发持久化 flush**（CLI 有 `flush`，Web 的 driver 没有） | 对话只进内存缓冲、**永不写盘** | turn 结束后 `sessions.flush()` 落盘 |
| 2 | 恢复的会话 **agent 不 live** | 发消息 POST 404 "agent not live"，消息丢弃 | 启动只恢复 Session 元数据；发消息**懒加载 resume** |
| 3 | **模型工具循环无步数上限**（`while True`） | turn 永不结束 → 不落盘 + 不返回 | `MAX_TURN_STEPS=25` 强制终止 + 落盘 |
| 4 | agent driver 用错事件循环 | TestClient/portal 后台线程创建的 driver 被请求级作用域**取消**、跨线程 Event 失效 | driver 锚定**宿主循环**（boot 时记录） |
| 5 | `request/context` 事件**漏注册事件目录** | 续聊 resume 时 `Session.from_seed` 严格校验拒绝 | 补注册进 `EVENT_CATALOG` |
| 6 | 前端 `api()` 只抛状态码、不读响应体 error | 报错信息看不到，只见"发送失败"提示框 | `api()` 带出后端 error 详情 |

**关键能力**：会话现在**跨重启持久化** —— 重启后 `/api/sessions` 完整恢复历史会话，
点开可直接续聊（自动 resume agent），新对话实时落盘 JSONL，刷新不丢。

### 鲸鱼娘页宠 🐳

Web 聊天界面右下角常驻 **DeepSeek 鲸鱼娘** 二次元页宠（手绘 SVG）：

- 蓝发发尾分叉成鲸鱼尾 + 头顶小鲸鱼帽 + 呆毛 + 大眼双高光 + 粉腮红 + 女仆围裙
- **8 个动画**：悬浮呼吸 / 发尾·帽尾·徽章尾摆动 / 眼睛跟随鼠标 / 泡泡上浮
- **点击冒台词** + **AI 思考/兴奋状态联动**（右上角状态灯同源）
- 两轮视觉验收打磨（补鲸鱼尾 / 修嘴 / 修腮红 / 调围裙色）

## 测试

```sh
python -m pytest tests -q   # 230 passed, 1 skipped（Linux-only Landlock 用例）
```

## 许可证

[MIT](LICENSE)

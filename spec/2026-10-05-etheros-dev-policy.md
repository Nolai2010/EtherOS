# EtherOS —— 插件原生 · 内核极简 · 开源大一统操作系统 总体开发方针（Design Spec v3）

> 文档状态：v3（已对齐用户全部硬修正与强化；待用户最终确认 → writing-plans）
> 起草：2026-10-05 ｜ v2→v3：推翻「固定核心非插件」表述、`plugins/` 升格绝对核心、Agent 脚手架收敛为单目录 `.etherkit/`、内核边界对齐「调度+协议解释」
> 方法：Superpowers `brainstorming` 流程；5 批澄清 + 用户修订指令 + 4 项对齐澄清

---

## 0. 文档定位、口号与决策来源

本文档是 **EtherOS** 的总体开发方针，作为后续 `writing-plans` 实施计划的输入。所有结论来自 5 批系统性澄清 + 用户对本版指令 + 4 项对齐澄清，未做任何单方面假设。

**概念定位**：EtherOS 是一个**插件原生（Plugin-Native）的开源大一统操作系统**——内核只做「调度 + 协议/能力解释（路由）+ 加载/隔离」，**零格式知识**；一切应用、格式兼容、驱动、服务、乃至文件管理器/设置/性能监控，全部以**插件**形态存在。新增任何能力 = 写一个**类 MCP 的声明式 JSON** + 把二进制放同级目录。

> ⚠️ **口号 IP 风险（严禁）**：原构想口号「**一切皆插件**」已被 **DeepSeek Harness** 占用，EtherOS **严禁使用**该口号。
> **主口号**：**「融汇万端」(Connect the Unconnectable.)**
> **技术向副口号**（用于架构文档 / 仓库描述）：**「一纸插件声明，兼容百种格式，贯通各类终端」(One plugin manifest, every app format, every device.)**
> 系统描述性 Tagline：**Plugin-Native. Kernel-Minimal.**

**参考工程**：`D:\JunYa\Downloads\huaizi-de-cows-main\huaizi-de-cows-main`（其价值在于可移植 AI-Agent 脚手架：`AGENTS.md` + `.codex/agents/*.toml` + `spec/` + `docs/`，使「换电脑不重新沟通」成立）。EtherOS 的 Agent 脚手架是对该模式的**单目录化升级**（见 §3.4）。

---

## 1. 决策汇总（v3 终版）

| 维度 | 结论 |
|---|---|
| **项目名** | **EtherOS**（原 MicroPlug OS，已全局替换） |
| **概念定位** | 插件原生大一统 OS；主口号「融汇万端 / Connect the Unconnectable.」，技术副口号「一纸插件声明，兼容百种格式，贯通各类终端」；禁用「一切皆插件」 |
| **内核边界** | 内核 = **调度 + 协议/能力解释(路由) + 加载/隔离**；**零格式/零文件系统知识**；驱动也是插件 |
| **插件形态** | 类 MCP 声明式 JSON（`plugin.json` / 应用级如 `douyin.json`）+ 同级二进制；两类：**原生插件**、**兼容桥插件** |
| **没有非插件** | 内核之外**没有任何非插件实体**：驱动/服务/shell/文件管理/设置/性能监控全是 **内建不可卸载插件（shipped plugins）** |
| **目录核心** | **`plugins/` 是整个系统的绝对核心目录**；`apps/system`→内建不可卸载插件集，`apps/user`→可选可替换插件 |
| **跨形态适配** | PC 窗口化、手机全屏/分屏——同一插件描述跨形态适配（容器策略为 manifest 字段） |
| **底座** | 优先评估 **ToaruOS**；保留原生目录与构建系统，**不早期重写内核** |
| **目标架构** | 多架构；优先 **x86-64 与 aarch64**（ToaruOS 已覆盖）；其他仅评估 |
| **运行环境** | 虚拟机优先；本地 QEMU 冒烟，CI 用 GitHub hosted + KVM |
| **项目定位** | 可产品化实验 OS（工程化、合规、CI/发布门槛高） |
| **主许可证** | **MIT**（M1 许可清算后宣布纯 MIT）；上游 UIUC/NCSA 类许可原样保留 + `NOTICE` |
| **第三方许可** | 全替换为同许可（MIT/Apache）；M1 先出「文件级许可清单」 |
| **贡献协议** | **DCO 证书**（每次提交 `Signed-off-by`，CI 自动校验） |
| **扩展机制** | 模块化服务+IPC、插件/扩展点、包管理器、SDK/稳定 API（四项全要） |
| **配置形态** | **集中化、单目录、可随仓库迁移**；构建/运行双轨 |
| **Agent 脚手架** | **单一 `.etherkit/` 目录 + 生成器**，**项目同步（随仓库走，换机/换工具复制即复用，明确非技能市场分发）**，覆盖 5 类 25+ 工具（见 §3.4）；复制一个目录 + 跑一次 `generate.sh` 即迁移 |
| **顶层布局** | 原生底座布局 + 叠加（保可编译） |
| **CI 平台** | GitHub Actions（六项全验 + 可选管线不阻塞） |
| **发布策略** | 语义化版本 + GitHub Releases（ISO/VM/OVA 多形态） |
| **分支模型** | GitHub Flow 简化（main + 短命分支 + PR + DCO） |
| **仓库隔离** | 独立 `etheros` 仓库，不与其它项目仓库混用 |

---

## 2. 技术选型

### 2.1 底座：优先 ToaruOS，不早期重写内核
- **优先评估 ToaruOS** 作为底座（自带 boot/kernel/libc/GUI 与一套用户态程序，保留 GUI 显示栈，避免重写）。**不限定 Linux**——若不满足，评估后换底座并重做许可与架构评估（见 §6 风险 1/2）。
- 保留底座**原生目录与构建系统**，仅在之上叠加载体；不早期重构内核。

### 2.2 插件原生架构（★系统基石）
- **内核极简 + 零格式知识**：内核只提供三项能力——① 进程/线程**调度**；② 读取各插件声明的**协议/能力并路由**（即「协议解释」：kernel 理解 plugin manifest 的 `protocols`/`capabilities` 字段，把请求导向拥有该能力的插件）；③ **加载/隔离**（把插件装入隔离域）。**内核不含任何文件系统格式、应用格式、设备协议逻辑**。
- **一切皆插件（系统内）**：内核之外**没有任何非插件实体**。驱动、系统服务、窗口管理器/shell、文件管理器、设置、性能监控，全都是 **shipped plugins（内建、标记 `uninstallable:false`）**；计算器、记事本、抖音兼容包等是 **optional plugins（可选可替换）**。结构上二者完全同构，区别仅在 manifest 的 `uninstallable` 标志。
- **插件 = 类 MCP 声明式 JSON + 同级二进制**：
  - **原生插件（native）**：`plugin.json` 声明 capabilities/tools/resources，`payload` 指向本系统原生二进制。
  - **兼容桥插件（compat-bridge）**：`plugin.json` 声明它「能处理」某外部格式（如 `ipa`/`exe`/`apk`），`payload` 放该 foreign 二进制，`translator` 指向 `plugins/compat/` 下的翻译运行时。**示例：装抖音 = 写 `douyin.json`（声明 `protocols:["ipa"]`）+ 把 `douyin.ipa` 放同级 → 即可打开。**
- **跨形态适配**：manifest 含 `container` 字段（`desktop:"windowed"` / `mobile:"fullscreen|split"`）；shell（一个内建插件）按当前形态选择容器策略——PC 窗口化、手机全屏或分屏。**同一插件描述，多形态渲染**。

### 2.3 架构与许可
- 多架构抽象 `arch/`；优先 x86-64 与 aarch64（ToaruOS 已覆盖），其他仅评估。
- 主许可 **MIT**（M1 清算后宣布纯 MIT）；上游 UIUC/NCSA 类 `LICENSE` 原样保留 + `NOTICE`；用 **REUSE 规范**做文件级 SPDX 标注，`LICENSES/` 集中；非 MIT/Apache 捆绑组件主动替换为同许可。

### 2.4 扩展机制（四类全要）
- **模块化服务 + IPC**：插件经内核路由的 IPC 互相通信。
- **插件/扩展点**：`plugin.json` schema 即稳定扩展契约（§3.2 `plugins/schema/`）。
- **包管理器**：`packages/` 安装/卸载 optional plugins。
- **SDK/稳定 API**：`sdk/` 给出插件开发稳定 ABI + 头文件 + 文档。

### 2.5 配置系统（集中单目录 + 双轨 + 形态自适应）
- **集中化、单目录、可随仓库迁移**：根 `config/`（整目录随 repo 走，换电脑零成本）。
- `config/default.toml`（运行期默认）、`config/build.toml`（构建期裁剪，类 kconfig）；镜像内 `/etc/os/config.toml` 可覆盖。
- **AI Agent 规则作为一类特殊「开发插件」（`plugins/dev/`）**管理——既享受插件化版本化，又不与系统能力插件混淆。

---

## 3. 目录结构（骨架）

### 3.1 顶层布局原则
**原生底座结构保留不动**，仅叠加 `.etherkit/` 脚手架、`arch/` 抽象、`plugins/` 体系与 CI。确保 `make` 仍能构建。

### 3.2 `plugins/` —— 绝对核心目录（★一切扩展能力的家）
- `plugins/schema/` → `plugin.json` schema（MCP 式原语 + `container` 跨形态字段 + `uninstallable` 标志）。
- `plugins/compat/` → 兼容运行时/翻译器（加载 ipa / exe / apk / 其它格式）；内核只暴露最小加载/隔离接口给它们。
- `plugins/builtin/` → **内建不可卸载插件集**（原 `apps/system` + `core/services` + `core/drivers` + shell/窗口管理器）：文件管理器、设置、性能监控、系统服务、驱动、shell。全部 `uninstallable:false`。
- `plugins/optional/` → **可选可替换插件**（原 `apps/user`）：计算器、记事本、抖音兼容包等。`uninstallable:true`。
- `plugins/dev/` → **开发插件**：AI Agent 规则（特殊类，隔离于系统能力插件）。
- `plugins/<name>/` → 具体插件，如 `plugins/optional/douyin/`（内含 `douyin.json` + `douyin.ipa`）。

> 注：旧概念 `apps/system`、`apps/user`、`core/services`、`core/drivers` 在 v3 中**重分类为 `plugins/` 的子集**；若保留 `apps/` 仅为兼容性视图，其真实来源是 `plugins/builtin` / `plugins/optional`。

### 3.3 多架构目录
- `arch/x86_64/`、`arch/aarch64/`（优先）；`arch/riscv64/` 等仅评估留桩。

### 3.4 可移植 AI-Agent 脚手架 `.etherkit/`（★项目同步 · 单目录迁移 · 覆盖 5 类 25+ 工具）

**关键澄清 —— 项目同步 ≠ 技能分发**：本脚手架解决的是 **「项目同步」**：EtherOS *项目自身*的 Agent 开发上下文（`AGENTS.md`、规则、约定、子代理角色）**随项目仓库走**，换电脑 / 换工具只复制一个目录 + 跑一次 `generate.sh` 即可零成本复用，**无需重新对 Agent 沟通**。它**不是**「技能分发」——即把一套可复用 Skill 包发布到市场、装进 `~/.workbuddy/skills/` 之类、跨项目复用。那是另一种诉求，本规格**明确不做技能市场分发**，`.etherkit/` 的内容由 EtherOS 项目自写、只服务本项目。

**支点（已联网核实，2026-10-05）**：**`AGENTS.md` 是 20+ 工具的跨工具事实标准**，被以下工具**原生读取**：OpenAI Codex、GitHub Copilot、Cursor、Claude Code（兼容读取）、Gemini CLI（可经 `context.fileName` 纳入）、Cline、Devin、Zed、Windsurf、Roo Code、Amazon Q、Continue、Augment、Antigravity、goose 等。这是「单目录事实源 → 生成各工具原生配置」能成立的基座，也使「换工具不重沟通」落地为工程现实。

**架构：「单一事实源 `.etherkit/` + 生成器」**——所有项目级 Agent 上下文集中在 `.etherkit/`，`generate.sh` 把它们展开成各工具的原生配置文件（写进各自正确路径）。**迁移 = 复制 `.etherkit/` 一个目录 + 跑一次 `generate.sh`**。

`.etherkit/` 内部按 5 类组织（内容由 EtherOS 项目自写，非通用技能包）：
```
.etherkit/
├── AGENTS.md                 # 工具无关「单一事实源」：项目契约（栈/命令/约束/子代理规则）
├── skills/                   # Skills 原生类（SKILL.md 格式）：Claude Code(.claude/skills/)、Copilot(.github/skills/)、CodeBuddy/WorkBuddy、OpenCode、Qoder、Kiro
├── agents-md/                # AGENTS.md 系：Codex、OpenCode、Amazon Q、Gemini CLI、Cursor、Windsurf、Aider、Zed、Devin、Factory、Augment、goose
├── rules/                    # 规则文件系（各工具原生子目录，generate 时落到对应路径）
├── prompts/                  # 聊天/系统提示词系（降级层）：豆包工作、ChatGPT Projects/GPTs、Kimi、千问、智谱/GLM、文心、元宝/混元、OpenClaw、Coze/扣子、Dify、飞书/钉钉
├── frameworks/               # 框架/平台（节点 system-prompt.md）：LangGraph、AutoGen、CrewAI、n8n、Zapier
├── subagents/                # 固定子代理角色（沿用 huaizi 并适配 OS）：builder/test-author/acceptance-checker/reviewer/visual-reviewer
└── generate.sh               # 从 5 类 + subagents 生成各工具原生配置（见映射表）；保证 25+ 份永不漂移
```

**`generate.sh` 映射表（已核实各工具原生位置）**：

| 目标工具 | 生成到的原生路径 |
|---|---|
| OpenAI Codex | 根 `AGENTS.md`（+ `.codex/agents/*.toml` 子代理） |
| GitHub Copilot | `.github/copilot-instructions.md`、`.github/skills/*/SKILL.md`、`.github/agents/*.agent.md` |
| Cursor | `.cursor/rules/*.mdc`（亦原生读 `AGENTS.md`） |
| Claude Code | 根 `CLAUDE.md`、`.claude/rules/`、`.claude/skills/`、`.claude/agents/` |
| Gemini CLI | 根 `GEMINI.md`（或经 `context.fileName` 直接读 `AGENTS.md`） |
| Cline | `.clinerules/*.md`（亦原生读 `AGENTS.md`） |
| Windsurf / Devin Desktop | `.windsurfrules` |
| Trae | `.trae/rules/*.md` |
| Zed | `.zed/rules` |
| Roo Code | `.roo/rules/*.md`、`.roo/mcp.json` |
| Amazon Q | `.amazonq/rules/*.md`、`.amazonq/mcp.json` |
| Continue | `.continue/rules/*.md`、`.continue/config.json` |
| Augment | `.augment/rules/*.md`、`.augment/mcp.json` |
| Kiro | `.kiro/steering/*.md` |
| JetBrains AI | `.aiassistant/rules/*.md` |
| Tabnine | `.tabnine/guidelines/*.md` |
| OpenHands | `.openhands/microagents/*.md` |
| Antigravity | `.agent/rules/*.md`、`.mcp.json` |
| Aider | `.aider.conf.yml` + conventions markdown |
| Devin | `devin.md` |
| Bolt / Lovable / Replit | `bolt.instructions.md` / `lovable.instructions.md` / `.replit/ai-rules` |
| 聊天/工作型 AI（无仓库指令标准） | `prompts/system-prompt.md` 模板 + 指引其粘贴/读取 `AGENTS.md`；**不承诺自动加载** |

- **固定角色**（存于 `.etherkit/subagents/`，generate 落 `.codex/agents/` 与各工具 agents 目录）：`builder`、`test-author`、`acceptance-checker`、`reviewer`、`visual-reviewer`（GUI/主题改动时只做视觉复核）。**写实现的 ≠ 审查的**。
- **漂移防护**：`.etherkit/AGENTS.md` 为唯一事实源，各工具原生文件**全部由 `generate.sh` 生成，禁止手工分散编辑**；CI job `spec-consistency` 已含对 `AGENTS.md` 与 `<spec>` 引用一致性的校验，从根上消除「多份规则各自漂移」。

### 3.5 完整树形图（目标骨架）
```
<etheros-repo>/
├── AGENTS.md                      # 工具无关单一事实源（根，generate.sh 生成/指针）
├── README.md
├── LICENSE / NOTICE               # MIT；上游 UIUC/NCSA 存于 LICENSES/
├── CORE_MANIFEST.toml             # 仅声明内核边界（不可换的只有内核本身）
├── config/                        # 集中配置单目录（随仓库迁移）
│   ├── default.toml               # 运行期默认
│   └── build.toml                 # 构建期裁剪
├── kernel/                        # 极简内核：调度 + 协议/能力路由 + 加载/隔离
├── arch/{x86_64,aarch64,riscv64}  # 优先 x86_64/aarch64
├── plugins/                       # ★绝对核心目录：一切皆插件
│   ├── schema/                    # plugin.json schema（MCP 式 + container + uninstallable）
│   ├── compat/                    # 兼容运行时（加载 ipa/exe/apk…）
│   ├── builtin/                   # 内建不可卸载插件（驱动/服务/shell/文件管理/设置/性能监控）
│   ├── optional/                  # 可选可替换插件（计算器/记事本/douyin…）
│   ├── dev/                       # 开发插件：AI Agent 规则
│   └── <name>/                    # 如 optional/douyin/ → douyin.json + douyin.ipa
├── packages/                      # 包管理元数据与打包
├── sdk/                           # 稳定 API 头文件 + ABI + 文档
├── themes/                        # 可换主题（亦为 plugins/optional 下的插件）
├── libs/ boot/                    # 沿用底座
├── .etherkit/                     # ★单目录可移植 Agent 脚手架（复制即迁移）
│   ├── AGENTS.md skills/ agents-md/ rules/ prompts/ frameworks/ generate.sh
├── spec/                          # 版本目标与验收规格
├── docs/{index,development/acceptance-standard,experience-library,subagent-guide}
├── .github/workflows/ci.yml       # CI 流水线
└── .gitignore
```

---

## 4. 里程碑划分（Phase 1 · YAGNI）

| 里程碑 | 目标 | 关键产出 | 出口标准 |
|---|---|---|---|
| **M0 仓库与合规** | 新建独立 `etheros` 仓库 + GitHub remote + 许可/合规基线 + 骨架 + `.etherkit/` 脚手架 | LICENSE(MIT)+NOTICE、REUSE 基线、DCO、`AGENTS.md` + `.etherkit/` + `generate.sh`、空骨架 | `git remote` 可达；`.etherkit/` 复制+生成后 25+ 工具可识别；空构建过 |
| **M1 底座基线** | 评估并拉取 ToaruOS（或备选），x86-64/aarch64 可构建且 GUI 启动 | 底座派生基线、**文件级许可清单** | `make` 成功；VM 启动见 GUI；许可清单覆盖全仓 |
| **M2 插件 schema + 集中配置 + 开发插件自举** | `plugin.json` schema（MCP 式 + `container` + `uninstallable`）、`config/` 单目录、`plugins/dev/` | schema v1、`config/*.toml`、`plugins/dev/` 初版 | schema 可校验示例插件；配置可改启动行为 |
| **M3 兼容插件桩 + 内核最小接口** | 1–2 个 demo 插件（如 Web/脚本型包装 + 简单 ipa/exe 包装）+ 兼容运行时桩 + 内核路由/隔离接口 | `plugins/compat/` 桩、`plugins/optional/douyin/`（示例） | 插件可被加载并窗口化运行 demo；内核未为格式改代码 |
| **M4 内建插件归位** | 把驱动/服务/shell/文件管理/设置/性能监控重分类进 `plugins/builtin/`（`uninstallable:false`） | `CORE_MANIFEST` 仅声明内核边界；CI 阻止改内核 | 内核之外无硬编码非插件实体 |
| **M5 CI 点亮** | GitHub Actions 六项验证 | `.github/workflows/ci.yml` | push/PR 全绿；可选管线不阻塞 |
| **M6 发布通道** | 语义化版本 + GitHub Releases 多形态产物 | 打 tag 自动化、ISO/VM/OVA | Release 含可启动产物 |

**Phase 2（后期）**：exe/ipa/Android/iOS 完整指令集/系统调用/GUI 框架翻译（逐格式立项）；移动端全屏/分屏适配；多架构完整可启动；生产级安全模型；生态文档与适配器补全。

---

## 5. CI 设计（GitHub Actions）

**触发**：`push`/`pull_request` 到 `main`。**Runner**：GitHub hosted `ubuntu-latest`（支持 KVM）。

**Jobs（六项全要，并行 + 门禁）**：
1. **build** — 按 `config/build.toml` 编译内核 + 用户态 + 插件 schema 校验。
2. **vm-smoke** — QEMU/KVM headless 启动镜像，串口捕获，断言到达用户态/GUI 初始化。
3. **license** — REUSE lint + 扫描，确保全文件 SPDX 为 MIT/Apache 且 `LICENSES/` 齐备。
4. **dco** — 校验 PR 内每个提交含 `Signed-off-by`。
5. **lint** — `clang-format`/`clang-tidy`/`cppcheck`。
6. **spec-consistency** — 校验 `AGENTS.md`、`<spec>`、`acceptance-standard.md` 引用与边界一致，防上下文漂移。

**可选管线（不阻塞）**：嵌套虚拟化深度测试、截图比对、多分辨率分屏测试。

**发布（M6）**：`tag` 触发 `release.yml` → 构建 ISO/VM/OVA → 上传 GitHub Release（语义化 `vMAJOR.MINOR.PATCH`）。

---

## 6. 风险与假设（v3）

**1. 内核纯度与底座风险**：ToaruOS 的 Misaka 是**混合模块化内核**，不是纯微内核；EtherOS **不追求纯微内核语义**，采用「用户态服务 + IPC + 可加载兼容运行时」体现插件化。**任何格式兼容都通过用户态兼容层实现，不强制改内核为微内核**，避免与「不重写内核」冲突。

**2. 许可兼容性风险**：ToaruOS 使用 **UIUC/NCSA 类许可**；整体 MIT 派生需先做许可清算表确认。**M1 先出「文件级许可清单」**，全替换同许可后再宣布纯 MIT。字体/图标/捆绑资源可能单独授权。

**3. 多架构风险**：ToaruOS 官方覆盖 **x86-64 与 aarch64**；自研兼容插件层尽量与 CPU 架构解耦，但**非 ELF 格式翻译、二进制兼容、移动形态适配不承诺全架构可启动**。

**4. 插件兼容风险**：`douyin.json` + `.ipa` 这类「写个 json 就能开非原生应用」是**目标形态，不是首版承诺**。首版只做 **plugin schema、本地格式白名单、用户态兼容运行时桩**；exe/ipa/Android/iOS 完整翻译**逐格式立项**。需内核态驱动的格式降级为「实验插件」，不进稳定路径。

**5. VM-first 与 CI 风险**：本地 QEMU 冒烟，CI 用 GitHub hosted + KVM；VirtualBox/VMware 仅人工验证。嵌套虚拟化/截图比对/分屏测试作为**可选管线，不阻塞主线**。

**6. 本地机器限制**：开发机 **16GB、AMD 680M、无 CUDA**。仅做文档、小规模构建、Agent 规则蒸馏、QEMU 轻量验证；**重型编译走 CI，模型训练/推理不本地跑**。

**7. 多 Agent 开发迁移风险（已收敛为「项目同步」单目录）**：覆盖 25+ 工具，分 5 类（Skills 原生 / AGENTS.md 系 / 规则文件系 / 聊天系统提示词系 / 框架平台）。**明确边界：本脚手架是 EtherOS 项目的「项目同步」载体（随仓库走、换机换工具复制即复用），不做「技能分发」（不发布到技能市场、不装进个人 skills 目录）**。策略：以 `.etherkit/` 为唯一事实源，`generate.sh` 按已核实的各工具原生路径展开；`AGENTS.md` 是 20+ 工具跨工具事实标准，作首要输出；聊天/工作型 AI 无统一仓库指令标准，提供 `prompts/system-prompt.md` 降级，**不承诺全部自动加载**。漂移防护由 CI `spec-consistency` + 单事实源生成保证。

**8. 产品化 vs 单人维护风险**：严格 **YAGNI**。M0–M6 只做：插件 schema、集中配置、1–2 个 demo 兼容插件、Agent 规则自举、VM 启动验证。**exe/ipa/移动全屏分屏、多架构、生产安全模型放到后期**。

**9. 仓库隔离风险**：本规格暂存 `docs/superpowers/specs/`；**M0 新建独立 `etheros` 仓库**，搬入 `AGENTS.md`、插件 schema、`.etherkit/`。**不与其它项目仓库混用**。

**10. 命名与一致性风险**：全仓**全局替换 MicroPlug → EtherOS**；避免再出现「MicroPlug OS」「微内核纯净化」等旧表述；`apps/system`/`core/*` 旧概念统一重分类为 `plugins/` 子集。

**11. 口号 IP 风险（严禁）**：「**一切皆插件**」已被 **DeepSeek Harness** 占用，EtherOS **严禁使用**。主口号 **「融汇万端」(Connect the Unconnectable.)**；技术副口号 **「一纸插件声明，兼容百种格式，贯通各类终端」(One plugin manifest, every app format, every device.)**；系统 Tagline **Plugin-Native. Kernel-Minimal.**。

---

## 7. 下一步（衔接 writing-plans）

- 待用户最终确认 v3 全部修正（口号已定为「融汇万端 / Connect the Unconnectable.」+ 技术副口号「一纸插件声明，兼容百种格式，贯通各类终端」）。
- 确认后调用 `writing-plans`，将 M0–M6（Phase 1）拆为带验收点的实施计划；Phase 2 标注为后期。
- 实施起点 **M0**：新建独立 `etheros` 仓库 + GitHub 同步 + 合规基线 + `.etherkit/` 脚手架自举，直接对应「Git 远程 + GitHub 同步 + 可点亮 CI」。

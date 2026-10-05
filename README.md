# EtherOS

> **融汇万端 (Connect the Unconnectable.)**
> 技术副口号：一纸插件声明，兼容百种格式，贯通各类终端 (One plugin manifest, every app format, every device.)
> Tagline: **Plugin-Native. Kernel-Minimal.**

插件原生、内核极简的开源大一统操作系统（概念阶段 → M0 骨架）。

- 内核只做 **调度 + 协议/能力解释(路由) + 加载/隔离**，零格式知识。
- 内核之外没有非插件实体：驱动/服务/shell/文件管理器/设置/性能监控 = `plugins/builtin/` 内建不可卸载插件；计算器、抖音兼容包等 = `plugins/optional/` 可选插件。
- 新增能力 = 写类 MCP 的声明式 `plugin.json` + 把二进制放同级目录，不改内核。
- 底座：优先评估 ToaruOS（M1 启动），不早期重写内核。许可 MIT（清算前保留上游 LICENSE+NOTICE），DCO，REUSE。

> ⚠️ 本项目不使用口号「一切皆插件」（已被 DeepSeek Harness 占用）。

## 仓库导航

| 目录 | 内容 |
|---|---|
| `spec/` | 总体开发方针（当前：`2026-10-05-etheros-dev-policy.md` v3）与版本规格 |
| `docs/` | 项目文档（索引制：`docs/index.md`）；`experience-library/` 教训库 |
| `kernel/` | 极简内核（M0 阶段仅边界声明） |
| `arch/` | x86_64 / aarch64（优先）、riscv64（留桩） |
| `plugins/` | ★绝对核心：schema / compat / builtin / optional / dev |
| `config/` | 集中配置单目录（随仓库迁移） |
| `packages/` `sdk/` `themes/` | 包管理 / 稳定 API / 主题 |
| `.etherkit/` | **Agent 项目同步单一事实源**（见下） |

## AI 协作 / 多电脑迁移（核心特性）

仓库内 `.etherkit/` 是所有 AI 工具上下文的单一事实源，`bash .etherkit/generate.sh` 一次生成 25+ 工具的原生配置（AGENTS.md / CLAUDE.md / GEMINI.md / .cursor/rules / .clinerules / .trae/rules / .github/copilot-instructions.md / .codex/agents …），生成物随仓库提交。

**换电脑 = clone 即用**：新机器上任何支持读取仓库指令文件的 AI 工具立刻拥有完整项目上下文，无需重新沟通。详见 `.etherkit/README.md`。

## 开发流程（摘要）

写实现 ≠ 做审查（不同上下文，禁止自评）；验收标准是外部合格线；一个修复一个核验；教训沉淀到 `docs/experience-library/`。完整 11 步流程见根 `AGENTS.md`。

## 状态

- [x] M0 骨架：目录、`.etherkit/` 自举、CI（etherkit 一致性检查）
- [ ] M0 收尾：GitHub remote、许可清算基线
- [ ] M1：ToaruOS 底座评估 + 文件级许可清单
- [ ] M2–M6：插件 schema → 兼容桩 → 内建插件归位 → CI 六项 → Releases

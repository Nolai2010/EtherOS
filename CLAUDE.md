# AGENTS.md —— EtherOS 项目契约（单一事实源）

> 本文件存于 `.etherkit/AGENTS.md`，是所有 AI 工具项目上下文的**唯一**事实源。
> 根目录 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` / `.cursor/rules/` 等均为 `bash .etherkit/generate.sh` 的**生成物**——改规则请改本文件后重新生成，**禁止手改生成物**。

## 目标

开发 **EtherOS**：插件原生、内核极简的开源大一统操作系统。
- 主口号：**融汇万端 (Connect the Unconnectable.)**
- 技术副口号：一纸插件声明，兼容百种格式，贯通各类终端 (One plugin manifest, every app format, every device.)
- 系统 Tagline：Plugin-Native. Kernel-Minimal.
- ⚠️ **禁用口号「一切皆插件」**（已被 DeepSeek Harness 占用）。

## 仓库结构

- `spec/`：总体开发方针与各版本规格。当前方针：`spec/2026-10-05-etheros-dev-policy.md`。
- `docs/`：项目文档。新增文档必须更新 `docs/index.md`；`docs/experience-library/` 记录已解决问题、复发规则与教训。
- `kernel/`：极简内核——只做 **调度 + 协议/能力解释(路由) + 加载/隔离**，**零格式知识**。
- `arch/`：多架构抽象（x86_64 / aarch64 优先，riscv64 留桩）。
- `plugins/`：★**绝对核心目录**，一切扩展能力的家（schema / compat / builtin / optional / dev）。
- `config/`：集中配置单目录（`default.toml` 运行期 / `build.toml` 构建期），随仓库迁移。
- `packages/`、`sdk/`、`themes/`：包管理元数据 / 插件稳定 API 与 ABI / 可换主题。
- `.etherkit/`：AI Agent 脚手架**项目同步**单一事实源（本目录 + `generate.sh`）。

## 实现约束（铁律）

1. **内核零格式知识**：不给内核添加任何文件系统格式、应用格式（ipa/exe/apk）、设备协议逻辑；格式兼容一律走 `plugins/compat/` 用户态兼容运行时。
2. **全系统皆插件（系统内）**：驱动/服务/shell/文件管理器/设置/性能监控 = `plugins/builtin/` 内建不可卸载插件（`uninstallable:false`）；计算器、抖音兼容包等 = `plugins/optional/`（`uninstallable:true`）。二者结构同构，仅 manifest 标志不同。
3. **新增能力 = 声明式 JSON + 同级二进制**（类 MCP 的 `plugin.json`），不改内核代码。
4. **不早期重写内核底座**（优先评估 ToaruOS）；保留底座原生目录与构建系统，仅叠加。
5. **YAGNI**：Phase 1（M0–M6）只做 schema、集中配置、1–2 个 demo 兼容插件、Agent 自举、CI、发布；exe/ipa 完整翻译、移动分屏、多架构完整启动、生产安全模型放 Phase 2。
6. **许可与合规**：MIT（M1 许可清算前保留上游 LICENSE + NOTICE）；文件级 SPDX 标注（REUSE）；每次提交带 `Signed-off-by`（DCO）。
7. **当前阶段（M0）**：只做文档、骨架、Agent 脚手架与 CI 点亮，不写内核/插件实现代码。

## 子 Agent 协作

- 固定角色见 `.etherkit/subagents/`（Codex 生成到 `.codex/agents/`）：
  - `builder`：按主 Agent 指定范围写实现；可改代码与必要文件；不改验收标准；不做复核。
  - `test-author`：依据验收标准写/维护测试；不写实现代码。
  - `acceptance-checker`：只核对每条验收标准是否有真实测试覆盖（假覆盖=未覆盖）；只读。
  - `visual-reviewer`：GUI/主题改动时对照基准做只读视觉复核。
  - `reviewer`：完成后只读复核，先核对验收标准，再看代码质量。
- **写实现的 Agent ≠ 审查的 Agent**（不同上下文）；**禁止自评**。
- 派发前主 Agent 必须给出：spec 路径、验收标准路径、测试入口、允许读写范围、返回要求。信息缺失时子 Agent 返回「缺少必要输入」，不得猜路径。
- 最终结论由主 Agent 负责，但必须统一复核改动并运行必要验证，不能照搬子 Agent 结论。

## 必须严格遵守的开发流程（11 步）

1. 主 Agent 读 `docs/development/acceptance-standard.md` 作为外部合格线；AI 不得自行新增、改写或降低。标准缺失/冲突/待定 → 停下请用户确认。
2. `test-author` 依据验收标准设计详细测试用例，输出到 `docs/`。
3. `acceptance-checker` 核对每条标准有真实测试覆盖；未覆盖完整 → 回 step 2。
4. 建立充足观测手段（日志、测试接口、截图、帧序列、可复现步骤）。
5. 按 spec 实现（可由 `builder` 承担）；实现 Agent 不改验收标准与测试口径。
6. 运行测试；失败 → 汇报 + 更新 `docs/experience-library/` → 修复后重跑。
7. 涉及 GUI/主题/画面基准 → 独立 `visual-reviewer` 只读复核（与实现者不同上下文）。
8. 视觉复核不通过 → 汇报修复 → 回 step 6。
9. 独立 `reviewer` 只读复核（先验收标准，后代码质量）。
10. reviewer 不通过 → 汇报修复 → 回 step 6。
11. 测试 + visual-reviewer + reviewer + 主 Agent 复核全部通过 = 开发完成。

## 多工具同步（.etherkit）

- 修改任何 Agent 规则后：`bash .etherkit/generate.sh` 重新生成 25+ 工具的原生配置，并连同源文件一并提交。
- **迁移到新电脑：clone 仓库即用**——各工具原生配置已随仓库提交，打开即有完整上下文，无需与无上下文 Agent 重新沟通；规则变更后再跑一次 `generate.sh` 即可。

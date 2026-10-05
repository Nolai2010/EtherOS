# 验收标准(当前版本:M0 骨架)

> 本文件是**外部合格线**:AI 不得自行新增、改写或降低;发现缺失/冲突/待定 → 停下请用户确认。
> 里程碑推进时,每个新版本在本文档追加对应章节(版本化,不回改旧章节)。

## M0 · 仓库、合规基线、骨架与 .etherkit 自举

| 编号 | 标准 | 验证方式 |
|---|---|---|
| M0-01 | 目录骨架完整:spec/ docs/(index+development+experience-library) kernel/ arch/{x86_64,aarch64,riscv64} plugins/{schema,compat,builtin,optional,dev} config/ packages/ sdk/ themes/ .etherkit/ .github/workflows/ | 目录清单比对 |
| M0-02 | `bash .etherkit/generate.sh` 可在 Git Bash 成功运行,产出覆盖:根 AGENTS.md、CLAUDE.md、GEMINI.md、.cursor/rules/*.mdc、.clinerules/、.trae/rules/、.github/copilot-instructions.md、.codex/agents/*.toml(5 角色) | 运行 + 产物清单 |
| M0-03 | generate.sh 幂等:连续运行两次,第二次 `git status` 无差异 | 运行两次 + git status |
| M0-04 | 生成物与 .etherkit/ 源一致(CI etherkit-consistency 通过) | CI 绿 |
| M0-05 | docs/index.md 与实际文档一一对应(无悬空、无遗漏) | 人工/agent 核对 |
| M0-06 | 总体开发方针已入库 spec/2026-10-05-etheros-dev-policy.md 且内容与 v3 对齐(含项目同步澄清与 generate.sh 映射表) | 与源 diff |
| M0-07 | CORE_MANIFEST.toml 声明内核三能力与禁入清单;与 spec §2.2 一致 | 比对 |
| M0-08 | .gitignore 覆盖构建产物/镜像产物/reports/ | 清单核对 |
| M0-09 | 根 README 含官方口号(主/副/Tagline)且不含禁用口号 | 文本检查 |
| M0-10 | git 仓库初始化完成,初始提交带 Signed-off-by(DCO) | git log --show-signature / --format 检查 |
| M0-11 | REUSE 基线:`LICENSES/MIT.txt` + `REUSE.toml` 存在且映射全仓(spec M0 关键产出"REUSE 基线") | 文件存在 + 内容含 SPDX 映射 |
| M0-12 | 空构建过:`make` 在仓库根目录 exit 0(spec M0 出口标准) | `make` 实跑 exit 0 |
| M0-13 | `.etherkit/` 五类齐全且有实体:skills/ agents-md/ rules/ prompts/ frameworks/ 均含非空文件且被 git 追踪 | `git ls-files .etherkit` 五类各有 ≥1 文件 |

> **勘误(2026-10-05,用户审计发现)**:初版清单遗漏了 spec M0 的"REUSE 基线"与"空构建过",
> 属实现者降标。已按 spec 还原(M0-11/12/13);此事件入 docs/experience-library/lessons.md。
> 依据:用户 2026-10-05 指令"重新用 Superpowers 流程核对" + 批准"全量出计划"。

**M0 明确不做(YAGNI)**:内核/插件实现代码、ToaruOS 拉取、GitHub remote 配置(下一步单独做)、六项 CI 全验(仅 etherkit-consistency)。

## M1+ · 占位

M1(底座基线)/M2(schema+配置)/M3(兼容桩)/M4(内建归位)/M5(CI 六项)/M6(发布)的验收标准在对应里程碑启动时,由用户确认后追加。

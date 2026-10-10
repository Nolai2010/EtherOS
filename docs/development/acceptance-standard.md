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

## M2 · 插件 schema、集中配置生效与开发插件自举

| 编号 | 标准 | 验证方式 |
|---|---|---|
| M2-01 | plugin.schema.json v1 存在于 plugins/schema/,schema_version="1",含 spec §2.2 全部字段(container/uninstallable/payload/protocols/translator/capabilities/tools/resources),且自身通过 JSON Schema 元校验 | 元校验命令实跑 |
| M2-02 | validator 存在且可执行:对仓库插件树校验 exit 0;对任一负例 manifest exit 非 0 并输出原因 | 正/负例实跑 |
| M2-03 | ≥1 个示例插件(optional)通过 validator 全部检查(含目录 uninstallable 规则) | validator 实跑 + manifest 内容比对 |
| M2-04 | 配置生效:config/default.toml [plugins] enabled 驱动插件启用;enabled 中不存在/非法 id → validator 失败 | 注入非法 id 实跑 |
| M2-05 | plugins/dev/ 有 ≥1 个 dev 插件 manifest 通过 validator,且 dev 目录 uninstallable=false 规则被断言覆盖 | validator 实跑 |
| M2-06 | kernel/ 本里程碑零改动 | `git diff v0.1.0-m1..HEAD -- kernel/` 为空 |
| M2-07 | CI 新增插件校验 job/step 且通过 | CI 绿 |
| M2-08 | docs/index.md 与新增文档一致(M0-05 不回退) | 比对 |

## M3 · 兼容插件桩、翻译运行时雏形与内核最小接口

| 编号 | 标准 | 验证方式 |
|---|---|---|
| M3-01 | plugins/compat/ 有 ≥1 个翻译运行时雏形实体：可执行 translator（stub），输入 manifest 与 payload 输出结构化翻译计划 JSON 并声明 stub 未实现真实格式解析（约束 16） | 实跑 translator 断言 exit 0 + 输出含协议与 stub 声明 |
| M3-02 | ≥1 个 compat-bridge 桩插件（douyin 示例）：protocols 含 ipa，translator 指向 plugins/compat/ 实体文件，通过 validator 全部检查；translator 指向不存在文件的负例被拒绝 | validator 正/负例实跑 |
| M3-03 | hello-plugin payload 实体化为可执行脚本（兑现 M2 记档），validator 对其校验通过 | validator 实跑 |
| M3-04 | 协议路由衔接：路由解析器按协议名从 enabled 插件解析出 plugin→translator→payload 结构化路由链；未知协议 → exit 非 0 且输出原因 | 路由器正/负例实跑 |
| M3-05 | 内核最小接口契约存在于 kernel/interfaces/（route/load/isolate 三原语，格式无关）；base/toaruos 零改动；kernel/ 无格式扩展名字面量 | `git diff v0.2.0-m2..HEAD -- base/toaruos` 为空 + `git diff v0.2.0-m2..HEAD -- kernel/` 仅新增 interfaces/ + grep 断言 |
| M3-06 | config [plugins] enabled 含 douyin 且 validator 全树校验 OK；M2 正/负例行为零回退 | validator 实跑 + 旧负例复跑 |
| M3-07 | CI plugin-schema job 含 M3 校验步骤且通过 | CI 绿 |
| M3-08 | docs/index.md 与 plugins/compat/README 更新一致（M0-05 不回退） | 比对 |

## M4 · 内建插件归位（清单层归位：builtin 实体 + 内核边界收紧）

| 编号 | 标准 | 验证方式 |
|---|---|---|
| M4-01 | plugins/builtin/ 有 ≥4 个内建插件实体（shell/files/settings/mon），uninstallable:false，通过 validator 全部检查；payload 为包装桩脚本可 sh 实跑并输出 stub 声明（约束 19，不冒充实体的"运行"） | validator 全树实跑 + payload 实跑断言 stub 输出 |
| M4-02 | CORE_MANIFEST.toml 收紧为仅声明内核边界：[kernel] capabilities 与禁入清单保留（M0-07 不回退），capabilities 与 kernel/interfaces 三原语对齐；[vendored_base] 指针 pinned==submodule 实际 SHA；[shipped_plugins]/[optional_plugins] 分节移除（语义由 plugins/builtin manifests 承载） | 文件实读 + grep + `git -C base/toaruos rev-parse HEAD` 比对 |
| M4-03 | vendored 树零改动：base/toaruos submodule 指针未动、无本地漂移 | `git diff v0.3.0-m3..HEAD -- base/toaruos` 为空 + `git diff --submodule=log` 为空 |
| M4-04 | kernel/ 零格式知识不回退且无实现代码：格式扩展名字面量 grep 零命中；kernel/ 文件清单仅 README + interfaces/* | grep + `git ls-files kernel/` 清单比对 |
| M4-05 | 内核边界守卫工具 tools/check_kernel_boundary.py 存在且 stdlib only；对现状树 exit 0；注入反例（kernel/ 混入实现文件 / pinned 失配 / 能力清单缺项）exit 非 0 且输出原因 | 守卫正/反例实跑 |
| M4-06 | CI 含 vendored 零改动 + kernel 边界断言 step 且通过；plugin-schema job 对 builtin manifests 自动扫描通过 | CI 绿 |
| M4-07 | 零 schema 变更：plugins/schema/plugin.schema.json 相对 v0.3.0-m3 diff 为空；M2/M3 正负例行为零回退 | diff 为空 + 旧负例复跑全 rejected |
| M4-08 | docs 一致：plugins/builtin/README 成员表更新、docs/index.md 登记新条目（M0-05 不回退） | 比对 |

## M5 · CI 点亮（spec §5 六项补齐 → 八 job 全绿）

| 编号 | 标准 | 验证方式 |
|---|---|---|
| M5-01 | license job 存在且绿：reuse lint 通过（CI 内 pip install reuse；默认排除 submodule，base/ 上游以 license-inventory/NOTICE 口径为准）；含"base/ 恒为 submodule"防御断言 | CI 绿 + 本地（或 CI）reuse lint 证据 |
| M5-02 | dco job 存在且绿：PR 与 push 双事件口径均覆盖 Signed-off-by 校验（merge commit 豁免记档） | CI 绿 + 正/反例证据 |
| M5-03 | lint job 存在且绿：clang-format --dry-run（自有 C）+ cppcheck（kernel/）+ pyflakes（tools/*.py 等）全过；扫描结构性排除 base/ | CI 绿 |
| M5-04 | spec-consistency job 存在且绿：docs/index.md 悬空检查 + acceptance-standard 里程碑章节存在性 + .etherkit/AGENTS.md spec 引用存在性；与 etherkit-consistency 分工无重复门禁（记档） | CI 绿 |
| M5-05 | ci.yml 达八 job（etherkit-consistency/plugin-schema/license/dco/lint/spec-consistency/build/vm-smoke），push/PR 全绿 | `gh run view` job 清单 + 全 success |
| M5-06 | 逐 job 递进纪律：license→dco→lint→spec-consistency 顺序，每 job 先本地模拟再 CI 实跑、绿一上一下一 | 台账/run 序列证据 |
| M5-07 | 旧四 job 零回退：etherkit-consistency/plugin-schema/build/vm-smoke 行为与 job 名不变 | CI 绿 + ci.yml diff 复核 |

## M6 · 发布通道（tag → 自动构建 → GitHub Release，三形态产物）

| 编号 | 标准 | 验证方式 |
|---|---|---|
| M6-01 | release.yml 存在：on push tags 'v*' + workflow_dispatch(dry_run) 双触发；build 步骤与 ci.yml build 同配方（toaruos/build-tools:1.99.x + util/build-in-docker.sh，注释互指） | 文件实读 + 双文件配方 diff 比对 |
| M6-02 | 干跑演练成功：workflow_dispatch dry_run=true 实跑产出 etheros-release-artifacts（ISO/kernel/ramdisk）且未创建任何 Release | run 证据 + `gh release list` 无新增 |
| M6-03 | 真实发布成功：v0.6.0-m6 tag push 触发 release.yml，GitHub Release 创建且资产 ≥3 件（image.iso + misaka-kernel + *.igz ramdisk），RELEASE_NOTES.md 为发布说明 | `gh release view v0.6.0-m6 --json assets,tagName,isPrerelease` |
| M6-04 | 语义化版本策略落档：RELEASE_NOTES.md 载明 v0.x.0-mN 惯例与 v1.0.0 留 Phase 1 后用户决策；-mN Release 标记 prerelease | 文件实读 + Release isPrerelease==true |
| M6-05 | OVA 降级记档：差异点 8（Phase 2）在验收报告与 RELEASE_NOTES 如实记录，不冒充 OVA 已支持 | 报告比对 |
| M6-06 | Release 含可启动产物（spec 出口字面）：image.iso 与 ci.yml vm-smoke 消费产物同源同配方（可启动性链路背书） | 配方比对 + vm-smoke 绿证据 |

## M1 · 底座基线(归档:经独立验收)

> 本章节为**归档补录**(2026-10-06 追加):M1 验收执行时本文档尚无 M1 章节(见验收报告口径差异段 1),
> 独立验收以 spec §4 M1 行为依据映射 A1–A9 实测,**9/9 PASS(含 A6 复验)**。
> 验收报告:`docs/reports/2026-10-06-m1-acceptance.md`;分支 feat/m0-m1,HEAD 1318a54。
> 以下条目按 spec §4 M1 行(目标/产出/出口标准)提炼,全部**已达成**。

| 编号 | 标准(已达成) | 验证方式 |
|---|---|---|
| M1-01 | 上游 ToaruOS 已评估并拉取,submodule 锁定 `e77143fd14391d880c3ee11c1524252cdcbfd225`,无本地改动、无漂移 | `git submodule status` + `diff --submodule=log`(A1) |
| M1-02 | CI 构建通道成立:upstream builder 镜像 `toaruos/build-tools:1.99.x` 内 `util/build-in-docker.sh` 构建,三 job(consistency/build/vm-smoke)全绿 | `gh run view`(run 37387961480,A2) |
| M1-03 | `make` 成功(spec 出口标准①):产出 `image.iso`(7.6MB,BIOS+EFI 双引导)与 `misaka-kernel` | CI build job 日志(A3;本机 Windows 不可构建属已知 Ruling 4,证据取 CI) |
| M1-04 | VM 启动见 GUI(spec 出口标准②):headless QEMU 下 serial 捕获 `livecd login:`(与 `apps/login.c:86` 互证)+ QMP screendump 真实帧 | artifact + CI 日志断言 `BOOT EVIDENCE OK`(A5;口径:台账 Task 11 裁定,差异段 3) |
| M1-05 | VM 冒烟证据报告落盘 `docs/reports/m1-vm-smoke.md`,与 CI artifact 三方互证 | 文件比对(A6 FAIL 后补交 dbb6119,复验 PASS) |
| M1-06 | 文件级许可清单 `docs/license-inventory.md` 覆盖全仓边界(spec 出口标准③):MIT/UIUC-NCSA/GPL 构建期边界/DejaVu 缺口如实记档,不宣布纯 MIT | 清单实读(A8;§6 风险 2 口径) |
| M1-07 | REUSE 基线保持:REUSE.toml `**` 映射 + LICENSES/MIT.txt,SPDX 抽查命中 | lint 降级核验(A9;本机无 reuse 模块,差异段 4) |

> 记档(非 FAIL,供终审裁量):aarch64 无独立构建证据(spec 目标句含之,出口标准字面未列,差异段 2)。
> M1 关闭形态:tag `v0.1.0-m1`。

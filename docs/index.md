# docs/index.md —— 文档索引

> 规则:新增/移动文档必须更新本表(来源:参考工程惯例,已写入根 AGENTS.md)。

| 文档 | 用途 |
|---|---|
| `../spec/2026-10-05-etheros-dev-policy.md` | 总体开发方针 v3(权威;口号/内核边界/里程碑/风险) |
| `subagent-guide.md` | 五固定角色的派发规则(必要输入/职责/禁止/输出) |
| `builder-reviewer-separation.md` | 写实现 ≠ 审查的规则与理由 |
| `harness-principles.md` | .etherkit 项目同步原则(单一事实源/生成物纪律/迁移) |
| `development/acceptance-standard.md` | 当前验收标准(外部合格线) |
| `experience-library/README.md` | 教训库说明 |
| `experience-library/lessons.md` | 教训记录(只增不改) |
| `experience-library/active-rules.md` | 复发≥2次问题的强制规则(待首条) |
| `tool-recognition-matrix.md` | M0 出口标准复核证据:25+ 工具原生路径/识别机制/验证状态矩阵 |
| `../plugins/schema/README.md` | 插件 manifest 契约 v1 字段语义表:类型/约束/spec §2.2/§3.2 依据、目录 uninstallable 规则、manifest 命名约定、validator 用法 |
| `../tools/validate_plugins.py` | 插件 manifest 校验器(M2):`python3 tools/validate_plugins.py` 全树校验+config 一致性;`--file` 单文件;`--config` 覆盖配置 |
| `reports/2026-10-06-m0-acceptance.md` | M0 独立验收报告(对抗式,13/13 通过) |
| `reports/2026-10-06-toaruos-survey.md` | M1 底座调研:ToaruOS 许可/依赖/架构/GUI 事实与 SHA 锁定 |
| `reports/2026-10-06-m1-acceptance.md` | M1 独立验收报告(9/9 通过,含 A6 复验;口径差异记档) |
| `reports/m1-vm-smoke.md` | M1 VM 冒烟证据报告:QEMU headless 启动,serial `login:` 取证与 CI artifact 互证 |
| `license-inventory.md` | M1 文件级许可清单:自有 MIT / 底座 UIUC-NCSA 与 4 子模块 / DejaVu 缺口;"纯 MIT"不宣布 |
| `../kernel/interfaces/plugin-routing.md` | 内核最小路由/隔离接口契约(M3):route/load/isolate 三原语,格式无关;同目录 `router_if.h` 为机器可读契约桩(不参与构建) |
| `../tools/route_plugins.py` | 协议路由解析器(M3):`python3 tools/route_plugins.py --protocol <p>` 在 enabled 的 compat-bridge 中按协议解析 plugin→translator→payload 路由链 JSON,未知协议 exit 非 0 |
| `../tools/route_plugins.py` | 同上 `--run <name>`:native 插件经 sh 实跑 payload 并透传输出;compat-bridge 仅调用用户态 translator 出翻译计划,不执行 foreign payload |
| `../plugins/compat/README.md` | compat 目录约定(M3):translator 集合地语义、translator 调用契约(--manifest/--payload、stub-plan-only)、路由链语义与 M3 stub 边界声明 |
| `docs/reports/2026-10-06-m2-acceptance.md` | M2 独立验收报告（8/8 PASS） |
| `docs/reports/2026-10-06-m3-acceptance.md` | M3 独立验收报告（8/8 PASS） |
| `../plugins/builtin/README.md` | 内建不可卸载插件集(M4):清单层归位口径、首批成员表(shell/files/settings/mon 包装桩)、uninstallable:false 规则 |
| `../tools/check_kernel_boundary.py` | 内核边界守卫(M4):`python3 tools/check_kernel_boundary.py` 断言 vendored 指针一致+kernel/ 白名单+格式字面量零命中+manifest 契约对齐;CI etherkit-consistency 每跑 |
| `docs/reports/2026-10-06-m4-acceptance.md` | M4 独立验收报告（9/9 PASS） |
| `docs/reports/2026-10-06-m5-acceptance.md` | M5 独立验收报告（7/7 PASS，3 条 PASS-with-note；含门禁消音红线复核） |
| `docs/reports/2026-10-06-m6-acceptance.md` | M6 独立验收报告（4 PASS / 2 PENDING；含 OVA 降级与 v1.0.0 留决策记档） |
| `../RELEASE_NOTES.md` | 发布说明（M6）：v0.6.0-m6 Phase 1 收官内容、v0.x.0-mN 版本惯例与 v1.0.0 留用户决策、三形态产物与 OVA 降级 Phase 2 记档；release.yml 以 `--notes-file` 消费 |
| `../CONTRIBUTING.md` | 贡献流程（M7-03）：DCO 签核 `git commit -s`（merge commit 豁免记档）、里程碑短命分支 `feat/m<N>-<slug>` → `merge --no-ff` 进主分支 → annotated tag `v0.x.0-mN`、验收闭环（实现者≠审查者、禁止自评、验收未过不合门不打 tag） |

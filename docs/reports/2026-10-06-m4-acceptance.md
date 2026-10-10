# M4 独立验收报告 —— 内建插件归位（清单层归位）

- **验收者**：acceptance-checker（独立上下文，与 M4 实现者不同；Builder≠Reviewer）
- **被验对象**：分支 `feat/m4-builtin`，HEAD `e3249f337a7e171239c78c9413f5e003e8ee3630`（`e3249f3`）
- **仓库**：`I:/etheros`（远端 `github.com/Nolai2010/EtherOS`）
- **执行日期**：2026-10-06
- **依据**：`docs/development/acceptance-standard.md` M4 章节（M4-01~M4-08）+ spec `spec/2026-10-05-etheros-dev-policy.md` §4 M4 行 / §2.2 / §3.2 / §6 风险 8（YAGNI）+ 计划 `2026-10-06-etheros-m4m6-phase1-closeout-draft.md`（APPROVED-BY-CONTROLLER，11 项差异点已裁定）+ SDD 台账 `progress.md` 尾部裁定
- **口径**：偏严，全部实跑；只记录实测输出，不接受口头声明。Python 解释器统一 `C:/Users/JunYa/.workbuddy/binaries/python/versions/3.13.12/python.exe`
- **工作树**：验收前后 `git status --porcelain` 均为空（反例注入全部用后还原，见 M4-05「还原核验」）

---

## 0. 编号映射说明

验收简报的「预期证据源」按证据源分组，其 M4-01~M4-08 序号与标准章节**不一一对应**（M3 验收报告同款现象）。本报告按**验收标准 M4 章节编号**逐条出证，映射如下：

| 简报证据项 | 对应标准编号 | 本报告落点 |
|---|---|---|
| 简报 M4-01（条目存在 + spec §4 映射） | 元检查 | §1 映射核验 |
| 简报 M4-02（CORE_MANIFEST 收紧） | M4-02 | M4-02 |
| 简报 M4-03（builtin 四桩） | M4-01 | M4-01 |
| 简报 M4-04（守卫工具） | M4-05 | M4-05 |
| 简报 M4-05（CI） | M4-06 | M4-06 |
| 简报 M4-06（文档） | M4-08 | M4-08 |
| 简报 M4-07（validator 全树 + 回退） | M4-01 / M4-07 | M4-01 / M4-07 |
| 简报 M4-08（submodule 零改动 + kernel 格式字面量） | M4-03 / M4-04 | M4-03 / M4-04 |

### §1 条目存在性与 spec §4 M4 行映射核验

命令：

```
$ sed -n '60,71p' docs/development/acceptance-standard.md
$ grep -n "M4" spec/2026-10-05-etheros-dev-policy.md
```

证据（标准章节标题与八条编号实存）：

```
## M4 · 内建插件归位（清单层归位：builtin 实体 + 内核边界收紧）
| M4-01 | ... | M4-02 | ... | M4-03 | ... | M4-04 | ... | M4-05 | ... | M4-06 | ... | M4-07 | ... | M4-08 | ...
```

spec §4 M4 行原文（`spec/2026-10-05-etheros-dev-policy.md:194`）：

```
| **M4 内建插件归位** | 把驱动/服务/shell/文件管理/设置/性能监控重分类进 `plugins/builtin/`（`uninstallable:false`） | `CORE_MANIFEST` 仅声明内核边界；CI 阻止改内核 | 内核之外无硬编码非插件实体 |
```

映射逐项：

| spec §4 M4 要素 | 覆盖它的标准条目 | 实测结论 |
|---|---|---|
| 重分类进 `plugins/builtin/` | M4-01 | 4 实体在 `plugins/builtin/`，见 M4-01 |
| `uninstallable:false` | M4-01 | 四 manifest 均 `false`，validator 目录规则强制，见 M4-01 |
| `CORE_MANIFEST` 仅声明内核边界 | M4-02 | 收紧到位，见 M4-02 |
| CI 阻止改内核 | M4-05 + M4-06 | 守卫工具 + CI step 实测，见 M4-05/06 |
| 出口「内核之外无硬编码非插件实体」 | M4-01~06 组合断言（降级口径） | 见口径差异 2 |

§3.2（`spec:92-93`）对照：`plugins/builtin/` → 内建不可卸载插件集，全部 `uninstallable:false`（含 shell / 文件管理器 / 设置 / 性能监控）；M4 首批与之一致。
§6 风险 8（YAGNI，`spec:236`）：M0–M6 只做插件 schema / 集中配置 / 1–2 个 demo 兼容插件 / Agent 规则自举 / VM 启动验证。M4 增量（4 个包装桩 + 1 个守卫脚本 + 1 个 CI step）**无越界实现**，符合。

判定：**PASS**（八条编号齐备，spec §4 M4 行三关键产出 + 出口标准均有对应条目，无遗漏）。

---

## M4-01 · builtin 四桩实体 + validator + payload 实跑 —— PASS

标准：`plugins/builtin/` 有 ≥4 个内建插件实体（shell/files/settings/mon），`uninstallable:false`，通过 validator 全部检查；payload 为包装桩脚本可 `sh` 实跑并输出 stub 声明（约束 19）。

**① 实体存在性 + 可执行位（git mode）**

```
$ git ls-files -s plugins/builtin/
100755 4d1c8d05...  plugins/builtin/files/payload/files
100755 2d256af8...  plugins/builtin/mon/payload/mon
100755 4d686b87...  plugins/builtin/settings/payload/settings
100755 df6042e0...  plugins/builtin/shell/payload/shell
100644 ...           plugins/builtin/{shell,files,settings,mon}/plugin.json
100644 ...           plugins/builtin/{shell,files,settings,mon}/README.md
100644 ...           plugins/builtin/README.md
```

四件三件套齐全（4×3 + 目录 README = 13 文件）；四个 payload 在 git 中均为 **100755**（M3 F1 先例的 `update-index --chmod=+x` 已落实）。

**② manifest 内容（四件同构，示例 shell）**

```json
{
  "schema_version": "1",
  "name": "shell",
  "version": "0.1.0",
  "type": "native",
  "uninstallable": false,
  "payload": "payload/shell",
  "container": { "desktop": "windowed" },
  "capabilities": ["sys.shell"]
}
```

`files`→`fs.browse`、`settings`→`sys.settings`、`mon`→`sys.perfmon`；四件 `uninstallable` 均为 `false`。

**③ validator 全树 + 单件**

```
$ python.exe tools/validate_plugins.py
plugins validation: OK
exit=0

$ for p in shell files settings mon; do python.exe tools/validate_plugins.py --file plugins/builtin/$p/plugin.json; done
plugins validation: OK   (×4)
exit=0 (×4)
```

全树扫描覆盖 **7 个实体**（`git ls-files plugins/ | grep plugin.json`）：4 builtin + `plugins/optional/hello-plugin` + `plugins/optional/douyin` + `plugins/dev/etheros-agent-rules`。

**④ payload 实跑**

```
$ for p in shell files settings mon; do sh plugins/builtin/$p/payload/$p; done
EtherOS builtin stub: shell (wrapper declaration; upstream entity lives in base/toaruos, not relocated by M4)
EtherOS builtin stub: files (wrapper declaration; upstream entity lives in base/toaruos, not relocated by M4)
EtherOS builtin stub: settings (wrapper declaration; upstream entity lives in base/toaruos, not relocated by M4)
EtherOS builtin stub: mon (wrapper declaration; upstream entity lives in base/toaruos, not relocated by M4)
exit=0
```

payload 首行 `#!/bin/sh`，文件权限 `-rwxr-xr-x`；输出仅为 stub 声明，**不冒充实体的"运行"**（约束 19）。

**⑤ README 明示包装上游既有能力**

`plugins/builtin/shell/README.md`（其余三件同构）：

> 本插件是系统能力"shell"的插件形态**声明与包装**（清单层归位，计划差异点 1 口径）：`uninstallable:false`（validator 目录规则），payload 为**包装桩脚本**，仅输出 stub 声明，**不冒充实体的"运行"**（约束 19）。
> 上游对应实体（终端程序）在 vendored 底座 `base/toaruos` 内部**原样保留**（约束 3/18），M4 不搬迁、不包装其内部实现；窗口化真集成属后续里程碑。

四件 README 均已明示；payload 注释同样声明。

**⑥ builtin 语义负例（config enabled 注入 builtin id 被拒）**

计划 M4-T3 Step 4 原文 sed 存在**双重缺陷**，本次按审查确认的修正版执行（详见口径差异 6）：

```
# 原计划版（缺陷复现）
$ sed 's/^enabled = /enabled = ["shell", /' config/default.toml | grep -n "^enabled"
17:enabled = ["shell", false          ← [compat] 行被误命中且未闭合
22:enabled = ["shell", ["hello-plugin", "douyin"]
$ python.exe tools/validate_plugins.py --config <(原计划版)
FAIL: ...\neg-orig.toml config unreadable: Unclosed array (at line 18, column 1)
FAIL: ...\neg-orig.toml missing [plugins] section — config is the single source of plugin enablement (Global Constraint 12)
exit=1                                 ← 挂在"非法 TOML"，未触及被测语义

# 修正版（锚定唯一目标行）
$ sed 's/^enabled = \[/enabled = ["shell", /' config/default.toml | grep -n "^enabled"
17:enabled = false                     ← [compat] 行未受影响
22:enabled = ["shell", "hello-plugin", "douyin"]
$ python.exe tools/validate_plugins.py --config <(修正版)
FAIL: I:\etheros\plugins\builtin\shell\plugin.json enabled id 'shell' must have uninstallable==true (职责 5)
exit=1
```

命中预期 `uninstallable==true` 文案（约束 12：builtin 隐式启用，enabled 只管 optional）。

**⑦ config 现状（builtin 不进 enabled）**：`config/default.toml` `[plugins] enabled = ["hello-plugin", "douyin"]` —— 四个 builtin 均不在列，符合"隐式启用"。

判定：**PASS**。

---

## M4-02 · CORE_MANIFEST.toml 收紧为仅声明内核边界 —— PASS

标准：`[kernel]` capabilities 与禁入清单保留（M0-07 不回退），capabilities 与 `kernel/interfaces` 三原语对齐；`[vendored_base]` pinned == submodule 实际 SHA；`[shipped_plugins]`/`[optional_plugins]` 分节移除。

**① [kernel] 零改动（M0-07 不回退）**

```
$ git diff v0.3.0-m3..HEAD -- CORE_MANIFEST.toml
@@ -1,6 +1,6 @@
-# EtherOS 内核边界声明（唯一不可插件化的部分）
+# EtherOS 内核边界声明（唯一不可插件化的部分）—— M4 收紧版：仅声明内核边界。
...（头注释 3 行）
-[shipped_plugins]
-# 内建不可卸载插件(本质仍是插件,位置 plugins/builtin/):
-uninstallable = false
-# 成员示例: shell / window-manager / file-manager / settings / perf-monitor / drivers / services
-
-[optional_plugins]
-# 可选可替换插件(位置 plugins/optional/):
-uninstallable = true
+[vendored_base]
+path = "base/toaruos"
+pinned = "e77143fd14391d880c3ee11c1524252cdcbfd225"
+license = "UIUC/NCSA (upstream as-is; see NOTICE & docs/license-inventory.md)"
```

diff 仅两个 hunk：头注释 3 行 + `[shipped_plugins]/[optional_plugins]` 8 行删除 → `[vendored_base]` 5 行新增。`[kernel]` 节**在 diff 中零增删行**（capabilities 与 forbidden_in_kernel 仅作上下文出现）。

收紧后 `[kernel]` 实读（`CORE_MANIFEST.toml:11-25`）：

```toml
[kernel]
capabilities = ["schedule", "protocol-route", "load-isolate"]
forbidden_in_kernel = ["fs-format", "app-format", "device-protocol", "ui", "driver"]
```

capabilities 三项、禁入清单五项**逐字保留**，M0-07 不回退成立。

**② pinned 与 submodule 实际 SHA 一致**

```
$ grep pinned CORE_MANIFEST.toml
pinned = "e77143fd14391d880c3ee11c1524252cdcbfd225"
$ git rev-parse HEAD:base/toaruos
e77143fd14391d880c3ee11c1524252cdcbfd225
$ git -C base/toaruos rev-parse HEAD
e77143fd14391d880c3ee11c1524252cdcbfd225
```

三者逐字一致。

**③ shipped/optional 分节移除无残留**

```
$ grep -rn "shipped_plugins\|optional_plugins" --include="*.md" --include="*.toml" --include="*.py" --include="*.json" --include="*.yml" . | grep -v "^./base/"
（唯一命中）.superpowers/.../reports/m4-t1-t2.md、.superpowers/.../reviews/m4-t1-t2-review.md（SDD 过程文档）
            docs/development/acceptance-standard.md:65（M4-02 行对"移除"这一事实的验收描述文本）
```

`CORE_MANIFEST.toml` 本身零命中；无任何功能文件/脚本消费被移除分节（无悬空引用）。SDD 工作区命中属过程记录，非仓库功能面。

**④ capabilities ↔ kernel/interfaces 三原语对齐**

- 契约文档 `kernel/interfaces/plugin-routing.md` §2 三原语：`route`（协议/能力路由）/ `load`（装入隔离域）/ `isolate`（隔离域权限）；§0 定位「内核只做三件事：**调度、协议/能力解释（路由）、加载/隔离**」。
- CORE_MANIFEST capabilities：`schedule`（调度）/ `protocol-route`（路由）/ `load-isolate`（加载+隔离）—— 与 spec §2.2（`spec:60` 内核三项能力：调度 / 协议能力解释路由 / 加载隔离）逐项对应。
- 机器可查形态：`tools/check_kernel_boundary.py` 职责 4 硬断言 `caps == {"schedule","protocol-route","load-isolate"}`，正例实测通过（见 M4-05）。
- 观察（见口径差异 4）：`schedule` 在契约文档中仅于 §0 散文出现，未单列 §2 原语；对齐链为 spec §2.2 + 守卫断言，不影响判定。

判定：**PASS**。

---

## M4-03 · vendored 树零改动 —— PASS

标准：`base/toaruos` submodule 指针未动、无本地漂移。

```
$ git diff v0.3.0-m3..HEAD -- base/toaruos
[空]
$ git diff --submodule=log
[空]
$ git -C base/toaruos status --porcelain
[空]
$ git submodule status
 e77143fd14391d880c3ee11c1524252cdcbfd225 base/toaruos (v2.3.0-799-ge77143fd)
```

四项双查（相对 v0.3.0-m3 的 diff、当前 `--submodule=log`、子仓 `status --porcelain`、`submodule status` 前缀无 `+`/`-`）**全空 / 全一致**。CI 非递归 checkout 下该子检查打印 SKIP（见 M4-06），本地双查补足，无盲区。

判定：**PASS**。

---

## M4-04 · kernel/ 零格式知识不回退 + 无实现代码 —— PASS

标准：格式扩展名字面量 grep 零命中；`kernel/` 文件清单仅 README + interfaces/*。

```
$ git ls-files kernel/
kernel/README.md
kernel/interfaces/plugin-routing.md
kernel/interfaces/router_if.h
$ find kernel -type f | sort
kernel/README.md
kernel/interfaces/plugin-routing.md
kernel/interfaces/router_if.h
$ grep -rEn "\.(ipa|exe|apk)\b" kernel/ ; echo $?
1                      ← 零命中
$ grep -rn "douyin" kernel/ ; echo $?
1                      ← 零命中（M3 先例口径的扩展 token）
$ git diff v0.3.0-m3..HEAD --stat -- kernel/
[空]                   ← kernel/ 本里程碑零改动
```

工作树扫描与 git 清单完全一致（无未跟踪混入），允许集合 = `kernel/README.md` + `kernel/interfaces/*`，`router_if.h` 为契约的机器可读桩（文档 §4 注明 `contract stub, not compiled`，不参与构建）。

判定：**PASS**。

---

## M4-05 · 内核边界守卫工具 —— PASS

标准：`tools/check_kernel_boundary.py` 存在且 stdlib only；对现状树 exit 0；注入反例（kernel/ 混入实现文件 / pinned 失配 / 能力清单缺项）exit 非 0 且输出原因。

**① stdlib only**

```
$ grep -n "^import\|^from" tools/check_kernel_boundary.py
16:import argparse
17:import re
18:import subprocess
19:import sys
20:import tomllib
21:from pathlib import Path
$ wc -l tools/check_kernel_boundary.py
120 tools/check_kernel_boundary.py
```

六个导入全部为标准库（`tomllib` 为 3.11+ 标准库），无第三方依赖，120 行（≤120 上限）。文件头声明「不导入/链接任何 kernel/ 与 base/toaruos 代码」（约束 11 同款工具层纪律）。

**② 正例**

```
$ python.exe tools/check_kernel_boundary.py
kernel boundary: OK
exit=0
```

**③ 反例 1 —— kernel/ 混入实现文件**

```
$ touch kernel/fake.c && python.exe tools/check_kernel_boundary.py
FAIL: kernel whitelist unexpected file under kernel/: kernel/fake.c (kernel must stay README + interfaces/* only)
exit=1
$ rm -f kernel/fake.c
```

**④ 反例 2 —— pinned 失配**（临时 manifest，不动被跟踪文件）

```
$ sed 's/pinned = "e77143fd/pinned = "deadbeef/' CORE_MANIFEST.toml > /tmp/cm-pinned.toml
$ python.exe tools/check_kernel_boundary.py --manifest <tmp>
FAIL: vendored pointer gitlink SHA e77143fd14391d880c3ee11c1524252cdcbfd225 != CORE_MANIFEST pinned deadbeef14391d880c3ee11c1524252cdcbfd225
FAIL: vendored pointer initialized submodule HEAD drifted from pinned deadbeef14391d880c3ee11c1524252cdcbfd225
exit=1
```

**⑤ 反例 3 —— 能力清单缺项**

```
$ sed 's/"load-isolate",//' CORE_MANIFEST.toml > /tmp/cm-caps.toml
$ python.exe tools/check_kernel_boundary.py --manifest <tmp>
FAIL: capabilities must equal ['load-isolate', 'protocol-route', 'schedule'] (kernel/interfaces three primitives, M0-07), got ['schedule', 'protocol-route']
exit=1
```

**⑥ 还原核验**

```
$ git status --porcelain
[空]
$ git diff --stat
[空]
```

反例 1 用 `rm` 还原并复验 `git status --porcelain kernel/` 为空；反例 2/3 全程只写 `/tmp` 临时文件（工具 `--manifest` 覆盖路径即其文档化的负测接口），被跟踪文件零改动；临时文件已删。仓库回到 e3249f3 干净态。

判定：**PASS**（正例 OK；三反例各 FAIL 且 exit 1，原因文案与注入项一一对应）。

---

## M4-06 · CI 集成 —— PASS

标准：CI 含 vendored 零改动 + kernel 边界断言 step 且通过；plugin-schema job 对 builtin manifests 自动扫描通过。

**① step 定义在 etherkit-consistency job**

```
$ grep -n "^  [a-z-]*:" .github/workflows/ci.yml
9:  etherkit-consistency:
51:  plugin-schema:
68:  build:
98:  vm-smoke:

$ sed -n '44,50p' .github/workflows/ci.yml
      - name: "Kernel boundary guard (M4: vendored pin + kernel whitelist + format literals)"
        # 仓库卫生门扩展(计划 M4-T5):vendored 指针一致 + kernel/ 白名单 + 格式字面量零命中
        # + manifest 契约对齐。本 job checkout 为非递归(submodule 未初始化),守卫对 vendored
        # 指针的检查走 git ls-tree HEAD(读 gitlink SHA),不受影响;仅"submodule 已初始化才
        run: python3 tools/check_kernel_boundary.py
```

step 位于行 44，处于 `etherkit-consistency`（行 9）job 内、`plugin-schema`（行 51）之前，符合计划 M4-T5 定位（仓库卫生门，不新占 job 名）。

**② run 37500561806 四 job 全绿**

```
$ gh run view 37500561806 -R Nolai2010/EtherOS
✓ feat/m4-builtin ci · 37500561806
JOBS
✓ plugin manifest schema & config consistency (M2) in 11s  (ID 112396176647)
✓ build ToaruOS base (upstream builder image) in 2m45s      (ID 112396177008)
✓ etherkit single-source consistency in 9s                  (ID 112396177098)
✓ vm smoke (QEMU headless boot evidence) in 33s             (ID 112397438877)

$ gh run view 37500561806 -R Nolai2010/EtherOS --json headSha,headBranch,conclusion
{"conclusion":"success","headBranch":"feat/m4-builtin","headSha":"e3249f337a7e171239c78c9413f5e003e8ee3630"}
```

run 的 `headSha` 逐字等于被验 HEAD **e3249f3**（证据覆盖到位，非滞后 run）。

**③ 守卫 step 步骤级日志（job 112396177098）**

```
$ gh run view --job 112396177098 -R Nolai2010/EtherOS --log | grep "check_kernel\|SKIP\|kernel boundary"
2026-10-06T17:03:35.2990964Z ##[group]Run python3 tools/check_kernel_boundary.py
2026-10-06T17:03:35.2991921Z python3 tools/check_kernel_boundary.py
2026-10-06T17:03:35.3448467Z SKIP: submodule not initialized — local drift checks skipped (CI checkout non-recursive is OK)
2026-10-06T17:03:35.3450478Z kernel boundary: OK
```

**SKIP 分支非静默**：日志明示打印跳过原因（submodule 未初始化），其余检查照常执行并最终 `kernel boundary: OK`。非递归 checkout 下 vendored 指针仍走 `git ls-tree HEAD`（读 gitlink SHA），守卫力不减；本地漂移由 M4-03 双查补足。

**④ plugin-schema job 对 builtin 自动扫描（job 112396176647）**

```
2026-10-06T17:03:36.7771152Z ##[group]Run python3 -m pip install --quiet jsonschema
2026-10-06T17:03:36.7772462Z python3 tools/validate_plugins.py
2026-10-06T17:03:38.1427554Z plugins validation: OK
```

该 job 未作任何 M4 改动（ci.yml diff 仅 +7 行、全部落在 etherkit-consistency），validator 全树扫描对 `plugins/builtin/` 四 manifest **零改动自动生效**并通过。

判定：**PASS**。

---

## M4-07 · 零 schema 变更 + M2/M3 正负例零回退 —— PASS

标准：`plugins/schema/plugin.schema.json` 相对 v0.3.0-m3 diff 为空；M2/M3 正负例行为零回退。

**① schema 零变更**

```
$ git diff v0.3.0-m3..HEAD -- plugins/schema/
[空]
$ git diff --stat v0.3.0-m3..HEAD
 .github/workflows/ci.yml                  |   7 ++
 CORE_MANIFEST.toml                        |  19 ++---
 docs/development/acceptance-standard.md   |  13 ++++
 docs/index.md                             |   2 +
 plugins/builtin/...                       |  13 文件新增
 tools/check_kernel_boundary.py            | 120 ++++++++++++++++++++++++++++++
 18 files changed, 286 insertions(+), 13 deletions(-)
```

`plugins/schema/` 无改动；全量 diff 中不含任何 schema 路径。

**② M2/M3 旧负例复跑（3+1 全拒、原因匹配）**

```
$ python.exe tools/validate_plugins.py --file tests/plugins/negative/bad-container.json
FAIL: tests/plugins/negative/bad-container.json schema: 'fullscreen' is not one of ['windowed']
exit=1

$ python.exe tools/validate_plugins.py --file tests/plugins/negative/bad-uninstallable.json
FAIL: tests/plugins/negative/bad-uninstallable.json directory rule: plugins/optional/ requires uninstallable==true, got False
exit=1

$ python.exe tools/validate_plugins.py --file tests/plugins/negative/compat-bridge-without-translator.json
FAIL: ... schema: 'translator' is a required property
FAIL: ... compat-bridge translator must be under plugins/compat/ (spec §2.2), got None
exit=1

$ python.exe tools/validate_plugins.py --file tests/plugins/negative/compat-bridge-translator-missing.json
FAIL: ... compat-bridge translator 'plugins/compat/no-such/translator.py' does not resolve to an existing file under repo root (spec §2.2, M3-02)
exit=1
```

原因文案与 M2/M3 验收记录一致，零回退。

**③ M3 正例不回退**

```
$ python.exe tools/validate_plugins.py --file plugins/optional/hello-plugin/plugin.json
plugins validation: OK
exit=0

$ python.exe tools/route_plugins.py --protocol ipa >/dev/null && python.exe tools/route_plugins.py | grep -c '"plugin"'
7
exit=0
```

路由 summary 列 7 条（4 builtin + hello-plugin + douyin + dev，≥6 达标），builtin 已进路由视图；`--protocol ipa` 仍解析成功。

判定：**PASS**。

---

## M4-08 · docs 一致 —— PASS

标准：`plugins/builtin/README.md` 成员表更新、`docs/index.md` 登记新条目（M0-05 不回退）。

**① builtin README 成员表四要素齐备**

```
## 成员表(M4 已归位首批 4 件)

| name | capabilities | 上游实体(base/toaruos 内,原样保留) | payload | 语义 |
| `shell`    | `sys.shell`    | 终端程序       | `payload/shell`    | 包装桩:echo stub 声明,不实现 shell 逻辑 |
| `files`    | `fs.browse`    | 文件浏览器     | `payload/files`    | 包装桩:echo stub 声明,不实现文件浏览 |
| `settings` | `sys.settings` | 设置程序       | `payload/settings` | 包装桩:echo stub 声明,不实现设置界面 |
| `mon`      | `sys.perfmon`  | 性能监控程序   | `payload/mon`      | 包装桩:echo stub 声明,不实现性能监控 |
```

四要素（name / capabilities / 上游实体 / payload）齐备并与 M4-01 实测 manifest 逐项吻合（`sys.shell`/`fs.browse`/`sys.settings`/`sys.perfmon`）；表内 payload 路径与 `git ls-files` 一致。README 另含「归位口径（M4，清单层归位）」段、成员规则（manifest 一律 plugin.json、builtin 隐式启用）、后续成员说明。

**② docs/index.md 新增条目**

```
$ git diff v0.3.0-m3..HEAD -- docs/index.md
+| `../plugins/builtin/README.md` | 内建不可卸载插件集(M4):清单层归位口径、首批成员表(shell/files/settings/mon 包装桩)、uninstallable:false 规则 |
+| `../tools/check_kernel_boundary.py` | 内核边界守卫(M4):`python3 tools/check_kernel_boundary.py` 断言 vendored 指针一致+kernel/ 白名单+格式字面量零命中+manifest 契约对齐;CI etherkit-consistency 每跑 |
```

**③ 零悬空（M0-05 不回退）**

```
$ grep -oE '^\| `[^`]+`' docs/index.md | sed 's/^| `//; s/`$//' > /tmp/idx2.txt
count=24
$ while read -r p; do [ -f "docs/$p" ] || [ -f "$p" ] || echo "DANGLING: $p"; done < /tmp/idx2.txt
dangling=0
```

24 条引用逐条 `test -f`（两条 `docs/reports/...` 以仓库根为基准、其余以 `docs/` 为基准），**零悬空**。

判定：**PASS**。

---

## 结论

| 编号 | 判定 |
|---|---|
| §1 条目存在性与 spec §4 映射 | PASS |
| M4-01 builtin 四桩 + validator + payload 实跑 | PASS |
| M4-02 CORE_MANIFEST 收紧（M0-07 不回退） | PASS |
| M4-03 vendored 树零改动 | PASS |
| M4-04 kernel/ 零格式知识 + 无实现代码 | PASS |
| M4-05 内核边界守卫工具（正例 + 三反例） | PASS |
| M4-06 CI 集成（四 job 全绿 + 步骤级证据） | PASS |
| M4-07 schema 零变更 + M2/M3 零回退 | PASS |
| M4-08 docs 一致 | PASS |

**总计：标准条目 M4-01 ~ M4-08 共 8 条，8/8 PASS；元检查（§1）1/1 PASS。缺陷数 0。**

---

## 口径差异（已裁定事项，不计缺陷）

1. **归位语义 = 插件清单层归位，非物理搬迁**（台账差异点① Ruling）：spec §4「重分类进 `plugins/builtin/`」以清单层落点兑现——每个成员是 manifest + 包装桩 payload，上游实体（终端/文件浏览器/设置/性能监控程序）在 `base/toaruos` 内部原样保留（约束 3/18）。口径已由 `plugins/builtin/README.md`「归位口径」段与四件 README 明示，M4-03/M4-04 实测证明 vendored 与 kernel 零改动。**不构成降标**。

2. **M4 出口降级为「声明完备 + 结构守卫」**（台账差异点② Ruling）：spec 出口「内核之外无硬编码非插件实体」在 M4 以 M4-01~06 组合断言兑现（声明齐备 + 守卫工具 + CI 强制），不含真内核路由/装载实现代码；真窗口化集成属后续里程碑。本报告按降级口径核验，八条全部达成。

3. **首批成员范围 = shell/files/settings/mon，驱动/服务不归位**（台账差异点③ Ruling）：spec §4 M4 行列 6 类（驱动/服务/shell/文件管理/设置/性能监控），标准 M4-01 文本已写明「≥4 个（shell/files/settings/mon）」，二者一致；驱动/服务归位属后续里程碑，`plugins/builtin/README.md`「后续成员（规划中，未归位）」段已记档（驱动「驱动即插件」语义已由 `forbidden_in_kernel` 声明承载）。

4. **capabilities ↔ 三原语的对齐形态**：契约文档 §2 三原语名为 `route`/`load`/`isolate`，`schedule` 仅在 §0 散文出现；CORE_MANIFEST 用 `schedule`/`protocol-route`/`load-isolate`。对齐链为 spec §2.2（内核三项能力：调度/协议能力解释路由/加载隔离）+ 守卫职责 4 的硬断言（实测正例通过、反例命中）。**记档**，建议后续里程碑在契约文档 §2 补 `schedule` 原语小节以消除命名粒度差。

5. **编号映射不一致**：验收简报「预期证据源」序号与标准 M4 章节序号不一一对应（按证据源分组）。本报告按标准章节编号出证，映射见 §0（M3 验收报告同款处置）。

6. **计划 M4-T3 Step 4 的 sed 双重缺陷**（属计划缺陷，非实现缺陷）：原文 `s/^enabled = /enabled = ["shell", /` ①`^enabled = ` 在 `config/default.toml` 中匹配两行（`[compat]` 的 `enabled = false` 与 `[plugins]` 的 `enabled = [...]`），②产出 `enabled = ["shell", false` 为**未闭合数组**的非法 TOML。实测复现：`Unclosed array (at line 18, column 1)`——负例挂在配置解析而非被测语义，无法证成约束 12。本次采用审查确认的修正版 `s/^enabled = \[/`（锚定唯一目标行），产出 `enabled = ["shell", "hello-plugin", "douyin"]`，正确命中 `enabled id 'shell' must have uninstallable==true`。

7. **CI 中 vendored 本地漂移子检查打印 SKIP**：`etherkit-consistency` job checkout 非递归、submodule 未初始化，守卫显式打印 `SKIP: submodule not initialized — local drift checks skipped`，其余检查照常。已裁定为「明示跳过、不作失败」，且由本报告 M4-03 本地双查（`git diff --submodule=log` 空 + `git -C base/toaruos status --porcelain` 空）补足，**无静默盲区**。

## 遗留观察（不阻塞，移交 M5/T8 顺带）

1. `docs/index.md` 两条 `docs/reports/...` 条目以仓库根为基准，与其余 22 条以 `docs/` 为基准不一致（M2/M3 遗留，未加重）。
2. 本报告 `docs/reports/2026-10-06-m4-acceptance.md` 尚未登记进 `docs/index.md`——按 M2/M3 先例由关门任务（T8/T10，控制器代笔 plumbing）补登；M4-08 只要求登记 M4 新条目（2 条已登记且零悬空），故不计 FAIL。
3. 四个 builtin 插件无独立 `tests/plugins/negative/` 负例文件（builtin 语义负例以 config 注入形式执行，见 M4-01 ⑥）；若后续需固化负例集可补 `builtin-in-enabled.json`。

---

**STATUS: PASS**

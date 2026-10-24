# M10 独立验收报告 —— translator 真实现（`.desktop` 描述符级端到端翻译）

- **验收者**：general-purpose-1（独立上下文；Builder≠Reviewer≠Acceptance——本验收者与 M10 实现者、M10-4 审查者均相互独立，不替实现背书，不粉饰，不采信任何自评输出；审查报告 `task-m10-4-review.md` 仅作线索来源，每条判定均有本方独立取证命令与输出）
- **被验对象**：分支 `feat/m10-translator`，HEAD `5b0e8b8`（`5b0e8b8defea08d97fd714330f65e006bae59c4a`，提交主题 `feat: demo-desktop-app end-to-end sample + CI translation smoke`）
- **区间**：`e238760..HEAD`，共 **3 个非合并提交**（`0a89954` → `afd003a` → `5b0e8b8`）；对照基线 tag `v0.9.0-m9`（M9 合并进 main 的提交为 `e238760`）
- **仓库**：`I:/etheros`（远端 `github.com/Nolai2010/EtherOS`）
- **执行日期**：2026-10-24
- **依据**：`docs/development/acceptance-standard.md` §`## M10 · translator 真实现（\`.desktop\` 描述符级端到端翻译）`（:130-139，M10-01~M10-06）+ 台账 M10 选题裁定（`.superpowers/sdd/2026-10-05-etheros-m0m1-implementation/progress.md` 第 178 行：诚实边界红线——**描述符级翻译，非二进制指令翻译，不得宣称"支持运行 .desktop 应用"之外的东西**）
- **口径**：偏严。全部判据**自己实跑取证**；CI 取证走 `gh` GET（`gh run view`，headSha 必须逐字等于分支 HEAD，防"陈旧 run"坑）；零回退用 pyyaml 做 **job 级对象比对** + 两次 run 的 job 名集合对象级比对，不做肉眼 diff；夹具与产物全程只落 `/tmp/m10-acc/**`；**未修改仓库 `config/default.toml`**（端到端实证用 /tmp 副本树实现，验收前后 `git status --porcelain` 均为空）
- **写操作范围**：**仅新建本报告一个文件**；未改 ci.yml / release.yml / schema / manifest / tools / translator / README / acceptance-standard.md，未推 tag、未动 main、未派子代理

---

## 0. 判据存在性核验与被验对象定位

```
$ git rev-parse HEAD && git branch --show-current
5b0e8b8defea08d97fd714330f65e006bae59c4a
feat/m10-translator

$ git status --porcelain
（空输出——工作区干净）

$ git log --oneline -4
5b0e8b8 feat: demo-desktop-app end-to-end sample + CI translation smoke
afd003a feat(compat): real .desktop translator (descriptor-level)
0a89954 docs: add M10 acceptance criteria (controller-verified)
e238760 Merge feat/m9-schema-v2: M9 plugin schema v2 (dependencies + topological load)
```

HEAD 与任务书所述 `5b0e8b8` 一致 ✅；分支正确 ✅。

判据实存：`docs/development/acceptance-standard.md:130-139` 的 M10 章节表，M10-01~M10-06 六条编号 / 标准 / 验证方式齐备，无缺项 ✅（该文件由 `0a89954` 入库，+11 行，纯追加）。

选题裁定红线实读（progress.md:178）："**诚实边界必须写明：这是描述符级翻译，不是二进制指令翻译，不得宣称"支持运行 .desktop 应用"之外的东西。**" —— 本报告 M10-04 按此红线独立取证。

判定：**PASS**（判据齐备、被验对象定位准确、无越界动作）

---

## 夹带与 DCO 总检（先行）

### D1 全量文件清单（`v0.9.0-m9..5b0e8b8`，7 个文件全部纯新增）

```
$ git diff v0.9.0-m9..5b0e8b8 --numstat
41	0	.github/workflows/ci.yml
11	0	docs/development/acceptance-standard.md
74	0	plugins/compat/desktop-entry/README.md
291	0	plugins/compat/desktop-entry/translator.py
25	0	plugins/optional/demo-desktop-app/README.md
6	0	plugins/optional/demo-desktop-app/app.desktop
14	0	plugins/optional/demo-desktop-app/plugin.json
$ git diff v0.9.0-m9..5b0e8b8 --numstat | awk '{a+=$1; d+=$2} END {print "total added:", a, "total deleted:", d}'
total added: 462 total deleted: 0
```

**7 个文件、+462/-0 纯新增** ✅。7 个文件全部落在 M10-01~M10-03 的应动范围内（判据入库 / 真 translator + README / 端到端示例三文件 + CI smoke），无计划外夹带。

### D2 逐提交范围（3 个提交，均带 Signed-off-by）

```
$ git log e238760..5b0e8b8 --no-merges --format='%h | %s | sob=%(trailers:key=Signed-off-by,valueonly)'
5b0e8b8 | feat: demo-desktop-app end-to-end sample + CI translation smoke | Nolai <120611751+Nolai2010@users.noreply.github.com>
afd003a | feat(compat): real .desktop translator (descriptor-level) | Nolai <120611751+Nolai2010@users.noreply.github.com>
0a89954 | docs: add M10 acceptance criteria (controller-verified) | Nolai <120611751+Nolai2010@users.noreply.github.com>
```

3/3 提交带 `Signed-off-by` ✅；主题长度实测 63 / 57 / 55，均 ≤72 ✅；每个提交只动其任务应动文件（判据入库 → translator → 示例 + CI），无跨任务裹挟 ✅。

### D3 REUSE 合规

```
$ python3 -m reuse lint
* Files with copyright information: 181 / 181
* Files with license information: 181 / 181
Congratulations! Your project is compliant with version 3.3 of the REUSE Specification :-)
exit=0
```

新 translator 带 SPDX 头（`plugins/compat/desktop-entry/translator.py:2` `# SPDX-License-Identifier: MIT`），其余新文件由 REUSE.toml `**` 通配覆盖，181/181 全合规 ✅。

判定：**PASS**（无夹带、DCO 齐备、REUSE 合规）

---

## M10-01 真 translator 存在：解析 `.desktop`、`status:"translated"`、真实产出 manifest + payload

**判据**：`plugins/compat/desktop-entry/translator.py` 解析 `.desktop`（[Desktop Entry]/Name/Exec/Type 等），成功时输出 `status: "translated"` 并**真实产出** manifest + payload 包装（非仅翻译计划）；沿用 M3 的 `--manifest/--payload` 接口契约。验证：CLI 实跑 + 产物存在性。

### 取证 1：CLI 实跑（产物落 /tmp/m10-acc/translated，自建目录）

```
$ rm -rf /tmp/m10-acc/translated
$ python3 plugins/compat/desktop-entry/translator.py --manifest plugins/optional/demo-desktop-app/plugin.json --out /tmp/m10-acc/translated
EXIT=0
stdout（节选）:
  "plugin": "demo-desktop-app",
  "source_format": "desktop-entry",
  "status": "translated",
  "kind": "descriptor-level",
  "steps": ["parse-desktop-entry", "normalize-name", "emit-manifest-v2", "emit-wrapper-payload"],
stderr: （空）

$ ls -la /tmp/m10-acc/translated/
-rw-r--r-- 1 JunYa 197609   607 Oct 24 17:34 demo-desktop-app.payload
-rw-r--r-- 1 JunYa 197609   399 Oct 24 17:34 plugin.json
```

**exit 0** ✅；**`status: "translated"`** ✅（区别于 M3 stub 的 `"stub-plan-only"`，见 M10-04 取证 5）；**manifest + payload 两文件真实落盘**（607 B / 399 B，非仅打印翻译计划）✅。

### 取证 2：产物内容实读（真实翻译，非占位）

`/tmp/m10-acc/translated/plugin.json`（manifest v2，399 B）：

```json
{
  "schema_version": "2",
  "name": "demo-desktop-app",
  "version": "0.1.0",
  "type": "compat-bridge",
  "uninstallable": true,
  "payload": "demo-desktop-app.payload",
  "container": { "desktop": "windowed" },
  "protocols": ["desktop-entry"],
  "translator": "plugins/compat/desktop-entry/translator.py",
  "capabilities": ["desktop.category.utility"]
}
```

`/tmp/m10-acc/translated/demo-desktop-app.payload`（包装 payload，607 B）：

```
# EtherOS M10 包装 payload —— 描述符级翻译产物,非二进制指令翻译产物
# generated by plugins/compat/desktop-entry/translator.py; this file is data: nothing parses or executes it
# Exec= is forwarded VERBATIM as a string: no instruction translation, no syscall mapping, no sandbox run (约束 47)
# source descriptor: I:\etheros\plugins\optional\demo-desktop-app\app.desktop
[EtherOS Wrapper]
Format=desktop-entry
Name=Demo Desktop App
Exec=/bin/echo M10 demo
Comment=M10 端到端示例:本文件是外部格式占位,Exec 只作字符串转发,不执行
Categories=Utility;
```

字段映射逐项对上（`Name=Demo Desktop App`→`demo-desktop-app`；`Type=Application`→`compat-bridge`；`Exec` 逐字转发；`Categories=Utility;`→`desktop.category.utility`）✅ —— 真实解析真实映射，非模板占位。

### 取证 3：M3 接口契约沿用

`translator.py:171-174`：`--manifest`（required）/ `--payload`（缺省取 manifest 的 payload 字段）/ `--out` / `--name`，与 `plugins/compat/stub-runtime/translator.py`（M3 stub）同形。缺 `--manifest` 时 argparse 报 `the following arguments are required: --manifest` 并 exit 2（与 M3 stub 同构）✅。

判定：**PASS**

---

## M10-02 产物过 v2 校验

**判据**：翻译产出的 manifest 能被 `tools/validate_plugins.py` 接受（schema v2），payload 文件真实存在。验证：`validate_plugins.py --file` 实跑 exit 0。

```
$ python3 tools/validate_plugins.py --file /tmp/m10-acc/translated/plugin.json
plugins validation: OK
EXIT=0
```

**exit 0 + "plugins validation: OK"** ✅；`payload: "demo-desktop-app.payload"` 指向的文件在同目录真实存在（M10-01 取证 1 的 `ls`，607 B）✅。

交叉验证：全树校验（含新入树的 `plugins/optional/demo-desktop-app/`）本地复跑亦 `plugins validation: OK`（exit 0）✅。

判定：**PASS**

---

## M10-03 端到端闭环：翻译产物被 load_plugins 纳入装载计划

**判据**：示例插件 `plugins/optional/demo-desktop-app/` 的 foreign payload 经翻译后，能被 `tools/load_plugins.py` 纳入装载计划（enabled 后）。验证：load_plugins 实跑 + 计划含该插件。

### 取证 1：构造临时 plugins 树 + config（仓库 config/default.toml 零改动）

```
$ mkdir -p /tmp/m10-acc/loadtree/optional/demo-desktop-app
$ cp /tmp/m10-acc/translated/plugin.json /tmp/m10-acc/translated/demo-desktop-app.payload /tmp/m10-acc/loadtree/optional/demo-desktop-app/
$ printf '[plugins]\nenabled = ["demo-desktop-app"]\n' > /tmp/m10-acc/loadtree.toml
```

（树上放的是 M10-01 中 translator **真实产出**的两个文件；`git status --porcelain` 在取证前后均为空，仓库 `config/default.toml` 未被触碰。）

### 取证 2：load_plugins 实跑 + 断言

```
$ python3 tools/load_plugins.py --plugins-root /tmp/m10-acc/loadtree --config /tmp/m10-acc/loadtree.toml
EXIT=0
（plan JSON 节选）
  "enabled": [{ "id": "demo-desktop-app", "type": "compat-bridge", "category": "optional",
                "payload": "demo-desktop-app.payload", "container": {"desktop": "windowed"},
                "capabilities": ["desktop.category.utility"] }],
  "load_order": ["demo-desktop-app"],
  "status": "plan-only"

$ python3 -c "<json.load 后断言>"
TRANSLATED ARTIFACT LOADABLE OK ['demo-desktop-app']
status: plan-only
```

**exit 0** ✅；**`load_order == ['demo-desktop-app']`**（计划含该插件）✅；status 仍为诚实的 `plan-only` ✅。

### 取证 3：仓库默认装载计划零变化（反证未借示例插件改默认行为）

```
$ python3 tools/load_plugins.py
EXIT=0
default load_order: ['files', 'mon', 'settings', 'shell', 'etheros-agent-rules', 'douyin', 'hello-plugin']
default skipped  : [{'id': 'demo-desktop-app', 'reason': 'optional plugin not listed in [plugins] enabled — config is the single source of enablement (Global Constraint 12)'}]
```

默认 `load_order` 与 M9 基线逐项相等（7 项一个位置都没动）；新示例插件按 config 未启用、正确进 `skipped` ✅ —— 端到端实证确实只发生在 /tmp 副本树，未污染仓库默认行为。

判定：**PASS**

---

## M10-04 诚实边界红线（本里程碑最高优先级，逐层独立复核）

**判据**：translator 输出与 README 明写"描述符级翻译，非二进制指令翻译"；`plugins/optional/douyin/` 与 stub-runtime 仍为 stub，未借本里程碑改口径。验证：文件实读 + douyin/stub 零改动证明。

### 取证 1：translator 无任何执行手段（全文检索）

```
$ grep -n -E "subprocess|os\.system|os\.popen|\bexec\(|\beval\(|popen|ctypes|\bsystem\(|spawn|Popen|__import__|\bcompile\(|marshal|pickle" plugins/compat/desktop-entry/translator.py
38:GROUP_RE = re.compile(r"^\[(.+)\]$")
39:ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
```

仅两处 `re.compile`（正则编译，非代码执行）✅；执行类 API（subprocess/os.system/exec/eval/popen/ctypes/system/spawn/Popen/__import__/marshal/pickle）**零命中** ✅。

### 取证 2：AST 级 import 白名单与危险调用核验

```
$ python3 -c "<ast.parse 后 walk>"
imports: ['argparse', 'json', 'pathlib', 're', 'sys']
non-stdlib: NONE
dangerous call names: ['compile']
$ python3 -c "<逐个 dump 危险名调用节点>"
Attribute -> Attribute(value=Name(id='re'), attr='compile') @line 38
Attribute -> Attribute(value=Name(id='re'), attr='compile') @line 39
```

imports 为 argparse/json/pathlib/re/sys **纯 stdlib** ✅；唯一命中危险名单的 `compile` 经 AST 节点级核实**均为 `re.compile`**（正则编译）✅。translator 无任何执行手段，红线第一层成立。

### 取证 3：包装 payload 为纯数据

```
$ python3 -c "<读 payload 字节>"
payload bytes: 607
（UTF-8 文本，10 行；含中文故非纯 ASCII，但无任何二进制内容）
exec line verbatim: ['Exec=/bin/echo M10 demo']
```

payload 为纯文本数据文件，`Exec=` 逐字字符串转发；文件头三行注释明示 "this file is data: nothing parses or executes it" / "no instruction translation, no syscall mapping, no sandbox run (约束 47)"；`translator.py:270-272` docstring 同口径 ✅。

### 取证 4：三层文案诚实性实读

- **模块 docstring**（translator.py:5-14）："这是**描述符级翻译**……它**不是二进制指令翻译**：不解析 exe/ipa/apk 等二进制容器；不做指令集解码、不做系统调用转换、不做沙箱内执行；`Exec=` 字段只作**字符串原样转发**……本工具从不执行它。"
- **README**（plugins/compat/desktop-entry/README.md:5-11「诚实边界（先读这一节）」）：五条逐条写明描述符级/非二进制指令翻译/Exec 只作转发/`status:"translated"` 不表示已装载更不表示已运行/douyin 与 stub-runtime 仍是 stub。
- **结果 JSON note**（实跑 stdout，translator.py:259-263）："descriptor-level translation……NOT binary instruction translation — no instruction decoding, no syscall translation, no in-sandbox execution; Exec= is forwarded verbatim as a string (约束 47). status 'translated' means the artifacts were really written — NOT loaded, NOT run. ipa/exe and plugins/optional/douyin/ remain stub (差异点 2)."

三层（docstring / README / result-note）口径一致且与红线裁定逐字吻合 ✅。

### 取证 5：夸大用语零命中 + stub 口径未变

```
$ grep -rn -E "支持运行|可以运行|能运行|运行 \.desktop|\.desktop 应用|可执行|真正执行|运行外部|运行任意" plugins/compat/desktop-entry plugins/optional/demo-desktop-app
GREP_EXIT=1（零命中）
```

"支持运行/可以运行"类夸大用语**零命中** ✅（progress.md:178 红线明令禁止）。

```
$ grep -n "stub-plan-only" plugins/compat/stub-runtime/translator.py
58:        "status": "stub-plan-only",
$ cat plugins/optional/douyin/plugin.json（节选）
  "protocols": ["ipa"],
  "translator": "plugins/compat/stub-runtime/translator.py",
```

stub-runtime 仍输出 `stub-plan-only`（:58）✅；douyin 仍 `protocols: ["ipa"]` + 指向 stub translator ✅。真实现成功时输出 `status:"translated"` + `kind:"descriptor-level"`（M10-01 取证 1 实跑），与 stub 的 `stub-plan-only` **形态分明、不可能混淆** ✅。

### 取证 6：douyin / stub-runtime / config 零改动（双基准）

```
$ git diff e238760..5b0e8b8 --name-status -- plugins/compat/stub-runtime plugins/optional/douyin
（空输出）
$ git diff v0.9.0-m9..5b0e8b8 --name-status -- plugins/compat/stub-runtime plugins/optional/douyin config/
（空输出）
```

相对 M9 合并点 `e238760` 与 tag `v0.9.0-m9` 双基准，douyin / stub-runtime / config/ **零改动** ✅ —— 未借本里程碑改口径。

判定：**PASS**（红线六层取证全部通过）

---

## M10-05 负例：缺失关键字段 / 非法格式 / 空文件

**判据**：缺失关键字段（无 Exec）、非法格式（非 .desktop 文本）、空文件 → 各自非 0 退出并给出原因。验证：三条负例实跑。

夹具全部自建于 `/tmp/m10-acc/neg/`（源声明 JSON + 对应 payload），输出目录每次预删后断言不存在：

```
=== 负例①：无 Exec（noexec.desktop：有 Name+Type=Application+Categories，无 Exec） ===
$ python3 plugins/compat/desktop-entry/translator.py --manifest .../src-noexec.json --out /tmp/m10-acc/neg-out
translator: desktop entry has no Exec= (or it is empty) — nothing to forward into the wrapper payload
EXIT=2
output dir exists: NO

=== 负例②：非法格式（badfmt.desktop：首行 { 的 JSON 文本） ===
$ python3 plugins/compat/desktop-entry/translator.py --manifest .../src-badfmt.json --out /tmp/m10-acc/neg-out
translator: payload is not a freedesktop desktop entry: no [Desktop Entry] section (looks like JSON, not a desktop entry)
EXIT=2
output dir exists: NO

=== 负例③：空文件（empty.desktop：0 字节） ===
$ python3 plugins/compat/desktop-entry/translator.py --manifest .../src-empty.json --out /tmp/m10-acc/neg-out
translator: payload 'empty.desktop' is empty (0 bytes / blank) — nothing to translate
EXIT=2
output dir exists: NO
```

三条必选负例各自 **exit=2（非 0）** ✅、**stderr 给出与形态一一对应的原因** ✅、**不产出任何输出目录** ✅；全部走统一 `refuse()` 路径（translator.py:45-48），无 traceback、无 crash 形态。

### 加跑（鼓励级）：Type=Link 与 id 撞名 douyin

```
=== 负例④：Type=Link（link.desktop：Type=Link + URL） ===
translator: desktop entry Type='Link' is not supported — only Type=Application maps to a compat-bridge plugin (Type=Link/Directory have no Exec payload to bridge)
EXIT=2    output dir exists: NO

=== 负例⑤：id 撞名（collide.desktop：Name=Douyin → 归一化 'douyin' 与 plugins/optional/douyin 撞名） ===
translator: normalized plugin id 'douyin' (from Name='Douyin') collides with an existing plugin id in plugins/{builtin,optional,dev} — refuse to overwrite another plugin (差异点 4)
EXIT=2    output dir exists: NO
```

两条加跑负例同样非 0 退出 + 明因 + 不产出 ✅（撞名拒绝证明 `tree_plugin_ids()` 对**真实仓库树**生效，红线"绝不覆盖另一个插件"为真）。

判定：**PASS**

---

## M10-06 旧门禁零回退

**判据**：十 job 名与行为不变，release.yml 零 diff，stub-runtime 与 douyin 零改动。验证：CI 十 job 全绿 + diff 复核。

### 取证 1：本里程碑 CI run 核验（headSha 逐字核对，防陈旧 run 坑）

```
$ gh run view 39055860799 --repo Nolai2010/EtherOS --json headSha,conclusion,status,event,jobs
headSha   : 5b0e8b8defea08d97fd714330f65e006bae59c4a   ← 与分支 HEAD 逐字相等
conclusion: success | status: completed | event: push | createdAt: 2026-10-17T17:55:33Z
job count: 10
  success   spec & docs reference consistency (anti context-drift)
  success   dco (Signed-off-by on every commit, merges exempt)
  success   etherkit single-source consistency
  success   build ToaruOS aarch64 base (upstream builder image)
  success   lint (EtherOS-owned code only; base/ structurally excluded)
  success   license (reuse lint, submodules excluded per spec 5 / risk 2)
  success   plugin manifest schema & config consistency (M2)
  success   build ToaruOS base (upstream builder image)
  success   vm smoke aarch64 (QEMU headless boot evidence)
  success   vm smoke (QEMU headless boot evidence)
```

**headSha 与被验对象 `5b0e8b8` 逐字相等** ✅；**十 job 全 success** ✅；push 事件 ✅。

### 取证 2：plugin-schema job 日志实读（新增 M10 step 与旧步骤全链实证）

job `117463571549` 日志关键行（`gh run view 39055860799 --log --job 117463571549`，共 257 行）：

```
L112: plugins validation: OK                                          ← 旧步骤① 全树 v2 校验
L161: LOAD PLAN OK 7                                                   ← 旧步骤③ M7 装载计划
L198: TOPO OK ['beta', 'alpha', 'gamma']                               ← 旧步骤④ M9 拓扑 smoke
L147: "status": "stub-plan-only"（route ipa→douyin）                   ← 旧步骤② M3 路由 smoke，stub 口径未变
L236: TRANSLATE OK /tmp/m10-translate/plugin.json                      ← 新增 M10 step：真翻译成功
L237: plugins validation: OK                                           ← 翻译产物过 v2 校验
L238: translator: desktop entry has no Exec= (or it is empty) — ...     ← 负例① 拒绝原文
L239: translator: payload is not a freedesktop desktop entry: no [Desktop Entry] section (looks like JSON, not a desktop entry)   ← 负例② 拒绝原文
L240: translator: payload 'empty.desktop' is empty (0 bytes / blank) — nothing to translate   ← 负例③ 拒绝原文
L241: TRANSLATED ARTIFACT LOADABLE OK ['demo-desktop-app']             ← 端到端闭环断言
```

**`TRANSLATE OK` → `plugins validation: OK` → `TRANSLATED ARTIFACT LOADABLE OK ['demo-desktop-app']`** 全链真实跑通 ✅；三条负例拒绝原文在 CI 日志内可见（`!` 反向断言，非空转）✅；**旧四步（全树校验 / 路由 smoke / 装载计划 / 拓扑 smoke）在本 run 内全部重新执行并通过**，其中路由 smoke 的 douyin 结果仍为 `stub-plan-only`（M10-04 红线在 CI 侧再次实证）✅。

### 取证 3：job 名集合与 M9 基线 run 对象级比对

```
$ gh run view 39054150814 --repo Nolai2010/EtherOS --json headSha,conclusion,jobs   # M9 合并进 main 的 run
headSha: e238760633e946e7f2b9864eb0022edac0cbe3bd | conclusion: success | job count: 10
M9  job count: 10 | M10 job count: 10
set equal: True
added  vs M9: NONE
removed vs M9: NONE
M9  conclusions: ['success']
M10 conclusions: ['success']
```

两次 run 的 **job 名集合逐一相等**（10=10，无增、无删、无改名）✅；两次均十 job 全 success ✅。

### 取证 4：ci.yml diff 形态（difflib opcode 级 + pyyaml job 级对象比对）

```
$ python3 -c "<difflib SequenceMatcher 两版 ci.yml>"
opcodes non-equal: [('insert', 113, 113, 113, 154)]
added_lines: 41 removed_lines: 0 pure_insertion: True

$ python3 -c "<pyyaml 两版 job 对象比对>"
job count base/m10: 10 10
removed jobs: NONE
added jobs  : NONE
job objects changed: ['plugin-schema']
non-jobs top-level changed: NONE
--- CHANGED detail: plugin-schema
  steps base/m10: 5 6
  step names base: [None, 'Validate plugin manifests against schema v2', 'Protocol routing smoke (M3 route_plugins)', 'Load plan smoke (M7 load_plugins)', 'Dependency topology smoke (M9 load_plugins dependencies)']
  step names m10 : [None, 'Validate plugin manifests against schema v2', 'Protocol routing smoke (M3 route_plugins)', 'Load plan smoke (M7 load_plugins)', 'Dependency topology smoke (M9 load_plugins dependencies)', 'Desktop-entry translation smoke (M10 real translator)']
```

ci.yml 相对 `v0.9.0-m9` 为**单一 insert opcode、+41/-0 纯追加**（difflib opcode 级，无任何 delete/replace）✅；pyyaml job 级比对：**10 job 无增删改名，顶层非 jobs 键零变化，唯一发生变化的 job 是 `plugin-schema`——旧 5 个 step 原样保留，仅在末尾追加第 6 个 step** `Desktop-entry translation smoke (M10 real translator)` ✅。该 step 内容（取证 2 已实读）为纯增强：真实翻译 + `test -f` 双断言 + v2 校验 + 三条负例 `!` 反向断言 + 装载计划闭环断言，**无任何断言放宽、无 `continue-on-error`、无 suppress** ✅。

### 取证 5：release.yml / config / stub-runtime / douyin 零 diff

```
$ git diff v0.9.0-m9..5b0e8b8 -- .github/workflows/release.yml | wc -c
0
$ git diff v0.9.0-m9..5b0e8b8 -- config/ | wc -c
0
$ git diff v0.9.0-m9..5b0e8b8 --name-status -- plugins/compat/stub-runtime plugins/optional/douyin
（空输出）
```

release.yml **0 字节** ✅；config/（含 default.toml）**0 字节** ✅；stub-runtime / douyin **零改动** ✅。

判定：**PASS**（零回退成立；`plugin-schema` job "追加一个 step" 的特殊口径按 M9-05 验收先例记档，见 §口径差异与遗留 项 1）

---

## 其它零改动核验

```
$ git diff v0.9.0-m9..5b0e8b8 --name-only
.github/workflows/ci.yml
docs/development/acceptance-standard.md
plugins/compat/desktop-entry/README.md
plugins/compat/desktop-entry/translator.py
plugins/optional/demo-desktop-app/README.md
plugins/optional/demo-desktop-app/app.desktop
plugins/optional/demo-desktop-app/plugin.json
```

全区间仅上述 7 个文件（+462/-0，见 D1）；`plugins/schema/`、`tools/`（validate/load 消费方）、`kernel/`、`REUSE.toml`、`base/toaruos` submodule、其余全部插件 manifest **零命中** ✅。tools/validate_plugins.py 与 tools/load_plugins.py 未被改动——端到端闭环是**既有工具对新产物的自然接纳**，非为通过验收而放松工具 ✅。

判定：**PASS**

---

## 已知 Minor 与 known-deferred notes 逐条独立核实（记档，不判 FAIL）

以下均为任务书预决"归 M10-6 关门处理"或已披露设计边界，本验收独立复核属实后记档：

1. **lint 的 pyflakes 目标未含新 translator（CI 覆盖缺口）** —— 独立复核属实：ci.yml:230 实证为 `python3 -m pyflakes tools/*.py plugins/compat/stub-runtime/*.py`，未含 `plugins/compat/desktop-entry/`。本地补测新 translator：`python3 -m pyflakes plugins/compat/desktop-entry/translator.py` → **exit 0，零告警**，故当前无潜在缺陷漏网，属覆盖缺口。**归 M10-6 关门**（方向只许更严：扩为 `plugins/compat/*/*.py`）。
2. **spec-consistency 里程碑白名单停在 M9（守卫缺口）** —— 独立复核属实：ci.yml:277 实证白名单元组为 `("M0"…"M9")`；M10 章节已入库（acceptance-standard.md:130）但不在守卫范围（若 M10 章节被删，CI 不会红）。与 M8-6/M9-6 先例同形态。**归 M10-6 关门**（扩至含 "M10"）。
3. **`--manifest` 必需、裸 .desktop 无法直通（M3 契约既定边界）** —— 独立复核属实：缺 `--manifest` 时 argparse 报 `the following arguments are required: --manifest`、exit 2。这是 M3 `--manifest/--payload` 契约的既定边界而非缺陷；若未来要直通需接口扩展（如 payload-only 模式）。**记档于 M10-6 关门文档**。
4. **重复 `Key=` 首次获胜（translator.py:109 `fields.setdefault`）** —— 探针实证：同一 `Exec=` 两行（`/bin/echo first` / `/bin/echo second`）→ 产物取 `Exec=/bin/echo first`（exit 0）。freedesktop 规范下重复键属非法输入，取首次值影响极小；README 未记档此细节。**建议后续补一行文档**（非 FAIL）。
5. **归一化截断前导数字（`3D Viewer` → `d-viewer`）** —— 已 README 明示（README.md:33-43 归一化五步规则含此例），属 schema `^[a-z]` 首字符约束的必然结果，拒绝伪装成"保留原义"。已披露的设计取舍，非 FAIL。
6. **v0.10.0-m10 tag 尚未打** —— `git tag -l v0.10.0-m10` 无结果，属 M10-6 关门动作（merge --no-ff + tag），不在本次验收范围，不判 FAIL。

---

## 口径差异与遗留

1. **M10-06「十 job 行为不变」的严格读法差异（与 M9-05 先例同口径）** —— `plugin-schema` job 是十者中唯一非对象全等的：新增一个 M10 翻译 smoke step（steps 5→6，旧 5 step 逐字保留）。严格字面读，其"行为"确有变化（多跑一个 step）；但方向为**纯增强**（无断言放宽、无 `continue-on-error`、无 suppress，step 内容正是 M10-01/02/03/05 判据所要求的 CI 覆盖），按"方向只许更严"的既有惯例判为零回退、记档而非抹平。其余 9 个 job 对象全等。**本条按任务书预决口径执行，判 PASS-with-note 记档。**
2. **端到端实证不改仓库 config/default.toml** —— M10-03 的"enabled 后纳入装载计划"用 /tmp 副本 plugins 树 + /tmp config 实现（取证见 M10-03），仓库 `config/default.toml` 实测零 diff；默认装载计划 7 项与 M9 基线逐项相等、示例插件正确落 `skipped`。实现期"临时启用后还原"的自述由此得到独立佐证。
3. **本报告未登记进 `docs/index.md`** —— 验收者铁律限制改动仓库文件（唯一例外即本报告本身）。沿用 M5~M9 报告先例，由 M10-6 关门任务补登。
4. **本机 git 到 github.com 的 HTTPS 通道状态** —— 本次远端取证全部走 `gh`（GET，`--repo Nolai2010/EtherOS`），未发起写操作；报告的推送见文末提交与 CI 复核段（若遇代理 502 按任务书重试纪律处理并如实记录）。
5. **临时目录** —— 全部夹具与产物落 `/tmp/m10-acc/**`（translated / loadtree / neg / dup-out 等），未落进仓库；`git status --porcelain` 在验收前后均为空。未触碰 /tmp 下实现者遗留的 m10-bin / m10-loadtree / m10-neg / m10-translate / m10-ttree 目录。
6. **M10-04 红线与 M10-05 负例的相互印证** —— 撞名负例（Name=Douyin）证明 translator 的 id 冲突门读的是真实仓库树；CI 路由 smoke 中 douyin 仍 `stub-plan-only`（M10-06 取证 2）证明新增真 translator 没有改变任何既有插件的路由/翻译口径。红线"首个真翻译"与"其余仍是 stub"两端均为实证，非文档声称。

---

**总判定：M10-01 ~ M10-06 六条全部 PASS（M10-06 按 M9-05 先例口径记档"plugin-schema 追加一个 step、方向纯增强"），阻塞缺陷 0；6 条已知 Minor / known-deferred notes 均为记档项（控制器已预决归 M10-6 关门或属既有设计边界），6 条口径差异已如实记档 —— 其中"plugin-schema job 纯增强记档"与"诚实边界红线三层取证全过"是最需要终审知悉的两点。**

**STATUS: PASS**

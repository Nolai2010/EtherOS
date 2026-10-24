# M11 独立验收报告 —— 装载闭环（plan → load 物化 → 路由消费）

- **验收者**：general-purpose-1（独立上下文；Builder≠Reviewer≠Acceptance——本验收者与 M11 实现者、M11-6 审查者均相互独立，不替实现背书，不粉饰，不采信任何自评输出；审查报告 `task-m11-6-review.md` 与实现者两波报告仅作线索来源，每条判定均有本方独立取证命令与输出）
- **被验对象**：分支 `feat/m11-load-closure`，HEAD `2a10245256eb9923bc1841e69af3c5ef85b12fc9`（`2a10245 ci: load-state smoke`）
- **区间**：`f312bf0..HEAD`（= tag `v0.10.0-m10` 所指提交），共 **5 个非合并提交**（`5ea80d7` → `6d52c7b` → `50b02b2` → `8e0e2b7` → `2a10245`）
- **仓库**：`I:/etheros`（远端 `github.com/Nolai2010/EtherOS`；远端分支头实测 == 本地 HEAD，逐字相等）
- **执行日期**：2026-10-24
- **依据**：`docs/development/acceptance-standard.md` §`## M11 · 装载闭环（plan → load 物化 → 路由消费）`（:161-170，M11-01~M11-06，实测与计划提案 6/6 逐字一致，见 M11-01 取证 4）+ 计划 `docs/superpowers/plans/2026-10-24-etheros-m11-load-closure-draft.md`（APPROVED-BY-CONTROLLER）
- **口径**：偏严。全部判据**自己实跑取证**；CI 取证走 `gh` GET（headSha 必须逐字等于分支 HEAD，防"陈旧 run"坑）；零回退用 difflib opcode + pyyaml job 级对象比对 + 六调用新旧两树逐字节回归，不做肉眼 diff；夹具与产物全程只落 `/tmp/m11-acc/**`；基线 worktree `/tmp/m11-acc-base @ f312bf0` 用后已 `git worktree remove`；**未修改仓库任何文件**（唯一写操作为本报告入库），验收前后 `git status --porcelain` 均为空
- **写操作范围**：**仅新建本报告一个文件**；未改 ci.yml / 契约 / tools / schema / config / release.yml / 插件树，未推 tag、未动 main、未派子代理
- **环境**：Git Bash + 系统 python3（3.13.14）；clang-format NPM 1.8.0（LLVM 15.0.0）；`gh` GET 可用。注意：本机 Python 内联 `/tmp` 路径不经 MSYS 转换（实现者 CONCERNS 5 同款注意点，本次以 argv 传路径 / `tempfile.gettempdir()` 规避，非产品问题）

---

## 0. 判据存在性核验与被验对象定位

```
$ git rev-parse HEAD && git branch --show-current
2a10245256eb9923bc1841e69af3c5ef85b12fc9
feat/m11-load-closure

$ git status --porcelain
（空输出——工作区干净）

$ git log --oneline -6
2a10245 ci: load-state smoke (M11 real load + route consumption)
8e0e2b7 feat(tools): route_plugins consumes load-state (M11-04)
50b02b2 feat(tools): host-side load_state (M11 real load primitive)
6d52c7b docs(contract): load-state contract (M11 loader load semantics)
5ea80d7 docs: add M11 acceptance criteria (controller-verified)
f312bf0 Merge feat/m10-translator: M10 translator real implementation (descriptor-level .desktop end-to-end)

$ git ls-remote origin refs/heads/feat/m11-load-closure
2a10245256eb9923bc1841e69af3c5ef85b12fc9  refs/heads/feat/m11-load-closure
```

HEAD 与任务书所述 `2a10245` 一致 ✅；分支正确 ✅；远程与本地同 SHA ✅；工作树干净 ✅。
判据实存：`docs/development/acceptance-standard.md:161-170` M11 章节表六条编号/标准/验证方式齐备 ✅。

判定：**PASS**（判据齐备、被验对象定位准确、无越界动作）

---

## 夹带与 DCO 总检（先行）

### D1 全量文件清单（`v0.10.0-m10..HEAD`，恰 7 文件）

```
$ git diff v0.10.0-m10..HEAD --name-status
M .github/workflows/ci.yml
M docs/development/acceptance-standard.md
M kernel/interfaces/loader-contract.md
M kernel/interfaces/loader_if.h
M kernel/interfaces/plugin-routing.md
A tools/load_state.py
M tools/route_plugins.py

$ git diff v0.10.0-m10..HEAD --numstat
79  0  .github/workflows/ci.yml          （纯追加）
11  0  docs/development/acceptance-standard.md（追加 M11 章节）
33  0  kernel/interfaces/loader-contract.md（纯追加,§7/§8）
74  3  kernel/interfaces/loader_if.h     （3 行为宏对齐空白,见 M11-06 取证 5）
11  0  kernel/interfaces/plugin-routing.md（追加 §5）
190 0  tools/load_state.py               （新建）
51  3  tools/route_plugins.py            （附加模式 + 分派）
```

**恰 7 个文件**，与计划 File Structure 的 M11-01..05 范围逐项一致，无计划外夹带 ✅。
未触碰清单逐项核验（`git diff v0.10.0-m10..HEAD -- <path>` 输出 **0 字节**）：`tools/load_plugins.py`、`tools/validate_plugins.py`、`plugins/schema/`、`config/`、`.github/workflows/release.yml`、`plugins/`（整树）、`base/`、`kernel/interfaces/README.md` ✅。

### D2 逐提交范围（5 个提交，均带 Signed-off-by）

```
$ git log v0.10.0-m10..HEAD --no-merges --format='%h | %s | sob=%(trailers:key=Signed-off-by,valueonly)'
2a10245 | ci: load-state smoke (M11 real load + route consumption)      | Nolai <120611751+Nolai2010@users.noreply.github.com>
8e0e2b7 | feat(tools): route_plugins consumes load-state (M11-04)       | Nolai <120611751+Nolai2010@users.noreply.github.com>
50b02b2 | feat(tools): host-side load_state (M11 real load primitive)   | Nolai <120611751+Nolai2010@users.noreply.github.com>
6d52c7b | docs(contract): load-state contract (M11 loader load semantics)| Nolai <120611751+Nolai2010@users.noreply.github.com>
5ea80d7 | docs: add M11 acceptance criteria (controller-verified)       | Nolai <120611751+Nolai2010@users.noreply.github.com>
```

5/5 提交带 `Signed-off-by` ✅；每提交只动其任务应动文件，无跨任务裹挟 ✅。

### D3 REUSE 合规与卫生

```
$ python3 -m reuse lint
* Files with copyright information: 183 / 183
* Files with license information: 183 / 183
Congratulations! Your project is compliant with version 3.3 of the REUSE Specification :-)
exit=0

$ python3 -m pyflakes tools/*.py
（无输出）exit=0
```

新文件 `tools/load_state.py` 带 SPDX MIT 头（:2），其余由 REUSE.toml `**` 通配覆盖，183/183 全合规 ✅；pyflakes 干净 ✅；七文件入库对象 CR 字节数全为 **0**（`git show HEAD:<f> | tr -dc '\r' | wc -c` 逐一实证）✅。

判定：**PASS**（无夹带、DCO 齐备、REUSE 合规）

---

## M11-01 装载契约扩展在位：契约 / 头文件 / 路由文档三处 + 键名集合比对

**判据**：loader-contract.md 定义 load 语义与装载状态 JSON 键名（status "loaded" 及诚实边界明文）；loader_if.h 对应结构与原语声明；plugin-routing.md 同步 route ← load-state 消费语义。验证：文件实读 + 键名集合比对。

### 取证 1：loader-contract.md §7/§8 实读（M11-01 核心）

`kernel/interfaces/loader-contract.md` 新增 §7「装载状态 JSON 契约(M11;键名即契约)」（:79-97）：顶层**九键表**（`status` 固定 `"loaded"` 且明文"宿主侧物化完成;**非**已启动/已运行" / `contract` / `stage` 取 `"M11-loader-load"` / `plan_contract` / `registry`（顺序即装载顺序,与 plan `load_order` 逐项相等）/ `load_order` / `routes`（协议 token → `{plugin, manifest, translator, payload}`;仅已装载 compat-bridge 激活;同 token 双声明即拒,约束 55）/ `skipped`（原样承袭）/ `notes`）；`registry[]` **十键**（六键承袭 plan + `protocols`/`translator`/`manifest`/`isolation` 固定 `"PER_PLUGIN"` 派生声明非强制）。§7 尾段诚实边界明文：**"`loaded` 只表示宿主侧注册表已物化 + 路由已激活,不表示已启动、更不表示已运行(约束 29 延续)"**（:97）。§8「装载状态拒绝语义(M11)」八项（:99-110）：非 JSON 对象 / status 非 plan-only / contract 非本契约 / id 树中不存在(ENOENT) / payload 引用不符 / payload 悬空 / load_order 与条目 id 集不一致 / 协议 token 激活冲突(EAMBIGUOUS)，逐条原因 + 非 0 退出 + 不输出状态 JSON。
§2 计划契约**零删除行**（diff 对该文件 +33/-0，纯追加）——M7 计划契约逐字保留 ✅。

### 取证 2：loader_if.h 对应结构与原语声明实读

`kernel/interfaces/loader_if.h` 新增（:103-196）：`etheros_protocol_token` / `etheros_translator_ref` typedef；`etheros_load_state_entry` **十字段**（id/type/category/payload/container/capabilities/protocols/translator/manifest/isolation，manifest 注释 "in-tree manifest path (repo-root relative)"，isolation 注释 "planned boundary; not enforced here"）；`etheros_load_route` **五字段**（token/plugin/manifest/translator/payload）；`etheros_load_state`（registry/registry_count/routes/route_count/skipped/skipped_count/stage）；结果码 `#define ETHEROS_EAMBIGUOUS (-3)`；原语声明 `int etheros_load_apply(const etheros_load_plan *plan, const etheros_load_request *request, etheros_load_state *out_state);`，注释含 "apply a plan-only plan, materialize host-side state; binds nothing into the kernel, starts nothing" 与漂移/EAMBIGUOUS 拒绝口径。`plan_load` 及既有全部声明逐字保留（见 M11-06 取证 5 的行守恒证明）✅。

### 取证 3：plugin-routing.md §5 实读

`kernel/interfaces/plugin-routing.md` 新增 §5「route ← load-state 消费语义（M11）」（:67-76）：两种消费途径（缺省直接扫 config / `--load-state` 消费激活路由表）、**语义等价性**（同源于 manifest 已声明 protocols，装载途径把扫树+启用判定提前到装载期）、歧义两途径一致（多命中即拒，装载途径将 EAMBIGUOUS 提前）、边界（"只供 route 查询;装载状态表示「宿主侧已登记 + 路由已激活」,不表示已启动、更不表示已运行;内核侧装载与镜像内启动期装载属后续里程碑(约束 29)"）✅。

### 取证 4：键名集合三方机械比对 + 入库六行逐字比对

契约 §7 表 / loader_if.h 结构 / **实跑产物**（`load_plugins.py > plan.json` → `load_state.py --plan plan.json --out state.json`，rc=0）三方比对（Python 脚本提取，非肉眼）：

```
contract §7 top-level keys (9) : ['status','contract','stage','plan_contract','registry','load_order','routes','skipped','notes']
actual state top-level keys (9): ['status','contract','stage','plan_contract','registry','load_order','routes','skipped','notes']
  set equal: True | order preserved: True
contract §7 registry[] keys (10) : ['id','type','category','payload','container','capabilities','protocols','translator','manifest','isolation']
loader_if.h entry fields (10)     : ['id','type','category','payload','container','capabilities','protocols','translator','manifest','isolation']
actual registry[0] keys (10)      : 同上
  contract == loader_if == actual: True（三方逐一相等）
contract §7 routes value keys : ['plugin','manifest','translator','payload']
actual routes['ipa'] keys     : ['plugin','manifest','translator','payload']  equal: True
loader_if.h etheros_load_route fields (5) : ['token','plugin','manifest','translator','payload'] == ['token']+routes value keys: True
```

M11-01 入库六行与计划 Task M11-1 Step 2 提案**机械逐字比对 6/6 相同**；章节位置在 M10 章节与 M1 归档块之后（append 语义，不回改旧章节）✅。

判定：**PASS**

---

## M11-02 真装载器存在：端到端正例 25/25 断言全过

**判据**：tools/load_state.py 消费 tools/load_plugins.py 的 plan（按 id 回读 manifest 补协议/translator 字段），成功输出 `status: "loaded"` 并真实物化 registry（顺序与 plan load_order 逐项相等）+ routes 激活表 + isolation 派生声明。验证：CLI 实跑 + 产物键名/顺序断言。

### 取证：正例管道实跑 + 全断言（产物落 /tmp/m11-acc/）

```
$ python3 tools/load_plugins.py > /tmp/m11-acc/plan.json          # rc=0, status "plan-only"
$ python3 tools/load_state.py --plan … --out /tmp/m11-acc/state.json  # rc=0, stdout/stderr 均空
```

断言结果 **25/25 PASS**：

| # | 断言 | 结果 |
|---|---|---|
| 1 | `status == "loaded"` | PASS |
| 2 | `stage == "M11-loader-load"` | PASS |
| 3 | `contract == "kernel/interfaces/loader-contract.md"` | PASS |
| 4 | `plan_contract == contract == plan.contract`（契约同源） | PASS |
| 5 | plan.status 仍为 `"plan-only"`（消费不改写计划） | PASS |
| 6 | registry id 序列 == plan `load_order` | PASS |
| 7 | registry id 序列 == 预期七项 `[files, mon, settings, shell, etheros-agent-rules, douyin, hello-plugin]` | PASS |
| 8 | `state.load_order == registry ids` | PASS |
| 9 | `routes` 键集合**恰为** `{"ipa"}` | PASS |
| 10 | `"desktop-entry"` 不在 routes（demo-desktop-app 未启用） | PASS |
| 11 | `routes["ipa"]` 四键 `{plugin, manifest, translator, payload}` | PASS |
| 12-15 | `routes["ipa"]` == `{douyin, plugins/optional/douyin/plugin.json, plugins/compat/stub-runtime/translator.py, plugins/optional/douyin/payload/douyin.ipa}` | PASS |
| 16 | registry 每项十键齐备 | PASS |
| 17 | isolation 全 `"PER_PLUGIN"`（派生声明） | PASS |
| 18 | douyin：type compat-bridge、protocols `["ipa"]`、translator 指向 stub-runtime | PASS |
| 19 | native 条目 `protocols==[]` 且 `translator==null` | PASS |
| 20-21 | manifest / payload 均为仓库根相对 POSIX（无反斜杠、非绝对路径） | PASS |
| 22 | `skipped` 逐项等于 plan `skipped`（含 demo-desktop-app 及原因原文） | PASS |
| 23 | 顶层九键顺序与契约一致 | PASS |
| 24 | 不带 `--out` 的 stdout 产物与 `--out` 落盘**逐字节相同** | PASS |

**回读 manifest 补字段实证**：plan 条目（M7 契约六键）无 `protocols`/`translator`，装载器按 id 回读树内 manifest 补入（douyin 得 `["ipa"]` + stub translator；native 得 `[]` + `null`），payload 引用与 manifest 逐一相符（不符即拒，见 M11-05）——"消费方对计划权威的尊重"为实证，非文档声称 ✅。

判定：**PASS**

---

## M11-03 装载产物被真实消费：route ← load-state 端到端

**判据**：route_plugins.py --load-state 从装载状态解析协议路由（如 ipa → douyin 链，exit 0）；未启用插件的协议不被激活（demo-desktop-app 的 desktop-entry 不在激活表）。验证：实跑 + 激活表内容断言。

### 取证 1：装载状态途径命中（exit 0）

```
$ python3 tools/route_plugins.py --load-state /tmp/m11-acc/state.json --protocol ipa
rc=0
{ "query": {"protocol": "ipa"},
  "route": {"plugin": "douyin", "manifest": "plugins/optional/douyin/plugin.json",
            "translator": "plugins/compat/stub-runtime/translator.py",
            "payload": "plugins/optional/douyin/payload/douyin.ipa"},
  "next": ["translator", "load"], "status": "routed" }
```

与缺省模式 `--protocol ipa` 的 route 四键**逐项相等**（Python 断言 `a['route']==b['route']` True）；顶层键集合同为 `[query, route, next, status]`；query/next/status 亦相等 ✅。**装载产物被真实消费**（非自说自话）✅。

### 取证 2：未激活协议与激活表内容断言

```
$ python3 tools/route_plugins.py --load-state state.json --protocol desktop-entry
rc=1  FAIL: protocol 'desktop-entry' is not activated by the load state — 未被装载状态激活:该协议无已装载插件声明,或声明者未启用 (route: ENOENT via load state)

$ python3 tools/route_plugins.py --protocol desktop-entry   （缺省模式对照）
rc=1  FAIL: protocol 'desktop-entry' no enabled plugin declares it (route: ENOENT)
```

- 激活表收录插件实测 `['douyin']`——**demo-desktop-app 不在激活表** ✅；
- 非 0 退出 ✅；原因含「装载状态」字样，与缺省模式"树中无 enabled 插件声明"**可区分** ✅（约束 53）。

判定：**PASS**

---

## M11-04 诚实边界：loaded 三处同口径 + 格式无关 + plan 权威 + 缺省输出回归

**判据**：load-state 输出与契约/README 明写"loaded = 宿主侧已登记 + 路由已激活，非已启动/非已运行；内核侧装载与镜像内启动期装载属后续"；load_plugins.py 默认输出仍为 plan-only 逐字不变。验证：文件实读 + 默认输出回归比对。

### 取证 1：loaded 边界三处同口径 grep

| 处 | 位置 | 原文（节选） |
|---|---|---|
| 工具输出 notes | `load_state.py:174` | "loaded = 宿主侧已登记 + 路由已激活,非已启动/非已运行;内核侧装载与镜像内启动期装载属后续里程碑(约束 29)。" |
| 工具 docstring | `load_state.py:8-9` | "loaded 只表示宿主侧注册表已物化 + 路由已激活,不表示已启动/更不表示已运行;内核侧装载与镜像内启动期装载属后续里程碑(约束 29)。" |
| 契约 | `loader-contract.md:97` | "`loaded` 只表示宿主侧注册表已物化 + 路由已激活,**不表示已启动、更不表示已运行**(约束 29 延续)。" |
| 路由契约边界 | `plugin-routing.md:76` | "装载状态表示「宿主侧已登记 + 路由已激活」,**不表示已启动、更不表示已运行**;内核侧装载与镜像内启动期装载属后续里程碑(约束 29)。" |

四同口径 ✅（README/RELEASE_NOTES 的 loaded 表述属 M11-8 关门范围，本区间外，按计划不判 FAIL）。
**夸大用语核查**：`已启动`/`已运行` 在全部新增/修改文件中仅出现在否定语境（"不得出现" / "非" / "不表示"，逐行核查 6 处命中全为否定式）✅。

### 取证 2：isolation 计划级非强制三处明示

`load_state.py:175`（notes："isolation 为计划级声明(PER_PLUGIN,loader_if.h 既有 enum),非强制;隔离强制属后续安全模型里程碑(约束 52)"）+ `loader-contract.md:95`（registry[] 行："固定 `"PER_PLUGIN"`,派生声明,非强制"）+ `loader_if.h:130`（"planned boundary; not enforced here"）✅。

### 取证 3：格式无关铁律（约束 54）

```
$ grep -nE '\.(ipa|exe|apk|desktop)\b|douyin|desktop-entry' kernel/interfaces/loader-contract.md kernel/interfaces/loader_if.h kernel/interfaces/plugin-routing.md tools/load_state.py tools/route_plugins.py
grep_exit=1（零命中）
$ python3 tools/check_kernel_boundary.py
kernel boundary: OK   rc=0
```

契约三件 + 两个工具**零格式扩展名字面量**；内核边界守卫复跑 OK ✅。

### 取证 4：load_state.py 纯 stdlib、不重读 config（约束 50）

AST 提取 imports = `{argparse, json, pathlib, sys}`——**纯 stdlib** ✅；**无 tomllib**、无任何 config 读取代码（唯一 "config" 字样在 docstring 的"不重读 config"声明句）✅。
**行为实证**：构造仅含 hello-plugin 的裁剪 plan（enabled/load_order 裁剪）对**真实树**跑 load_state → registry == `["hello-plugin"]`、routes == `{}`——尽管 `config/default.toml` 启用着 douyin。**启用集权威是 plan，实证成立** ✅。

### 取证 5：load_plugins.py 默认输出 plan-only 逐字不变

与基线 worktree（`f312bf0`）逐字节回归（详见 M11-06 取证 2）：无参与 `--config config/default.toml` 两种调用 stdout/stderr/rc **全部 IDENTICAL**；默认输出 `status: "plan-only"`、`load_order` 七项一个位置都没动 ✅（该文件在本区间 0 字节 diff，双证）。

判定：**PASS**

---

## M11-05 负例：plan/tree 漂移四形态 + EAMBIGUOUS，逐条实跑

**判据**：plan/tree 漂移（id 不存在 / payload 引用不符 / load_order 不一致 / status 非 plan-only）→ 各自非 0 退出并给出原因；两个已装载插件声明同一协议 token → 装载期 EAMBIGUOUS 拒绝。验证：逐条实跑。

全部实跑（夹具落 /tmp/m11-acc/neg/**），各自 **rc=1**、stderr 逐条明因、stdout 无状态 JSON：

| # | 形态 | rc | stderr 摘要（实测） |
|---|---|---|---|
| 1a | **id 树中不存在**（enabled 与 load_order 同步改 ghost 值，目标形态 §8-4） | 1 | `FAIL: ghost-plugin-not-in-tree plan entry id matches no manifest under plugins/{builtin,dev,optional} (load: ENOENT)` |
| 1b | （加跑）仅改 enabled id 不改 load_order | 1 | `load_order [...] is inconsistent with the enabled entry id set (load: EINVAL)`（落 §8-7，同样非 0） |
| 2 | **payload 引用不符**（files 条目改为 `payload/other-name`） | 1 | `FAIL: files plan entry payload 'payload/other-name' does not match manifest payload 'payload/files' (load: EINVAL)` |
| 3a | **load_order 缺一 id** | 1 | `load_order [...] is inconsistent with the enabled entry id set (load: EINVAL)` |
| 3b | （加跑）load_order 重复一 id | 1 | 同上（集合不一致） |
| 4 | **status 非 plan-only**（改为 `loaded`） | 1 | `FAIL: ... status 'loaded' is not 'plan-only' — only a plan-only plan can be loaded (load: EINVAL)` |
| 5 | （加跑）contract 非本契约 | 1 | `contract 'some/other-contract.md' is not this contract 'kernel/interfaces/loader-contract.md' (load: EINVAL)` |
| 6 | （加跑）输入非 JSON 对象（数组） | 1 | `input is not a JSON object (load: EINVAL)` |
| 7 | （加跑）JSON 语法错误 | 1 | `unreadable/invalid JSON: Expecting property name ... (load: EINVAL)` |
| 8 | （加跑）payload 悬空（最小树：manifest 与 plan 同指不存在文件） | 1 | `FAIL: files payload 'payload/missing-file' does not resolve to an existing file (load: EINVAL)` |

### EAMBIGUOUS 夹具（最小两 compat-bridge 同声明 ipa）

自建最小树 `/tmp/m11-acc/amb-tree/`（builtin/dev 空目录 + optional/amb-a、optional/amb-b；各 `plugin.json` schema v2、type compat-bridge、`protocols: ["ipa"]`、translator 指向仓库内 `plugins/compat/stub-runtime/translator.py`、uninstallable=true 与 optional 目录规则一致、payload 为真实小文件；未整树拷贝，`plugins/dev/etheros-agent-rules` 的仓库根相对 payload 注意点不涉及）：

```
$ python3 tools/validate_plugins.py --file .../amb-a/plugin.json   → plugins validation: OK  rc=0
$ python3 tools/validate_plugins.py --file .../amb-b/plugin.json   → plugins validation: OK  rc=0
$ python3 tools/load_plugins.py --plugins-root amb-tree --config amb.toml → rc=0（真实生产者出计划,load_order [amb-a, amb-b]）
$ python3 tools/load_state.py --plan amb-plan.json --plugins-root amb-tree
rc=1  FAIL: protocol 'ipa' ambiguous: loaded plugins 'amb-a' and 'amb-b' both declare it (load: EAMBIGUOUS, constraint 55)
stdout 为空（无状态 JSON）
```

夹具 manifest 过 v2 校验 ✅；歧义在**装载期**拒绝（约束 55，比路由时才发现更早失败）✅。

判定：**PASS**（四条必选负例 + EAMBIGUOUS 全部非 0 + 明因；加跑 5 条覆盖 §8 全八项形态）

---

## M11-06 旧门禁零回退：CI 十 job 全绿 + 六调用逐字节回归 + release.yml 零 diff

**判据**：十 job 名与行为不变（既有 step 零改动、只追加），load_plugins.py 与 route_plugins.py 缺省输出同 v0.10.0-m10 逐项相等，release.yml 零 diff。验证：CI 十 job 全绿 + 输出回归比对。

### 取证 1：CI run 核验（headSha 逐字核对，防陈旧 run 坑）

```
$ gh run view 40087939306 --repo Nolai2010/EtherOS --json headSha,conclusion,status,event,jobs
headSha   : 2a10245256eb9923bc1841e69af3c5ef85b12fc9   ← 与被验对象 HEAD 逐字相等
conclusion: success | status: completed | event: push | createdAt: 2026-10-24T10:57:19Z
job count : 10 —— 十 job 全 success
  license / spec & docs reference consistency / build / build aarch64 / dco /
  plugin manifest schema & config consistency (M2) / etherkit single-source consistency /
  lint / vm smoke / vm smoke aarch64
```

**headSha 逐字相等** ✅；push 事件 ✅；**十 job 全 success** ✅（含 lint job——连带实证 loader_if.h 宏重排在 CI 工具链下合规，见取证 5）。

### 取证 2：新旧两树六调用逐字节回归（独立复做，未复用实现者结论）

基线 worktree `/tmp/m11-acc-base @ f312bf0` vs 工作树，六种调用各捕获 stdout/stderr/rc 三份产物，`filecmp` 逐字节：

| 调用 | rc | stdout | stderr | 判定 |
|---|---|---|---|---|
| `route_plugins.py --protocol ipa` | 0==0 | IDENTICAL | IDENTICAL(空) | PASS |
| `route_plugins.py --protocol desktop-entry` | 1==1 | IDENTICAL(FAIL ENOENT) | IDENTICAL(空) | PASS |
| `route_plugins.py --run hello-plugin` | 0==0 | IDENTICAL | IDENTICAL(空) | PASS |
| `route_plugins.py`（无参 summary） | 0==0 | IDENTICAL | IDENTICAL(空) | PASS |
| `load_plugins.py`（无参） | 0==0 | IDENTICAL | IDENTICAL(空) | PASS |
| `load_plugins.py --config config/default.toml` | 0==0 | IDENTICAL | IDENTICAL(空) | PASS |

**6/6 逐字节回归通过** ✅。route_plugins.py 缺省路径零变化（该文件 diff 的 3 行"删除"为 docstring 收尾扩展与 main 分派结构替换，缺省路径那行逐字保留在 else 分支内；六调用回归为行为侧硬证）。

### 取证 3：plugin-schema job 日志实读（新 M11 step 与旧步骤全链实证）

job `120854580805` 日志（326 行）关键行：

```
L112: plugins validation: OK                                    ← 旧步骤① M2 全树 v2 校验
L147: "status": "stub-plan-only"（route ipa→douyin）              ← 旧步骤② M3 路由 smoke，stub 口径未变
L161: LOAD PLAN OK 7                                             ← 旧步骤③ M7 装载计划
L198: TOPO OK ['beta', 'alpha', 'gamma']                         ← 旧步骤④ M9 拓扑 smoke
L236/241: TRANSLATE OK / TRANSLATED ARTIFACT LOADABLE OK ['demo-desktop-app']  ← 旧步骤⑤ M10 翻译 smoke
L308: LOAD STATE OK ['files','mon','settings','shell','etheros-agent-rules','douyin','hello-plugin'] ['ipa']   ← 新增 M11 step 三标记①
L309: ROUTE VIA LOAD STATE OK douyin                             ← 三标记②
L310: LOAD-STATE SMOKE OK (M11 real load + route consumption)     ← 三标记③
```

三标记实读 ✅；**旧五步在本 run 内全部重新执行并通过**（M3 路由 smoke 的 douyin 结果仍 `stub-plan-only`——M11 未借装载链改任何既有插件口径）✅。
负例断言执行痕迹（L266/L270/L280/L284/L300/L304：三条 `if out=$(cmd); then ::error; exit 1; fi` + 三条 `grep -q` 命令均在日志中执行）且 **`##[error]` 真注解零命中**（日志中 6 处 `::error` 字样均为青色命令回显，非真注解）——CI 侧负例全部按预期拒绝 ✅。

### 取证 4：job 名集合与 M10/M9 基线 run 对象级比对 + ci.yml 结构比对

```
M11 run 40087939306 vs M10 run 40084445914（@f312bf0=v0.10.0-m10）: job count 10==10, set equal: True, added NONE, removed NONE
M11 run vs M09 run 39054150814（@e238760）:                        job count 10==10, set equal: True, added NONE, removed NONE
三次 run 均十 job 全 success
（任务书备选的 run 40084445929 实为 release.yml 的 run——仅 build release artifacts + publish-release 两 job,非 ci.yml run,故取 40084445914；39054150814 为 M9 合并 run,双重对照）
```

ci.yml 结构比对（difflib opcode 级 + pyyaml job 级对象比对）：

```
difflib non-equal opcodes: [('insert', 154, 154, 154, 233)]  → +79/-0 纯追加,无 delete/replace
pyyaml: job count 10==10; removed jobs NONE; added jobs NONE; non-jobs top-level changed NONE
        job objects changed: ['plugin-schema']
        plugin-schema steps: 6 → 7; new == base + [1 appended]: True; 旧 step 对象逐一相等: True
        追加 step 名: 'Load-state smoke (M11 real load)'
        continue-on-error anywhere in ci.yml: False
```

十 job 名集合与 M10 基线（及 M9 基线）**逐一相等** ✅；唯一变化的 job 是 `plugin-schema`——旧 6 个 step 原样保留、仅在末尾追加第 7 个 step，纯增强（无断言放宽、无 suppress）✅。
**口径记档（与 M9-05/M10-06 先例同口径）**：严格字面读"十 job 行为不变"，plugin-schema 多跑一个 step 属行为变化；但方向为纯增强（step 内容正是 M11-02/03/04/05 判据所要求的 CI 覆盖，负例断言三方向可失败，见 M11-05 附加取证），按"方向只许更严"惯例判零回退、**PASS-with-note 记档**。其余 9 个 job 对象全等。

### 取证 5：release.yml 零 diff + loader_if.h 3 行宏对齐空白证明

```
$ git diff v0.10.0-m10..HEAD -- .github/workflows/release.yml | wc -c
0
```

**release.yml 0 字节** ✅（config/、plugins/schema/、tools/load_plugins.py、tools/validate_plugins.py、plugins/ 整树、base/ 亦 0 字节，见 D1）。

loader_if.h 的 3 行变化（`ETHEROS_OK`/`ENOENT`/`EINVAL` 三宏）**仅限空白**的独立证明：

1. **语义逐字**：diff 删除行恰 3 行且均为宏行；去空白规范化后旧行与新行逐一相同（`#define ETHEROS_OK 0 /* plan produced */` 等 3/3 True）；旧文件其余全部非空行按原顺序出现在新文件（行守恒：127 → 198 行，净 +71，与 +74/-3 的 numstat 一致）——`plan_load` 及既有全部声明零改动；
2. **必要性实证（反事实）**：取基线文件、仅在宏块内插入 `ETHEROS_EAMBIGUOUS` 而**不重排**，本机 clang-format 15.0.0 + 仓库 `.clang-format` 干跑 → **rc=1，恰报 3 处违规（107/108/109 行，即三行旧宏）**——"不重排则 CI lint 必红"属实；纯基线文件干跑 rc=0（对照）；
3. **充分性实证**：提交态文件本机 `--dry-run --Werror` **rc=0**；且 **CI lint job（run 40087939306）success**——CI 侧工具链实证接受。

结论：属"契约逐字保留"（语义未动）与"lint 零回退"（门禁通过）两条约束的交涉点，**接受、记档，不要求回退**（与审查 Minor 裁定同结论，本方独立取证）。

判定：**PASS**（plugin-schema 追加一个 step 按先例口径 PASS-with-note 记档，见取证 4）

---

## CI smoke 非空转抽验（对抗探针，证明断言可失败）

自选对抗探针（全部落 /tmp/m11-acc/probe/**，以 GitHub Actions 同款 `bash -eo pipefail` 执行）：

- **探针 0（基线对照）**：CI step 正例管道原样本地复跑 → `LOAD STATE OK [7 ids] ['ipa']` / `ROUTE VIA LOAD STATE OK douyin` / **EXIT=0**（与 CI 日志三标记逐字一致）；
- **探针 ①a**：把状态 `routes` 清空 → 正例 route 消费管道 rc=1（消费者 JSON 解析失败，pipefail 生效）→ 门禁会红 ✅；
- **探针 ①b**：给状态 `routes` 注入 `desktop-entry` → `set(routes) == {"ipa"}` 断言 AssertionError（"routes must be exactly ipa: ['desktop-entry', 'ipa']"）→ 门禁会红 ✅；
- **探针 ③**：registry 逆序（与 load_order 不符）→ "registry id order must equal plan load_order" AssertionError → 门禁会红 ✅；
- **探针 ②（负例断言模式三方向）**：以 ghost-id 断言为例——cmd 意外成功 → `::error` 分支（红）；cmd 失败但原因不符（status 非 plan-only 的输出）→ grep 不中（红）；cmd 失败且原因相符（目标形态）→ 放行（绿）。三方向实证，新模式无"意外成功反而放行"路径 ✅。

**CI smoke 非空转，实证成立。**

---

## 已知 Minor 与 known-deferred notes 逐条独立核实（记档，不判 FAIL）

以下 3 条为 M11-6 审查报告的 Minor 项，本验收独立复核结论如下（均不要求回退）：

1. **load_state.py §8-7 校验为集合口径**（`load_state.py:84`，`sorted(order) != sorted(entry_ids)`）——独立复核属实：构造整体逆序的 load_order 喂入 → rc=0 被接受，registry 随该逆序物化（实测 registry == 逆序后的 load_order，逐项相等）。契约 §8-7 字面即"与条目 id **集**不一致"，实现与契约字面一致；契约 §2 的"同序"是计划生成者（load_plugins.py，实测恒同序）的义务，该形态经真实生产者不可达。**与审查裁定同结论：不构成缺陷，记档；如需更严须契约 §8-7 文案与实现同步改（后续里程碑事项）。**
2. **spec-consistency job 白名单止于 M10**（ci.yml:359 元组 `("M0"…"M10")`）——独立复核属实：M11 章节已入库但未纳入防删保护元组（若 M11 章节被删，该 job 不会红）。先例同形态（M7-01→扩 M7、M9-3→扩 M9、M10-6→扩 M10），**归 M11-8 关门处理**（纯增强，不会假红）；按先例本轮不判 FAIL。
3. **route_plugins FAIL 明因走 stdout 而非 stderr**（M3 既有约定，`route_plugins.py:161-163`）——独立复核属实：缺省模式与 `--load-state` 模式的 FAIL 均打 stdout、stderr 为空、rc=1；load_state.py 的 FAIL 走 stderr。两者不一致，但缺省路径行为零变化是硬约束，新代码沿用旧约定正确。**记档**（任务书中"stderr 明因"表述对 route 路径历来适用于 stdout，特此说明）。

另记档（非缺陷）：`--load-state` 未激活原因的 bilingual 表述（「装载状态」中文字样为 CI 断言区分两模式所必需，语义明确）；本机 Python 内联 `/tmp` 路径不经 MSYS 转换为测试环境注意点（CI/Linux 不受影响）。

---

## 口径差异与遗留

1. **M11-06「十 job 行为不变」的严格读法差异（与 M9-05/M10-06 先例同口径）** —— `plugin-schema` 是十者中唯一非对象全等的：追加一个 M11 load-state smoke step（6→7，旧 6 step 逐字保留）。严格字面读其"行为"确有变化（多跑一个 step）；但方向为**纯增强**（无断言放宽、无 `continue-on-error`、无 suppress，负例断言三方向可失败），按"方向只许更严"惯例判零回退、PASS-with-note 记档。其余 9 job 对象全等。
2. **loaded 边界三处同口径的范围** —— 约束 51 字面含 RELEASE_NOTES/README，但二者属 M11-8 关门范围（本区间 `git diff` 零命中，计划 File Structure 明列归 M11-8）。本轮按区间判定：工具输出 notes/docstring、loader-contract.md §7、plugin-routing.md §5 四处同口径（含工具 docstring 共四处），README/RELEASE_NOTES 留待 M11-8 关门时同口径补写并复核。
3. **本报告未登记进 `docs/index.md`** —— 验收者铁律限制改动仓库文件（唯一例外即本报告本身）。沿用 M5~M10 报告先例，由 M11-8 关门任务补登。
4. **远端写操作** —— 本机到 github.com 的 HTTPS 通道：区间取证全部走 `gh` GET 与 `git ls-remote`（只读）；报告的推送见文末提交与 CI 复核段（若遇代理 502 按任务书重试纪律处理并如实记录）。
5. **临时目录与 worktree 卫生** —— 全部夹具与产物落 `/tmp/m11-acc/**`（plan/state/neg/amb-tree/probe/reg-*/fmt 对照件），未落进仓库；基线 worktree `/tmp/m11-acc-base` 用后已 `git worktree remove` 注销；`git status --porcelain` 在验收前后均为空。
6. **§8-7 逆序接受与正例断言的相互关系** —— 正例断言"registry id 序列 == plan load_order"（M11-02 #6）对逆序输入同样成立（registry 忠实跟随 load_order），故逆序接受不削弱 M11-02 判据；它只是"集合口径 vs 顺序口径"的宽严之差，且经真实生产者不可达（见 known-deferred notes 1）。

---

**总判定：M11-01 ~ M11-06 六条全部 PASS（M11-06 按 M9-05/M10-06 先例口径记档"plugin-schema 追加一个 step、方向纯增强"），阻塞缺陷 0；3 条 Minor 均为记档/建议级（§8-7 集合口径与契约字面一致且不可达、spec-consistency 白名单未扩 M11 归 M11-8、FAIL 输出流约定），3 条口径差异已如实记档 —— 其中"plugin-schema 纯增强记档"与"loaded 诚实边界四处同口径 + CI 三标记实证"是最需要终审知悉的两点。**

---

## 提交与 CI 复核（报告入库后）

### 提交与推送

```
$ git add docs/reports/2026-10-24-m11-acceptance.md   （提交前 git status --porcelain 仅含该文件）
$ git commit -s -m "docs: M11 acceptance report (M11-01..06, independent)"
[feat/m11-load-closure 2e247ca] docs: M11 acceptance report (M11-01..06, independent)
 1 file changed, 436 insertions(+)   Signed-off-by: Nolai <120611751+Nolai2010@users.noreply.github.com>

$ git push origin feat/m11-load-closure
   2a10245..2e247ca  feat/m11-load-closure -> feat/m11-load-closure   （一次成功,无 502 重试）

$ git ls-remote origin refs/heads/feat/m11-load-closure
2e247ca36684995352f10385bfeb815f28210489  refs/heads/feat/m11-load-closure   ← 与本地新提交逐字相等
```

### 推送后 CI 复核（先核对 headSha 再取 run id,防陈旧 run）

```
$ gh run list --branch feat/m11-load-closure --limit 3 --json databaseId,headSha,conclusion,status,event
新 run: 40091498889, headSha 2e247ca36684995352f10385bfeb815f28210489 ← 等于本报告提交,非陈旧 run; event: push

$ gh run view 40091498889 --repo Nolai2010/EtherOS --json headSha,conclusion,status,event,jobs
headSha   : 2e247ca36684995352f10385bfeb815f28210489
conclusion: success | status: completed | event: push
job count : 10 —— 十 job 全 success（docs-only 提交）
  dco / license / etherkit single-source consistency / spec & docs reference consistency /
  build ToaruOS base / lint / plugin manifest schema & config consistency (M2) /
  build ToaruOS aarch64 base / vm smoke / vm smoke aarch64
```

新 headSha（`2e247ca`）上 **十 job 全 success** ✅（docs-only：本报告入库不触发任何门禁变化，plugin-schema job 的 M11 load-state smoke step 在新 commit 上再次全绿）。轮询期间 GitHub API 一次瞬时 502 按重试纪律重取后终态 success（502 为代理瞬断，非 CI 失败）。

**STATUS: PASS**

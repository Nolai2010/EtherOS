# M9 独立验收报告 —— schema v2（插件依赖声明 + 拓扑装载）

- **验收者**：general-purpose-2（独立上下文，与 M9-1~M9-4 的实现者 / 复审者均不同；不替实现背书，不粉饰，不采信任何自评输出）
- **被验对象**：分支 `feat/m9-schema-v2`，HEAD `cfc4c18`（`cfc4c18697fe44c1b8d6c1bcb12249ba5b1c0b35`，提交主题 `ci: M9 gate, schema v2 wording, topology smokes, fixtures`）
- **区间**：`dc16897..HEAD`，共 **4 个非合并提交**（`966cc40` → `b43f82f` → `3d2872e` → `cfc4c18`）；对照基线 tag `v0.8.0-m8` = `edb6b23`
- **仓库**：`I:/etheros`（远端 `github.com/Nolai2010/EtherOS`）
- **执行日期**：2026-10-18
- **依据**：`docs/development/acceptance-standard.md` §`## M9 · schema v2（插件依赖声明 + 拓扑装载）`（M9-01~M9-06）+ 验收简报 `.superpowers/sdd/2026-10-05-etheros-m0m1-implementation/briefs/m9-t5-acceptance-brief.md`
- **口径**：偏严。全部判据**自己实跑取证**；M9-04 的零依赖退化基线是**自己** `git worktree add` 取 `v0.8.0-m8` 实跑出来的（未采信实现者贴的任何输出），用完已 `worktree remove` + `prune`；零回退一律用 pyyaml 做 **job 级对象比对**，不做肉眼 diff；夹具全程只落 `/tmp`
- **写操作范围**：**仅新建本报告一个文件**；未改 ci.yml / release.yml / schema / manifest / tools / acceptance-standard.md，未推 tag、未动 main、未派子代理

---

## 0. 判据存在性核验与被验对象定位

```
$ git -C I:/etheros log --oneline -1
cfc4c18 ci: M9 gate, schema v2 wording, topology smokes, fixtures
$ git -C I:/etheros branch --show-current
feat/m9-schema-v2
```

HEAD 与简报所述 `cfc4c18` 一致 ✅；分支正确。

判据实存：`docs/development/acceptance-standard.md` 的 `## M9 · schema v2（插件依赖声明 + 拓扑装载）` 章节表，M9-01~M9-06 六条编号 / 标准 / 验证方式齐备，无缺项 ✅（该文件由 `966cc40` 入库，+11 行，纯追加）。该章节已被 spec-consistency 门禁的里程碑白名单覆盖（见 M9-06）。

**零改动文件核验**（验收者铁律的自我取证）：写本报告前 `git status --short` 为空；本报告为本次唯一新增文件。

判定：**PASS**（判据齐备、被验对象定位准确、无越界动作）

---

## 夹带与 DCO 总检（先行）

### D1 全量文件清单（`dc16897..HEAD`，18 个文件全部为 M，零新增零删除）

```
$ git diff --name-status dc16897..HEAD
M  .github/workflows/ci.yml
M  docs/development/acceptance-standard.md
M  kernel/interfaces/loader-contract.md
M  kernel/interfaces/loader_if.h
M  plugins/builtin/files/plugin.json
M  plugins/builtin/mon/plugin.json
M  plugins/builtin/settings/plugin.json
M  plugins/builtin/shell/plugin.json
M  plugins/dev/etheros-agent-rules/plugin.json
M  plugins/optional/douyin/plugin.json
M  plugins/optional/hello-plugin/plugin.json
M  plugins/schema/plugin.schema.json
M  tests/plugins/negative/bad-container.json
M  tests/plugins/negative/bad-uninstallable.json
M  tests/plugins/negative/compat-bridge-translator-missing.json
M  tests/plugins/negative/compat-bridge-without-translator.json
M  tools/load_plugins.py
M  tools/validate_plugins.py
```

18 个文件全部落在 M9-01~M9-06 的应动范围内 ✅。

> 注：以 `v0.8.0-m8`（`edb6b23`）为基准比对时，清单会多出 `docs/reports/2026-10-17-m8-acceptance.md`（M8 报告"事后复核"段）。经核该改动发生在 `edb6b23..dc16897` 之间（M8 关门后补记），**不在 M9 区间**，非 M9 引入，不计为 M9 夹带。

### D2 逐提交范围（4 个提交，均带 Signed-off-by）

```
$ git log dc16897..HEAD --no-merges --stat --format='%h %s'
cfc4c18 ci: M9 gate, schema v2 wording, topology smokes, fixtures
  .github/workflows/ci.yml | 46 +++++  tests/plugins/negative/*.json | 2 +- ×4      (M9-02 夹具迁移 + M9-04/06 CI)
3d2872e feat: loader dependency topology, cycle rejection, contract sync
  kernel/interfaces/loader-contract.md | 15 +-  loader_if.h | 25 +-  tools/load_plugins.py | 97 ++++   (M9-04/05)
b43f82f feat: schema v2 deps, tree migration, validator, CI anchor
  ci.yml | 8 +-  7× plugin.json | 2 +-  plugin.schema.json | 14 +-  validate_plugins.py | 68 +++      (M9-01/02/03/06)
966cc40 docs: add M9 acceptance criteria (controller-verified)
  docs/development/acceptance-standard.md | 11 +++                                                     (判据入库)
```

```
$ git log dc16897..HEAD --no-merges --format='%h | %s | %(trailers:key=Signed-off-by,valueonly)'
cfc4c18 | ci: M9 gate, schema v2 wording, topology smokes, fixtures | Nolai <120611751+Nolai2010@users.noreply.github.com>
3d2872e | feat: loader dependency topology, cycle rejection, contract sync | Nolai <120611751+Nolai2010@users.noreply.github.com>
b43f82f | feat: schema v2 deps, tree migration, validator, CI anchor | Nolai <120611751+Nolai2010@users.noreply.github.com>
966cc40 | docs: add M9 acceptance criteria (controller-verified) | Nolai <120611751+Nolai2010@users.noreply.github.com>
```

4/4 提交带 `Signed-off-by` ✅；主题长度实测 57 / 64 / 58 / 54，均 ≤72 ✅；每个提交只动其任务应动文件，无跨任务裹挟 ✅。

判定：**PASS**（无夹带、DCO 齐备）

---

## M9-01 plugin.schema.json 升 v2

### 取证 1：与 `v0.8.0-m8` 版 properties 键集合程序化比对

```
$ git show v0.8.0-m8:plugins/schema/plugin.schema.json > /tmp/m9acc/schema-v1.json
$ cp plugins/schema/plugin.schema.json /tmp/m9acc/schema-v2.json
$ python -c "<json 载入两版做集合与逐字段比对>"

v1 props: [capabilities, container, name, payload, protocols, resources, schema_version, tools, translator, type, uninstallable, version]
v2 props: [capabilities, container, dependencies, name, payload, protocols, resources, schema_version, tools, translator, type, uninstallable, version]
added  : ['dependencies']
removed: []
required v1: ['schema_version','name','version','type','uninstallable','payload','container']
required v2: ['schema_version','name','version','type','uninstallable','payload','container']
required equal: True
addProps v1/v2: False False
allOf equal: True
const v2: 2
SAME capabilities / container / name / payload / protocols / resources / tools / translator / type / uninstallable / version
deps item pattern == name pattern: True   (^ [a-z][a-z0-9-]*$ 两处逐字相同)
```

**键集合只多 `dependencies` 一个**（11 → 12），无删改 ✅；`required` 未被扩（dependencies 仍为可选）✅；`additionalProperties: false` 保留 ✅；除 `schema_version` 的 `const`（1→2，即本条判据要求）与其 description 外，**其余 11 个共有字段定义逐字未改**（含 name/version 的 pattern、type 的 enum、container 子属性、translator 前缀 pattern）✅；末尾 `allOf`（compat-bridge ⇒ protocols 非空 + translator）对象全等 ✅。

### 取证 2：元素 pattern 与 name 一致

```
deps def: {"type":"array","items":{"type":"string","pattern":"^[a-z][a-z0-9-]*$"},"uniqueItems":true,...}
name pattern: ^[a-z][a-z0-9-]*$
→ 两者逐字相等 ✅
```

### 取证 3：schema 自身元校验

`tools/validate_plugins.py` 首步 `Draft202012Validator.check_schema` 实跑未报 `schema meta-validation failed`（全树校验 `exit=0`），schema 结构自洽 ✅。

判定：**PASS**

---

## M9-02 全树 manifest 迁移 + validator 明确拒 v1 并给迁移提示

### 取证 1：全树 `schema_version` 清单（零 "1" 命中）

```
$ git grep -n '"schema_version"' -- plugins/ tests/
plugins/builtin/files/plugin.json:2:  "schema_version": "2",
plugins/builtin/mon/plugin.json:2:  "schema_version": "2",
plugins/builtin/settings/plugin.json:2:  "schema_version": "2",
plugins/builtin/shell/plugin.json:2:  "schema_version": "2",
plugins/dev/etheros-agent-rules/plugin.json:2:  "schema_version": "2",
plugins/optional/douyin/plugin.json:2:  "schema_version": "2",
plugins/optional/hello-plugin/plugin.json:2:  "schema_version": "2",
tests/plugins/negative/bad-container.json:2:  "schema_version": "2",
tests/plugins/negative/bad-uninstallable.json:2:  "schema_version": "2",
tests/plugins/negative/compat-bridge-translator-missing.json:2:  "schema_version": "2",
tests/plugins/negative/compat-bridge-without-translator.json:2:  "schema_version": "2",

$ git grep -n '"schema_version": *"1"' -- plugins/ tests/
NO_MATCH_v1
```

**7 个 manifest + 4 个负例夹具全为 "2"，零 "1" 命中** ✅（与简报要求的数量、取值逐项吻合）。

全仓库范围另有三处 `"schema_version": "2"`：ci.yml 的 4 个 M9 拓扑夹具（:87/:91/:95/:99）、ci.yml 锚点断言（:250）、`tools/validate_plugins.py:111` 的读取点 —— 均为配套同步，非 manifest 遗漏。

### 取证 2：manifest diff 无夹带（除版本行外零改动）

```
$ git diff v0.8.0-m8..HEAD -- plugins/builtin plugins/dev plugins/optional
 7 个文件，每个 hunk 均只有一行：
-  "schema_version": "1",
+  "schema_version": "2",
```

7/7 均为单行版本替换，无夹带 ✅；4 个负例夹具同理 ✅。

### 取证 3：v1 manifest 负例实跑（/tmp 夹具，仓库内不新增文件）

夹具 `/tmp/m9acc/fx/v1-manifest.json`（`schema_version: "1"`，其余字段按 v1 合法形态构造：native / uninstallable true / payload 指向同目录真实 `payload.bin` / container 合法）：

```
$ python tools/validate_plugins.py --file /tmp/m9acc/fx/v1-manifest.json
FAIL: ...v1-manifest.json schema: '2' was expected
FAIL: ...v1-manifest.json manifest schema_version '1' is superseded by '2'; migrate: set "schema_version": "2" in this plugin.json (spec §2.4 契约版本化, M9 约束 39)
exit=1
```

非 0 退出 ✅；**迁移提示明确存在**（`migrate: set "schema_version": "2" in this plugin.json`）✅ —— 不只是"scheme 报错"，而是带可执行迁移指引的语义层拒绝（`tools/validate_plugins.py:111-113`）。

对照正例：`python tools/validate_plugins.py --file /tmp/m9acc/fx/ok-dep.json` → `plugins validation: OK`，`exit=0`（证明负例的红不是夹具本身畸形的假红）。

全树校验实跑：`python tools/validate_plugins.py` → `plugins validation: OK`，`exit=0` ✅。

判定：**PASS**

---

## M9-03 依赖语义断言（自依赖 / 重复 / 引用不存在 id）

三条负例夹具全部自建于 `/tmp/m9acc/fx/`，逐条实跑：

```
=== 自依赖 self-dep.json  dependencies: ["self-dep"] ===
FAIL: ...self-dep.json dependencies: self-dependency 'self-dep' — a plugin cannot depend on itself (M9 v2, 约束 40)
FAIL: ...self-dep.json dependencies: 'self-dep' not found in plugin tree — every dependency must reference an existing plugin id (M9 v2, 约束 40)
exit=1

=== 重复依赖 dup-dep.json  dependencies: ["files", "files"] ===
FAIL: ...dup-dep.json schema: ['files', 'files'] has non-unique elements
FAIL: ...dup-dep.json dependencies: duplicate entry 'files' — dependencies must be a set of distinct plugin ids (M9 v2, 约束 40)
exit=1

=== 引用不存在 id missing-dep.json  dependencies: ["no-such-plugin"] ===
FAIL: ...missing-dep.json dependencies: 'no-such-plugin' not found in plugin tree — every dependency must reference an existing plugin id (M9 v2, 约束 40)
exit=1

=== 对照正例 ok-dep.json  dependencies: ["files", "mon"] ===
plugins validation: OK
exit=0
```

三条各**非 0 退出**且**原因与形态一一对应** ✅；重复依赖由 schema 层 `uniqueItems` 与 validator 语义层双重拦下（语义层给的是可读原因，不是裸 JSON Schema 报错）✅；存在性断言在 `--file` 单文件模式下也对真实插件树生效（`tree_plugin_ids()` 实读 `plugins/{builtin,dev,optional}`）✅。

> 口径说明（不判 FAIL）：自依赖负例同时触发了"引用不存在 id"这条（因为 `self-dep` 这个 id 本就不在真实插件树里）。两条都指向同一个根因，且**自依赖专属原因在第一行**，判定不受影响。

判定：**PASS**

---

## M9-04 装载器拓扑排序（本里程碑核心）

### 取证 1：零依赖退化 —— 与 `v0.8.0-m8` 基线**自己实跑**逐项比对

```
$ git worktree add /tmp/m9acc/baseline v0.8.0-m8
Preparing worktree (detached HEAD edb6b23)
$ cd /tmp/m9acc/baseline && python tools/load_plugins.py > /tmp/m9acc/plan-baseline.json   # exit=0
$ cd I:/etheros && python tools/load_plugins.py > /tmp/m9acc/plan-m9.json                  # exit=0
$ python -c "<json 逐项比对>"

baseline load_order: ['files','mon','settings','shell','etheros-agent-rules','douyin','hello-plugin']
m9      load_order: ['files','mon','settings','shell','etheros-agent-rules','douyin','hello-plugin']
ITEMWISE EQUAL     : True
```

**与简报给出的基线序列 `files, mon, settings, shell, etheros-agent-rules, douyin, hello-plugin` 逐项相等** ✅ —— 仓库内 7 个插件全无依赖，升级后 `load_order` 一个位置都没动，无回退。

清理：`git worktree remove /tmp/m9acc/baseline && git worktree prune`，`git worktree list` 复原为仅 `I:/etheros` ✅。

### 取证 2：键名集合与基线做集合比对

```
top keys baseline: [contract, enabled, load_order, notes, skipped, stage, status]
top keys m9      : [contract, enabled, load_order, notes, skipped, stage, status]
top key set equal: True            （顶层 7 键）
entry keys baseline: [capabilities, category, container, id, payload, type]
entry keys m9      : [capabilities, category, container, id, payload, type]
entry key set equal: True          （每项 6 键）
all entries 6 keys: True True
status baseline/m9: plan-only plan-only     （status 仍固定 "plan-only" ✅）
contract equal: True    stage equal: True    skipped equal: True
entry payload equal: True   （7 项条目除顺序外全等）
```

顶层 7 键 + 每项 6 键，集合与基线**完全一致**，无新增 / 改名 ✅。

### 取证 3：notes 中"无依赖排序来源"表述确已改掉

```
--- baseline notes（旧） ---
 * schema v1 无 dependencies 字段,依赖顺序无来源;load_order 为目录序遍历序(...)
--- m9 notes（新） ---
 * schema v2 起 manifest 支持可选 dependencies 字段:load_order 为依赖拓扑序(被依赖者在前);无依赖时退化为目录序遍历序(...)
 * 依赖 id 必须落在本次装载的启用集里(树里有但未启用同样拒绝);依赖成环由本装载器检测,检测到即拒绝出计划(非 0 退出并列出环上成员,约束 41)。
```

```
$ git grep -n -E "依赖顺序无来源|无依赖排序来源|无 \`dependencies\` 字段"
docs/development/acceptance-standard.md:127:| M9-05 | ... notes 中"无依赖排序来源"表述已更新 ... |
```

唯一命中是**判据文本自身在引用该表述**，非残留实现/文档陈述 ✅。

### 取证 4：夹具树验证拓扑序（被依赖者在前）

自建夹具树 `/tmp/m9acc/fxdep`（`alpha→beta`、`zulu→alpha`、`optional/gamma→beta`；目录序 alpha<beta<zulu，config 仅启用 gamma）：

```
$ python tools/load_plugins.py --plugins-root /tmp/m9acc/fxdep --config /tmp/m9acc/fxdep.toml
load_order: ['beta', 'alpha', 'zulu', 'gamma']
beta  < alpha : True        （目录序里 beta 在 alpha 之后，被依赖者被提前）
alpha < zulu  : True
beta  < gamma : True        （跨类别依赖同样生效）
enabled ids == load_order: True
status: plan-only
exit=0
```

**目录序被真实拓扑关系改写**（若退化路径出错，输出会是 `alpha,beta,zulu,gamma`）✅。

另按 ci.yml 内 M9 step 的**原样夹具**复跑一次（`alpha→beta` + 无关 `gamma`）：`TOPO OK ['beta', 'alpha', 'gamma']`，`exit=0` ✅。

### 取证 5：依赖环 → 非 0 退出并列出环上成员

```
$ python tools/load_plugins.py --plugins-root /tmp/m9acc/fxcycle --config /tmp/m9acc/fxempty.toml   # a↔b
FAIL: dependency cycle detected among: a → b → a (load: EINVAL, constraint 41)
exit=1

$ python tools/load_plugins.py --plugins-root /tmp/m9acc/fxcycle3 --config /tmp/m9acc/fxempty.toml  # p→q→r→p
FAIL: dependency cycle detected among: p → q → r → p (load: EINVAL, constraint 41)
exit=1
```

2-环与 3-环均**非 0 退出**且**环上成员完整列出**（含闭环首尾同节点）✅；无 warn 降级、无静默跳过。

### 取证 6：依赖未启用 → 非 0 退出

```
$ python tools/load_plugins.py --plugins-root /tmp/m9acc/fxnoen --config /tmp/m9acc/fxnoen.toml   # alpha→orphan(optional,未启用)
FAIL: ...fxnoen.toml plugin 'alpha' depends on 'orphan', which exists in the plugin tree but is not enabled in this load (optional plugins must be listed in [plugins] enabled — Global Constraint 12)
exit=1

$ python tools/load_plugins.py --plugins-root /tmp/m9acc/fxghost --config /tmp/m9acc/fxempty.toml  # alpha→ghost(全树无此 id)
FAIL: alpha plugin 'alpha' depends on 'ghost', which matches no manifest under plugins/{builtin,dev,optional} (load: ENOENT)
exit=1
```

"树里有但未启用"与"树里根本没有"两种形态分别给出 ENOENT 语义的原因并**非 0 退出** ✅（`tools/load_plugins.py:123-137`）。

判定：**PASS**（本条是 M9 最核心的一条，六项子取证全部实跑通过）

---

## M9-05 契约同步（loader-contract.md + loader_if.h）

### 取证 1：loader-contract.md 反映拓扑语义

```
$ git diff v0.8.0-m8..HEAD -- kernel/interfaces/loader-contract.md
- `load_order` | 装载顺序(插件 id 列表,与 `enabled` 各项 `id` 同序)
+ `load_order` | 装载顺序(...同序):**依赖拓扑序**(被依赖者在前);**无依赖时退化为目录序**(builtin → dev → optional,各类内目录名字典序)
- `notes` | 诚实声明(未真正装载、依赖排序无来源等)
+ `notes` | 诚实声明(未真正装载、依赖拓扑/环检测口径、装载期边界等)
## 3. 装载顺序
- 顺序 = **builtin → dev → optional**;各类内部按**目录名字典序**。
- schema v1 **无 `dependencies` 字段** → 依赖顺序无来源,按"无依赖顺序约束"处理;...
+ **顺序 = 依赖拓扑序** ... **被依赖者排在前**(A 依赖 B ⇒ B 在 A 之前);同批就绪者按目录序消费。
+ **无依赖时退化为目录序** ... (与 M7/M8 的既有输出逐项一致)。
+ **依赖环 = 拒绝** ... 非 0 退出并列出环上成员(见 §5-5);不得静默跳过、不得降级为 warn。
+ **依赖必须被启用** ... 树中存在但本次未启用 ⇒ 同样拒绝(见 §5-4)。
+ 分层口径(M9 约束 41):validator 管"插件树里有没有这个 id"...;loader 管"这一次装载有没有启用它"以及"依赖图是否成环"。
§5 拒绝语义 新增第 4、5 条(依赖未启用 / 依赖成环),与实跑负例一一对应。
```

"无依赖排序来源"表述确已删除，替换为拓扑语义 ✅；§5 拒绝语义扩到 5 条且与 M9-04 的实跑输出对应 ✅。

### 取证 2：loader_if.h 反映拓扑语义

```
- * order of "entries" IS the load order.  Schema v1 carries no
- * dependency field, so the order is provenance order: ...
+ * ... Since schema v2 a manifest may declare the optional "dependencies"
+ * array ...: the load order is then the dependency TOPOLOGICAL order, a
+ * dependency always preceding its dependent.  With no dependency declared
+ * the order degenerates to provenance order ... -- byte-identical to the
+ * pre-v2 output.  A dependency cycle, or a dependency absent from this
+ * load's enabled set, is rejected (plan_load returns EINVAL / ENOENT) --
+ * never silently skipped.
-#define ETHEROS_ENOENT (-1) /* config-enabled id matches no manifest in the tree */
+#define ETHEROS_ENOENT (-1) /* enabled id or dependency matches no manifest */
+#define ETHEROS_EINVAL (-2) /* bad manifest, dangling payload, bad dependency */
 plan_load 注释新增 Order / 依赖未启用 / 依赖成环三段
```

机器可读形态与契约文档同步 ✅；返回码语义扩展（依赖场景），**未新增/改名任何返回码** ✅。

### 取证 3：契约键名集合不变

契约 §2 顶层键表（`status` / `contract` / `stage` / `enabled` / `load_order` / `skipped` / `notes`）与 `enabled[]` 每项键表（`id` / `type` / `category` / `payload` / `container` / `capabilities`）—— diff 中**只改了 `load_order` 与 `notes` 的"语义描述"列，键名列一字未动** ✅；与 M9-04 取证 2 的输出键名集合实测（顶层 7 + 每项 6）互为交叉验证 ✅。

判定：**PASS**

---

## M9-06 旧门禁零回退 + schema 锚点同步

### 取证 1：release.yml 零 diff

```
$ git diff v0.8.0-m8..HEAD -- .github/workflows/release.yml | wc -c
0
$ git diff --name-only v0.8.0-m8..HEAD -- .github/
.github/workflows/ci.yml          （仅此一个）
```

**0 字节** ✅；`.github/` 全目录只有 ci.yml 一个文件被改 ✅。

### 取证 2：pyyaml job 级对象比对（10 job）

```
$ python -c "<yaml.safe_load 两版，逐 job 对象全等比对>"
top-level keys base: [True, 'jobs', 'name']     # True 即 YAML 1.1 下的 on:
top-level keys m9  : [True, 'jobs', 'name']
non-jobs equal: True
job count base/m9: 10 10
job names base: [etherkit-consistency, plugin-schema, license, dco, lint, spec-consistency, build, vm-smoke, build-aarch64, vm-smoke-aarch64]
job names m9  : [etherkit-consistency, plugin-schema, license, dco, lint, spec-consistency, build, vm-smoke, build-aarch64, vm-smoke-aarch64]
job name set equal: True      job order equal: True

IDENTICAL  etherkit-consistency
CHANGED    plugin-schema
IDENTICAL  license
IDENTICAL  dco
IDENTICAL  lint
CHANGED    spec-consistency
IDENTICAL  build
IDENTICAL  vm-smoke
IDENTICAL  build-aarch64
IDENTICAL  vm-smoke-aarch64
```

10 个 job，**名集合与顺序全等，零删除、零改名** ✅；除 spec-consistency（本条判据要求同步的那一 job）外，**8/9 个其他 job 对象全等**。

`plugin-schema` 是九者中唯一发生变化的，变化内容为：① 步骤名 `Validate plugin manifests against schema v1` → `...v2`（措辞同步）；② **新增**一个 `Dependency topology smoke (M9 load_plugins dependencies)` 步骤。二者均**纯增强**、未放宽任何断言、未加 `continue-on-error` / suppress，不构成回退。严格读"其余九 job 行为不变"，该 job 属"行为被扩"而非"行为被改"，已如实记档见 §口径差异与遗留 项 2。

### 取证 3：锚点确为 "1"→"2"，且仍是严格 fail（非消音、非删除）

```
--- 两版 spec-consistency 内联 python 的锚点行 ---
BASELINE: if schema.get("properties", {}).get("schema_version", {}).get("const") != "1":
          fails.append("plugin.schema.json schema_version anchor drifted from \"1\"")
M9      : if schema.get("properties", {}).get("schema_version", {}).get("const") != "2":
          fails.append("plugin.schema.json schema_version anchor drifted from \"2\"")
两版均: print("\n".join(fails)); sys.exit(1)
exit1 存在: True True | fails.append 存在: True True | warn 字样: False False
```

断言结构（`!=` 比较 → `fails.append` → `sys.exit(1)`）**一字未变**，改的只是"当前契约版本"这个事实值 ✅；未被改成只 warn、未被删除、未加豁免 ✅。

### 取证 4：锚点漂移仍会红（非消音的实证）

```
$ python -c "<取真实 schema，按 M9 断言式求三种取值>"
真实文件 const         : '2' -> 断言触发(应 False): False     （当前不红）
漂移到 "1" -> 断言触发(应 True) : True                        （改回旧版 → 红）
漂移到 "3" -> 断言触发(应 True) : True                        （漂到未来版 → 红）
```

### 取证 5：本地实跑 spec-consistency 脚本（取 HEAD 版 ci.yml）

```
$ python -c "<ci.yml spec-consistency 内联 python>"
spec consistency: OK
exit: 0
```

含 M9 章节存在性（`## M9` 行首锚定）与锚点 `.const == "2"`，本地实测通过 ✅。

### 取证 6：本地复跑 plugin-schema 各 step

```
route ipa: OK                       route bogus: 非0 OK
run hello: OK                       run douyin: OK
LOAD PLAN OK 7                      bogus enabled: 非0 OK
TOPO OK ['beta', 'alpha', 'gamma']  （M9 新增 step 正例）
FAIL: dependency cycle detected among: a → b → a ... exit=1   （M9 新增 step 负例）
```

判定：**PASS**

---

## 其它零改动核验

```
$ for p in base/toaruos config/ CORE_MANIFEST.toml REUSE.toml .etherkit/; do
    git diff --name-only v0.8.0-m8..HEAD -- "$p" | wc -l; done
base/toaruos -> 0     config/ -> 0     CORE_MANIFEST.toml -> 0     REUSE.toml -> 0     .etherkit/ -> 0
```

```
$ git diff v0.8.0-m8..HEAD --submodule=short -- base/toaruos
（空输出，无 +/- 前缀漂移）
$ git ls-tree HEAD base/toaruos        160000 commit e77143fd14391d880c3ee11c1524252cdcbfd225
$ git ls-tree v0.8.0-m8 base/toaruos  160000 commit e77143fd14391d880c3ee11c1524252cdcbfd225
```

submodule gitlink SHA 两版**逐字相同**，无 `+` 前缀 ✅；`config/`（含 `default.toml`）、`CORE_MANIFEST.toml`、`REUSE.toml`、`.etherkit/` 全部零 diff ✅；7 个 manifest 与 4 个夹具除版本行外无夹带改动（见 M9-02 取证 2）✅。

判定：**PASS**

---

## CI 总账

```
$ gh api "repos/Nolai2010/EtherOS/actions/runs?branch=feat/m9-schema-v2&per_page=10" --jq '...'
{"conclusion":"success","head_sha":"cfc4c18697fe44c1b8d6c1bcb12249ba5b1c0b35","id":39050848810,"run_attempt":1,"status":"completed",
 "display_title":"ci: M9 gate, schema v2 wording, topology smokes, fixtures"}

$ gh run view 39050848810 --repo Nolai2010/EtherOS --json jobs --jq '{count, jobs:[.jobs[]|{name,conclusion}]}'
count: 10
 spec & docs reference consistency (anti context-drift)      success
 dco (Signed-off-by on every commit, merges exempt)          success
 etherkit single-source consistency                          success
 plugin manifest schema & config consistency (M2)            success
 lint (EtherOS-owned code only; base/ structurally excluded) success
 build ToaruOS aarch64 base (upstream builder image)         success
 build ToaruOS base (upstream builder image)                 success
 license (reuse lint, submodules excluded per spec 5/risk 2) success
 vm smoke aarch64 (QEMU headless boot evidence)              success
 vm smoke (QEMU headless boot evidence)                      success

$ gh run view 39050848810 --repo Nolai2010/EtherOS --json headSha --jq .headSha
cfc4c18697fe44c1b8d6c1bcb12249ba5b1c0b35
$ git rev-parse HEAD
cfc4c18697fe44c1b8d6c1bcb12249ba5b1c0b35
```

**10/10 job 全 success** ✅；**headSha 与分支 HEAD 逐字相等** ✅（未踩"gh run list 返回陈旧 run"的坑：走的是 Actions API 按 branch 列 run + `run view` 取 `headSha` 核对）。

M9 新增 step 的 CI 实际日志（job 117448936165）：

```
Validate plugin manifests against schema v2      → plugins validation: OK
Load plan smoke (M7 load_plugins)                → LOAD PLAN OK 7
Dependency topology smoke (M9 ...)               → TOPO OK ['beta', 'alpha', 'gamma']
Dependency topology smoke (M9 ...)               → FAIL: dependency cycle detected among: a → b → a (load: EINVAL, constraint 41)
```

正例打印 `TOPO OK`、负例打印环成员且整 step 仍 success（`!` 反转断言）✅。

判定：**PASS**

---

## 已知 Minor 逐条独立核实（记档，不判 FAIL）

1. **步骤名 v1→v2 与里程碑白名单扩 M9 属计划外** —— 独立复核属实：ci.yml 除新增 M9 拓扑 step 外，另有 `Validate plugin manifests against schema v1` → `...v2` 的步骤名改动，以及 spec-consistency 白名单 `("M0"…"M8")` → `("M0"…"M9")`。二者均由控制器裁定接受。白名单扩列方向为**更严**（M9 章节原被删不红，现会红），非消音；步骤名改动纯措辞。判定：接受，不判 FAIL。
2. **`find_cycle` 多环并存时只报首个被 DFS 命中的环** —— 实现确为 DFS 取一环即返回（`tools/load_plugins.py:70-93`）。实测单环（2-环 / 3-环）成员完整、非 0 退出，判据要求（"列出环上成员"）满足；多环场景属已知限制，仍非 0 退出，不判 FAIL。
3. **跨类别依赖未禁止**（builtin 可依赖 optional，只要启用）—— 实测夹具 `optional/gamma → builtin/beta` 通过；属设计选择，不判 FAIL。
4. **历史 M4 报告 `:90` 仍嵌一处 v1 示例文本** —— 独立复核属实：`git grep '"schema_version": *"1"'` 全仓库唯一命中为 `docs/reports/2026-10-06-m4-acceptance.md:90`。按"追加不回改"处理未动；该文本在史料性报告内，不参与任何门禁断言（spec-consistency 只扫 schema 文件本体），不判 FAIL。
5. **仓库 7 个插件全无依赖，拓扑分支仓库内永远走退化路径** —— 独立复核属实：7 个 manifest 无一声明 `dependencies`，`resolve_load_order` 的拓扑分支在仓库内不被触发，只能靠夹具与 CI 覆盖。本次已用自建夹具树（含跨类别、3 节点链、2-环、3-环）补足覆盖，不判 FAIL。

---

## 口径差异与遗留

1. **M9 是有意破坏性升级，不判 FAIL** —— v2 不做双版本共存：`const` 硬切 `"2"`、全树 7 manifest + 4 夹具迁移、validator 明确拒 v1 并给迁移提示（`migrate: set "schema_version": "2" in this plugin.json`）。这是 spec §2.4「任何字段变更 = schema_version 变更」下的裁定选择。本验收**未**因"v1 不能用"判 FAIL；但"给了迁移提示"这一条已实跑验证为真（M9-02 取证 3）。
2. **M9-06「其余九 job 行为不变」的严格读法差异** —— `plugin-schema` job 是九者中唯一非对象全等的：新增一个 M9 拓扑 step + 步骤名 v1→v2。严格字面读，其"行为"确有变化；但方向为**纯增强**（无断言放宽、无 `continue-on-error`、无 suppress），且该 step 正是 M9-04 判据所要求的 CI 覆盖。按"方向只许更严"的既有惯例记为零回退，判 PASS；此处如实记档而非抹平。其余 8 个 job 对象全等。
3. **schema 锚点 1→2 属同步非消音** —— 已独立确认：断言结构（`!=` → `fails.append` → `sys.exit(1)`）一字未变、`warn` 字样零命中、未被删除；并实测漂移到 `"1"` / `"3"` 仍触发断言（M9-06 取证 3/4）。
4. **环检测归装载器不归 validator** —— 分层口径与简报一致：validator（`validate_plugins.py`）只做单 manifest 静态断言（存在性 / 自依赖 / 重复），环由 `load_plugins.py` 的 `resolve_load_order` + `find_cycle` 检测。M9-03 与 M9-04 分别按各自归属取证，未混判。
5. **本报告未登记进 `docs/index.md`** —— 验收者铁律限制改动仓库文件（唯一例外即本报告本身）。沿用 M5/M6/M7/M8 报告先例，由 M9 关门任务补登。
6. **本机 git 到 github.com 的 HTTPS 通道不可用** —— 与 M7/M8 同形态，所有远端取证改走 `gh`（`api.github.com` 可达），`gh` 一律用 `--repo Nolai2010/EtherOS`（不接受 `-C`）。本地与远端的判据均已闭环。
7. **临时 worktree 已清理** —— `git worktree add /tmp/m9acc/baseline v0.8.0-m8` 用完即 `git worktree remove` + `git worktree prune`；`git worktree list` 复原为仅 `I:/etheros`。所有夹具（`/tmp/m9acc/**`、`/tmp/m9-dep`、`/tmp/m9-cycle`）均未落进仓库，`git status --short` 除本报告外为空。

---

**总判定：M9-01 ~ M9-06 六条全部 PASS，阻塞缺陷 0；5 条已知 Minor 均为记档项（控制器已裁定或属既有设计选择），7 条口径差异已如实记档 —— 其中"破坏性升级"与"plugin-schema job 纯增强"两条是最需要终审知悉的非平凡取舍。**

**STATUS: PASS**

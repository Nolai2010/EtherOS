# M7 独立验收报告 —— Phase 2 开门（装载契约 + 门禁硬化 + 可行性调研）

- **验收者**：general-purpose-1（独立上下文，与 M7 各任务实现者 / 复审者均不同；不替实现背书，不粉饰）
- **被验对象**：分支 `feat/m7-phase2-opening`，HEAD `16dd9fb`（提交主题 `docs: Phase 2 feasibility report (aarch64 build, OVA) + index rows`）
- **区间**：`b350a34..HEAD`（M7 自主分支点起，共 8 个非合并提交）
- **仓库**：`I:/etheros`（远端 `github.com/Nolai2010/EtherOS`）
- **执行日期**：2026-10-17（本机时区；文件名沿用 M7 计划日期 2026-10-11，与判据条目对齐）
- **依据**：`docs/development/acceptance-standard.md` M7 章节（M7-01~M7-07，7a98a75 入库）+ 验收简报 `.superpowers/sdd/2026-10-05-etheros-m0m1-implementation/briefs/m7-t7-acceptance-brief.md`
- **口径**：偏严，全部实跑；只记录实测输出；M7-3/4 的 Important（cppcheck 多文件塌缩）修复 db62985 独立复核而非采信原复审结论
- **未触碰任何仓库文件**：反例与夹具全部落在 `/tmp`（副本经 `git archive` 导出，未用 worktree）；写操作仅本报告一个文件；未派子代理、未推 tag、未动 main

---

## 0. 判据存在性核验与被验对象定位

```
$ git -C I:/etheros log --oneline -1
16dd9fb docs: Phase 2 feasibility report (aarch64 build, OVA) + index rows
$ git -C I:/etheros branch --show-current
feat/m7-phase2-opening
```

HEAD 与简报所述 `16dd9fb` 一致 ✅；分支正确。

判据实存：`sed -n '/^## M7/,$p' docs/development/acceptance-standard.md` 输出 M7 章节表，M7-01~M7-07 七条编号、标准、验证方式齐备，无缺项 ✅。

**零改动文件核验**（验收者铁律的自我取证）：`git -C I:/etheros status --short` 在写完本报告前为空；本报告为本次唯一新增文件。

判定：**PASS**（判据齐备、被验对象定位准确、无越界动作）

---

## 夹带与 DCO 总检（先行：M7 跨 8 任务多 worker，最易出夹带）

### D1 全量文件清单

```
$ git -C I:/etheros diff b350a34..HEAD --stat
 .github/workflows/ci.yml                      |  45 ++++-
 CONTRIBUTING.md                               |  47 +++++
 docs/development/acceptance-standard.md       |  12 ++
 docs/index.md                                 |   4 +-
 docs/reports/2026-10-11-phase2-feasibility.md | 247 ++++++++++++++++++++++++++
 kernel/interfaces/loader-contract.md          |  72 +++++++
 kernel/interfaces/loader_if.h                 | 116 ++++++++++++
 tools/load_plugins.py                         | 124 +++++++++++
 8 files changed, 661 insertions(+), 6 deletions(-)
```

8 个文件全部对应 M7-01~06 的应动范围；`base/toaruos`、`plugins/schema/plugin.schema.json`、`config/default.toml`、`CORE_MANIFEST.toml`、既有 `tools/validate_plugins.py` / `tools/route_plugins.py` / `tools/check_kernel_boundary.py` **零出现** ✅。

### D2 逐提交范围（8 个提交，均带 Signed-off-by）

```
$ git show --stat --format='%h %s%n%(trailers:key=Signed-off-by,valueonly)' <sha>
7a98a75 docs: add M7 acceptance criteria (controller-verified)   → acceptance-standard.md（判据入库）
763905d ci: harden spec-consistency (M7-01 anchoring, empty-set) → ci.yml（M7-01）
63350fe ci: lint 空集断言 + 里程碑元组扩到 M7                    → ci.yml（M7-02）
ed799c6 docs: CONTRIBUTING.md 贡献流程 + index 登记 (M7-03)       → CONTRIBUTING.md + docs/index.md（M7-03）
ee41bf7 feat(m7): loader contract + userland load-plan generator  → ci.yml + loader-contract.md + loader_if.h + load_plugins.py（M7-04/05）
db62985 ci: fix cppcheck argv quoting exposed by second kernel header → ci.yml 1 行（M7-3/4 Important 修复）
e2af6ab docs: add active-rules.md row to related-docs table       → CONTRIBUTING.md 1 行（复审 Q2 修复）
16dd9fb docs: Phase 2 feasibility report + index rows            → docs/index.md + 可行性报告（M7-06）
```

每个提交只动其任务应动文件，无跨任务裹挟 ✅。8/8 提交 trailer 均含 `Signed-off-by: Nolai <120611751+Nolai2010@users.noreply.github.com>` ✅。

判定：**PASS**（无夹带、DCO 齐备）

---

## M7-01 spec-consistency 行首锚定 + 空候选集断言

### 实现取证（ci.yml:157-209 内联 python）

1. **行首锚定**（ci.yml:190-196）：`std_lines = ...splitlines()` 后判定 `line == f"## {m}" or line.startswith(f"## {m} ")` —— 整行等于或行首带空格前缀，`## M1+ · 占位` 二者皆不满足；
2. **空候选集断言**（ci.yml:182-183）：`if candidates < 1: fails.append(...)`，0 候选即 FAIL；
3. 里程碑元组从 M5 扩到 M7（ci.yml:194），方向更严。

### 反例实证（/tmp 副本，`git archive` 导出，未碰仓库）

```
# 反例 A：真 ## M1 头被 ## M1+ · 占位 掩盖
$ cd /tmp/m7check && sed -i 's/^## M1 /## M1+ · 占位 /' docs/development/acceptance-standard.md
$ <复跑 spec-consistency 内联 python>
acceptance-standard.md missing section: M1
EXIT=1
```

`## M1+ · 占位` 不再掩盖真 `## M1` 缺失 ✅。

```
# 反例 B：index.md 清空令候选为 0
$ printf '# index (emptied for negative test)\n' > docs/index.md
$ <复跑>
docs/index.md yielded 0 path candidates (0 backticked snippet(s) scanned); regex or index content broke
EXIT=1
```

空候选集不再静默通过 ✅。

```
# 基线（未篡改副本）
BASELINE OK: candidates=29, scanned=31
```

判定：**PASS**

---

## M7-02 lint 空集断言 + db62985 未放宽门禁独立确认

### 实现取证（ci.yml:128-148）

1. clang-format 步（ci.yml:134-136）：`FILES=$(find kernel tools plugins \( -name '*.c' -o -name '*.h' \) -type f)` → `test -n "$FILES" || { ...exit 1; }` → `xargs clang-format --dry-run --Werror`。`--Werror` 与 M5 基线逐字相同；
2. cppcheck 步（ci.yml:144-146）：`find kernel ...` → `test -n` 断言 → `xargs -d '\n' cppcheck --language=c --enable=warning --error-exitcode=1`。三个参数与 M5 基线逐字相同，无 `--suppress`；
3. pyflakes 步（ci.yml:148）与 M5 基线逐字相同；
4. find 起点限定 `kernel tools plugins` / `kernel`，结构性排除 `base/`，与 M5 注释一致。

### db62985 独立确认（不采信原复审结论）

```
$ git show db62985 -- .github/workflows/ci.yml
-          printf '%s\0' "$FILES" | xargs -0 cppcheck --language=c --enable=warning --error-exitcode=1
+          printf '%s\n' "$FILES" | xargs -d '\n' cppcheck --language=c --enable=warning --error-exitcode=1
```

仅改 xargs 分割方式；cppcheck 参数一字未动、未加 suppress、job 名未动。机理实证（/tmp/m7check，kernel/ 现有两个 .h）：

```
$ 新写法：printf '%s\n' "$FILES" | xargs -d '\n' echo "[argv]"
[argv] kernel/interfaces/loader_if.h kernel/interfaces/router_if.h      ← 两个独立 argv 项
$ 旧写法：printf '%s\0' "$FILES" | xargs -0 echo "[argv]"
[argv] kernel/interfaces/loader_if.h
kernel/interfaces/router_if.h                                            ← 塌缩成一个含换行 argv 项
```

旧写法确系"多文件塌缩"（单 argv 项内嵌换行），修复后每文件独立成项，**方向更严**：修复前第二个头文件实际上从未被cppcheck检查。✅

### 空集反例（/tmp 空目录）

```
$ mkdir -p /tmp/m7empty
$ FILES=$(find /tmp/m7empty \( -name '*.c' -o -name '*.h' \) -type f); test -n "$FILES" || { echo "EMPTY-SET ASSERT FIRED (would exit 1)"; exit 1; }
EMPTY-SET ASSERT FIRED (would exit 1)
EXIT=1
```

目标为空不再 exit 0 静默通过 ✅。

判定：**PASS**（空集断言两步俱全；db62985 未放宽任何门禁参数）

---

## M7-03 CONTRIBUTING.md + index 登记

### 三段齐备（实读 CONTRIBUTING.md，47 行）

1. **DCO**（§1，:6-17）：`git commit -s -m "主题一行,不超过 72 字符"`；CI dco job 逐条校验；**merge commit 豁免如实写入**（:15-16）且注明"非合并提交一律不豁免"；漏签补救 `git rebase --signoff` 且告诫勿强推；
2. **分支与 tag 惯例**（§2，:19-25）：每里程碑短命分支 `feat/m<N>-<slug>`；收官 `git merge --no-ff`；annotated tag `v0.x.0-mN` 与 release.yml 行为；
3. **验收闭环**（§3，:27-37）：Builder ≠ Reviewer 引 `docs/builder-reviewer-separation.md`；禁止自评（没跑的写"未验证"）；独立验收报告入 `docs/reports/`；验收未过不合门不打 tag；教训沉淀路径。

### 引用路径逐一核实（/tmp 副本实测）

```
OK  docs/builder-reviewer-separation.md
OK  docs/reports/2026-10-06-m6-acceptance.md
OK  docs/development/acceptance-standard.md
OK  docs/experience-library/lessons.md
OK  docs/experience-library/active-rules.md
OK  AGENTS.md
```

§3 引用 6/6 存在 ✅。

### index 登记

`docs/index.md:35` 登记 `../CONTRIBUTING.md`（M7-03 行）。双基准命中实证：

```
docs-relative exists: True      ← 命中（spec-consistency 检查的 or 语义）
root-relative exists: False
```

基线复跑 `BASELINE OK: candidates=29`（该行无空白、计入候选且不悬空）✅。

### 已知 Minor ③ 核实

M7-3/4 复审 Q2"相关文档表漏列 active-rules.md"：**确已修复**——`CONTRIBUTING.md:47` 列出 `docs/experience-library/active-rules.md`（提交 e2af6ab，1 行增量）✅。

判定：**PASS**

---

## M7-04 装载契约（格式无关 + not compiled）

### 实现取证（实读两文件）

1. **not compiled 声明**：`loader_if.h:7-10` "contract stub, not compiled ... MUST NOT be referenced by any build system"；`loader-contract.md:3` "均为**契约表达**,不参与任何构建"；
2. **格式无关**：`loader_if.h:12-17` "Format-agnostic by construction ... never the concrete structure of any application format"；契约 §1 铁律（不见任何具体应用格式的结构/解析/翻译）；
3. **格式字面量零命中**：直查 `grep -nE '\.(ipa|exe|apk|dll|so|app|deb|rpm)'` 两文件 → 零命中；
4. **守卫实跑**（kernel/ 白名单 + 格式字面量 + manifest 契约对齐，M4 起覆盖本条）：

```
$ python3 tools/check_kernel_boundary.py
kernel boundary: OK
EXIT=0
```

判定：**PASS**

---

## M7-05 用户态装载器（重点条目）

### 正例实跑

```
$ python3 tools/load_plugins.py            （EXIT=0，输出合法 JSON）
status: 'plan-only'
contract: kernel/interfaces/loader-contract.md | stage: M7-loader-plan
top-level keys == ['contract', 'enabled', 'load_order', 'notes', 'skipped', 'stage', 'status']
TOP KEYSET MATCH: True          （与契约 §2 七键逐字一致）
ALL ENTRY KEYSETS MATCH: True   （enabled[] 六键 {id,type,category,payload,container,capabilities}）
ALL SKIP KEYSETS MATCH: True    （skipped[] {id,reason}；本轮 0 skipped）
enabled ids: ['files', 'mon', 'settings', 'shell', 'etheros-agent-rules', 'douyin', 'hello-plugin']
enabled categories: ['builtin','builtin','builtin','builtin','dev','optional','optional']
CATEGORY ORDER builtin->dev->optional: True
load_order == enabled ids: True
```

- builtin 四个（files/mon/settings/shell）+ dev 一个（etheros-agent-rules）+ optional 两个（douyin/hello-plugin，均列于 config enabled）✅
- 隐式启用语义与 validator 同口径（builtin/dev 不列 enabled 亦入计划）✅
- `notes` 四条如实："未真正装载、未启动任何插件(约束 29)"；"启动期装载……属后续里程碑"；"schema v1 无 dependencies 字段……load_order 为目录序遍历序"；格式无关声明 ✅

### 契约键名集合比对（脚本化，非肉眼）

比对基准取自 `loader-contract.md` §2 三张表，输出键集合逐字相等（见上 TOP/ENTRY/SKIP KEYSET MATCH 三行全 True）✅。

### 负例（4 条，夹具 /tmp/fix，均非 0 退出且不输出计划 JSON）

```
(a) bogus enabled id:
FAIL: bogus.toml [plugins] enabled id 'no-such-plugin' matches no manifest under plugins/{builtin,dev,optional} (load: ENOENT)
EXIT=1
(b) 插件目录缺 plugin.json:
FAIL: .../optional/hello-plugin/plugin.json plugin directory without plugin.json (cannot plan a load entry)
EXIT=1
(c) manifest payload 悬空:
FAIL: shell payload 'nonexistent-payload.bin' does not resolve to an existing file (load: EINVAL)
EXIT=1
(d) plugin.json JSON 非法:
FAIL: .../optional/douyin/plugin.json unreadable/invalid JSON: Expecting property name enclosed in double quotes: line 1 column 3 (char 2)
EXIT=1
```

四条 stdout 均只有 FAIL 行、无计划 JSON 冒充成功 ✅。

### 红线扫描（不实表述）

```
$ grep -rn "已装载|已启动|已运行|已加载" --include="*.{py,h,md}" .
kernel/interfaces/loader-contract.md:14: ...**不得**出现"已装载/已启动/已运行"之类表述。
```

全仓唯一命中为契约 §0 的**禁令自引**（"不得出现"否定语境），属简报明示的良性命命；`load_plugins.py` 与 `loader_if.h` 本身零命中（其诚实声明用"未真正装载/未启动"否定式）✅。

判定：**PASS**

---

## M7-06 可行性调研（未落地是判据一部分）

### 报告实读（docs/reports/2026-10-11-phase2-feasibility.md，247 行）

1. **议题一（aarch64）结论可执行**："**建议做**（Phase 2 清偿，分两步，只动 ci.yml）"——证据清偿（build-aarch64 job 复刻配方换镜像/脚本）+ 可启动性背书（vm-smoke-aarch64，断言字符串同源 `apps/login.c:86`），附成本表（≈+4-6 min 机器时/push、人力半天内）与 6 条依据引用；
2. **议题二（OVA）结论可执行**："**建议不做**（维持 M6 差异点 8 降级）"——附三条触发条件与最小实现路径备查，附成本表（实现半天、Release +8MB、双 hypervisor 验证长期债）；
3. **诚实边界**：专列「未能证实项」5 条（aarch64 镜像可拉取性、TCG 冒烟时长、VMware 导入体验、上游工具链脚本负面事实、是否存在等 OVA 用户），查不到的明说"未能证实"，未编造 ✅；
4. **未落地实现**（用 diff 证明，不评结论好坏）：

```
$ git diff v0.6.0-m6..HEAD --stat -- .github/workflows/
 .github/workflows/ci.yml | 45 ++++++++++++++++++++++++++++++++++++++-----
 1 file changed, 40 insertions(+), 5 deletions(-)
$ git diff v0.6.0-m6..HEAD -- .github/workflows/ci.yml | grep -E '^[+-]' ...
+ Load plan smoke (M7 load_plugins)          ← ee41bf7（M7-05）
+ M7-3 空集断言（clang-format）               ← 63350fe（M7-02）
+ M7-3 空集断言（cppcheck）+ xargs -d '\n'    ← 63350fe / db62985（M7-02/修复）
+ M7-01 行首锚定 + 空候选集断言                ← 763905d（M7-01）
$ grep -niE 'aarch|arm64|ova|qemu-system-aarch' .github/workflows/ci.yml .github/workflows/release.yml
release.yml:31: OVA deferred to Phase 2, 差异点 8     ← M6 遗留注释（零 diff 文件内），非本次改动
```

workflows 全量 diff 仅 ci.yml 的 4 处 M7 既有改动，**无新增 aarch64 job、无 release 产物逻辑变更**；release.yml 中 OVA 仅存于 M6 时已有的降级注释 ✅。

判定：**PASS**

---

## M7-07 旧门禁零回退

```
$ git diff v0.6.0-m6..HEAD -- .github/workflows/release.yml | wc -l
0
```

release.yml 零 diff ✅（tag 触发 `tags: ['v*']` / `dry_run` / `if: github.event_name == 'push'` / `--prerelease` 四项 M6 行为因零 diff 而原样，grep 实测四行俱在）。

ci.yml job 名基线比对（pyyaml 解析，非肉眼）：

```
M5 baseline jobs: ['etherkit-consistency', 'plugin-schema', 'license', 'dco', 'lint', 'spec-consistency', 'build', 'vm-smoke']
HEAD jobs       : ['etherkit-consistency', 'plugin-schema', 'license', 'dco', 'lint', 'spec-consistency', 'build', 'vm-smoke']
COUNT: 8 -> 8 | NAMES IDENTICAL: True
```

八 job、名称与顺序与 M5 基线逐一相同 ✅。

判定：**PASS**

---

## CI 总账

```
$ gh --repo Nolai2010/EtherOS run list --branch feat/m7-phase2-opening --limit 3
[{"conclusion":"success","headSha":"16dd9fb1d40edf236fc2cfd52babb801cef4f4ec","databaseId":39032538853,...}]
$ gh --repo Nolai2010/EtherOS run view 39032538853 --json jobs
 success  license (reuse lint, submodules excluded per spec 5 / risk 2)
 success  spec & docs reference consistency (anti context-drift)
 success  etherkit single-source consistency
 success  build ToaruOS base (upstream builder image)
 success  dco (Signed-off-by on every commit, merges exempt)
 success  lint (EtherOS-owned code only; base/ structurally excluded)
 success  plugin manifest schema & config consistency (M2)
 success  vm smoke (QEMU headless boot evidence)
job count: 8
```

最新 run（39032538853）headSHA `16dd9fb` 与分支 HEAD 一致，八 job 全 success ✅。

判定：**PASS**

---

## 已知 Minor 逐条独立核实（记档，不判 FAIL）

1. **`load_plugins.py:36` `sorted()` 死排序**（build_plan 已重排）——独立复现属实：`scan_plugins` 内 `sorted(p for p in base.iterdir() ...)` 的序被 `build_plan:72` 的 `sorted(...)` 覆盖。无害，赞成披露。
2. **enabled 重复 id 不拒绝**——独立复现属实：`build_plan:87-89` 只查树中命中、不查重复；集合语义下无害（同 id 两条 enabled 仍只出一份计划）。赞成披露。
3. **active-rules.md 漏列**——**已修复**（e2af6ab，CONTRIBUTING.md:47），见 §M7-03。

---

## 口径差异与遗留

1. **本报告未登记进 `docs/index.md`**：验收者铁律限制改动仓库文件（唯一例外即本报告本身）。沿用 M5/M6 报告先例，由关门任务补登一行。建议文本：
   ```
   | docs/reports/2026-10-11-m7-acceptance.md | M7 独立验收报告（7/7 PASS；含 db62985 未放宽门禁独立确认、4 条负例实证、口径差异 1 条记档） |
   ```
   经本机校验：该引用在 spec-consistency 双基准检查下按 docs/ 相对基准可解析，登记后不会悬空。
2. **反例执行环境说明**：所有反例在 `/tmp` 副本/夹具上完成（`git archive` 导出，非 worktree，不写仓库 `.git`）；夹具树因 `etheros-agent-rules` 的 payload 为仓库相对路径（`../../../.etherkit/AGENTS.md`），补拷 `.etherkit/` 后自洽——此点为夹具环境细节，不影响仓库内正例（正例在仓库内实跑通过）。
3. **cppcheck 修复的"更严"定性**：db62985 修复前第二个内核头（router_if.h）实际从未进入 cppcheck argv（塌缩为单项），修复后两颗头均受检——本次验收以 echo 实证 argv 分割确认该机理，而非采信提交自述。
4. **cli.yml lint job 无本机实跑**：本机无 cppcheck/clang-format（`which` 零命中），lint 全绿证据取 CI run 39032538853 的 lint job success；argv 行为以 echo 等价实证。
5. **装载"未落地"边界**：loader_if.h 的 `plan_load` 为声明式契约桩（不被构建），load_plugins.py 为宿主侧计划生成器；两者均不构成运行期装载——与 M7-05 判据"如实声明 stub"一致，不构成"偷渡实现"。

---

**STATUS: PASS（M7-01 ~ M7-07 七条全部 PASS；夹带/DCO/CI 总账全过；阻塞缺陷数 0；遗留均为记档项，交控制器/关门任务裁量）**

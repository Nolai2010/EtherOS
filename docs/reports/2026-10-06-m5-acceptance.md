# M5 独立验收报告 —— CI 点亮（spec §5 六项补齐 → 八 job 全绿）

- **验收者**：acceptance-checker（独立上下文，与 M5 实现者不同；Builder≠Reviewer）
- **被验对象**：分支 `feat/m5-ci`，HEAD `85c5af9f6936e1d955b36083b42cf522d44acdea`（`85c5af9`，提交主题 `ci(dco): use PR event SHAs instead of origin/<base_ref>`）
- **仓库**：`I:/etheros`（远端 `github.com/Nolai2010/EtherOS`）
- **执行日期**：2026-10-11（本机时区；文件名沿用 M5 计划日期 10-06，与 M2/M3/M4 验收报告同系列）
- **依据**：`docs/development/acceptance-standard.md` M5 章节（M5-01~M5-07）+ spec `spec/2026-10-05-etheros-dev-policy.md` §5 + 验收简报 `m5-t6-acceptance-brief.md`（含控制器三条预裁定口径差异）
- **口径**：偏严，全部实跑；只记录实测输出，不接受口头声明。Python 解释器统一 `C:/Users/JunYa/.workbuddy/binaries/python/versions/3.13.12/python.exe`；`gh` 统一 `--repo Nolai2010/EtherOS`
- **工作树**：验收前 `git status --short` 为空；反例注入（4 组，涉及 4 个文件）全部 `git checkout --` 还原，验收后 `git status --short` 复验为空（见 M5-04「还原核验」）
- **未触碰任何仓库文件**：本报告为本次唯一新增；反例脚本落在 `%TEMP%/m5acc/spec_check.py`，未落进仓库

---

## 0. 判据存在性核验

命令：

```
$ sed -n '73,81p' docs/development/acceptance-standard.md
```

证据（M5 章节头与七条编号实存）：

```
## M5 · CI 点亮（spec §5 六项补齐 → 八 job 全绿）
| M5-01 | license job 存在且绿：reuse lint 通过 ... 含"base/ 恒为 submodule"防御断言 | CI 绿 + 本地（或 CI）reuse lint 证据 |
| M5-02 | dco job 存在且绿：PR 与 push 双事件口径 ... （merge commit 豁免记档） | CI 绿 + 正/反例证据 |
| M5-03 | lint job 存在且绿：clang-format --dry-run（自有 C）+ cppcheck（kernel/）+ pyflakes（tools/*.py 等）全过；扫描结构性排除 base/ | CI 绿 |
| M5-04 | spec-consistency job 存在且绿：docs/index.md 悬空检查 + acceptance-standard 里程碑章节存在性 + .etherkit/AGENTS.md spec 引用存在性 ... | CI 绿 |
| M5-05 | ci.yml 达八 job（etherkit-consistency/plugin-schema/license/dco/lint/spec-consistency/build/vm-smoke），push/PR 全绿 | `gh run view` job 清单 + 全 success |
| M5-06 | 逐 job 递进纪律：license→dco→lint→spec-consistency 顺序，每 job 先本地模拟再 CI 实跑、绿一上一下一 | 台账/run 序列证据 |
| M5-07 | 旧四 job 零回退：etherkit-consistency/plugin-schema/build/vm-smoke 行为与 job 名不变 | CI 绿 + ci.yml diff 复核 |
```

判定：**PASS**（章节与七条编号实存，无缺项）

---

## M5-01 license job 存在且绿

### 结构取证（ci.yml 现版本）

```
$ sed -n '68,79p' .github/workflows/ci.yml
  license:
    name: license (reuse lint, submodules excluded per spec 5 / risk 2)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Defensive assert base/toaruos stays a submodule
        run: git config -f .gitmodules --get submodule.base/toaruos.path | grep -qx "base/toaruos"
      - name: reuse lint (default excludes submodules; upstream licenses via NOTICE & docs/license-inventory.md)
        run: |
          python3 -m pip install --quiet reuse
          reuse --version
          reuse lint
```

- `reuse lint` **未传 `--include-submodules`**（见 §红线 grep，新增四 job 区间内该字符串零命中）。
- 防御断言在 `ci.yml:73-74`，本地复现实跑：

```
$ git config -f .gitmodules --get submodule.base/toaruos.path | grep -qx "base/toaruos"
base/toaruos submodule assert OK
```

### 本机实跑复核（不依赖 CI）

```
$ C:/Users/JunYa/.workbuddy/binaries/python/versions/3.13.12/python.exe -m reuse --version
python -m reuse, version 6.2.0

$ C:/Users/JunYa/.workbuddy/binaries/python/versions/3.13.12/python.exe -m reuse lint
# SUMMARY
* Bad licenses: 0
* Deprecated licenses: 0
* Licenses without file extension: 0
* Missing licenses: 0
* Unused licenses: 0
* Used licenses: CC0-1.0, MIT
* Read errors: 0
* Invalid SPDX License Expressions: 0
* Files with copyright information: 164 / 164
* Files with license information: 164 / 164

Congratulations! Your project is compliant with version 3.3 of the REUSE Specification :-)
```

### CI 取证

```
$ gh --repo Nolai2010/EtherOS run view 38071828408 --json jobs --jq '.jobs[]|"\(.name) | \(.conclusion)"'
license (reuse lint, submodules excluded per spec 5 / risk 2) | success
```

判定：**PASS** —— 非"CI 配置侥幸绿"：本机 reuse 6.2.0 实跑 164/164 合规，与 CI 结论互证。

---

## M5-02 dco job 存在且绿（PR / push 双事件）

### 结构取证（ci.yml 现版本）

```
$ sed -n '81,110p' .github/workflows/ci.yml
  dco:
    name: dco (Signed-off-by on every commit, merges exempt)
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }                       # ← 全历史 fetch
      - name: Check Signed-off-by
        run: |
          set -e
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            RANGE="${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }}"
            COMMITS=$(git log --no-merges --format=%H "$RANGE")
          else
            BEFORE="${{ github.event.before }}"
            if [ -z "$BEFORE" ] || [ "$BEFORE" = "0000...0000" ]; then
              COMMITS=$(git log --no-merges --format=%H)   # 新分支首推：全历史
            else
              COMMITS=$(git log --no-merges --format=%H "$BEFORE..${{ github.event.after }}")
            fi
          fi
          fail=0
          for sha in $COMMITS; do
            git log -1 --format=%B "$sha" | grep -q "Signed-off-by:" || { echo "::error::..."; fail=1; }
          done
          echo "checked ... non-merge commit(s)"
          exit $fail
```

要素逐项：`fetch-depth: 0` ✅（ci.yml:86）；`--no-merges`（merge 豁免）✅（ci.yml:96 与 102 双分支均有）；pull_request 事件分支 ✅（ci.yml:90-96）；push 事件分支含首推零 SHA 兜底 ✅（ci.yml:97-103）；`exit $fail` 真失败退出 ✅（ci.yml:110）。

### 本地脚本级模拟（push 分支口径）

```
$ for sha in $(git log --no-merges --format=%H v0.4.0-m4..HEAD); do
    git log -1 --format=%B "$sha" | grep -q "Signed-off-by:" && echo "OK   $sha" || echo "MISS $sha"; done
OK   85c5af9f6936e1d955b36083b42cf522d44acdea
OK   ec611a4fa28c9b7c40114386bb0a802c56152582
OK   a9f2c6a53df743a06c08d94830f956de24b3fa82
OK   5973940726b1ec020756e6414724ec5559a44083
OK   0378cf74796f45e16a806a6d087cc2dd4ce18086
OK   0965ff8e7b27f4d04d194efc0450de0bf917456c
OK   8491618d7929d1669d336c80d5710cae017d6b7c
OK   1c7c2827e4f491884d89be96d17fa7eefbd93e87
OK   db98f73308c59b73838872983ab995aa02a2743e
fail=0
```

merge 豁免口径的现实必要性（证明 `--no-merges` 不是空配置）：

```
$ git log --merges --oneline -3
08e3fea Merge feat/m4-builtin: M4 builtin plugin repatriation
d229d04 Merge feat/m3-compat: M3 compat stub minimal core
633e029 Merge feat/m2-plugins: M2 plugin schema minimal core
```

（`v0.4.0-m4..HEAD` 范围内 merge 提交数 0，故 push 口径下豁免不触发；历史中确存在 merge 提交。）

### CI 取证

run 38068373204（dco 首次上线）至 38071828408，`dco (Signed-off-by on every commit, merges exempt)` 连续 success。

判定：**PASS-with-note** —— 结构性双事件口径齐备、push 口径本地脚本级实证通过、CI 连续绿。note：**PR 事件分支未做真机实证**（本机代理拦截 POST，`gh pr create` / REST `POST /pulls` / 直连 curl 均不可达），仅结构性实现 + 本地脚本级模拟，详见口径差异 1。

---

## M5-03 lint job 存在且绿

### 结构取证（ci.yml 现版本）

```
$ sed -n '112,131p' .github/workflows/ci.yml
  lint:
    name: lint (EtherOS-owned code only; base/ structurally excluded)
    steps:
      - uses: actions/checkout@v4
      - name: Install tools
        run: sudo apt-get update && sudo apt-get install -y --no-install-recommends clang-format cppcheck && python3 -m pip install --quiet pyflakes
      - name: clang-format (C under kernel/ tools/ plugins/ only)
        run: find kernel tools plugins \( -name '*.c' -o -name '*.h' \) -type f | xargs -r clang-format --dry-run --Werror
      - name: cppcheck (kernel/)
        run: find kernel \( -name '*.c' -o -name '*.h' \) -print0 | xargs -0 -r cppcheck --language=c --enable=warning --error-exitcode=1
      - name: pyflakes (python tools)
        run: python3 -m pyflakes tools/*.py plugins/compat/stub-runtime/*.py
```

要素逐项：`find kernel tools plugins` 起点 → base/ 结构性排除 ✅（ci.yml:123、129、131 三处起点均不含 base/）；`clang-format --dry-run --Werror` ✅（`--Werror` 在位，未被删）；`cppcheck --error-exitcode=1` ✅（未被放宽、未加 `--suppress`，见 ci.yml:127-128 注释与 §红线 grep）；pyflakes ✅（ci.yml:131）；**无 clang-tidy**（差异点 4 已裁定省略，不计缺陷）。

### 扫描集实测

```
$ find kernel tools plugins \( -name '*.c' -o -name '*.h' \) -type f
kernel/interfaces/router_if.h
$ find kernel tools plugins \( -name '*.c' -o -name '*.h' \) -type f | wc -l
1
$ ls tools/*.py plugins/compat/stub-runtime/*.py
plugins/compat/stub-runtime/translator.py
tools/check_kernel_boundary.py
tools/route_plugins.py
tools/validate_plugins.py
```

### 本机可复现部分实跑

```
$ C:/Users/JunYa/.workbuddy/binaries/python/versions/3.13.12/python.exe -m pyflakes tools/*.py plugins/compat/stub-runtime/*.py
pyflakes exit=0          # 无输出 = 零告警
```

clang-format / cppcheck 本机无工具链（`which clang-format cppcheck` → not found），**本机未取证**；CI 侧实证见下。

### CI 取证

```
$ gh --repo Nolai2010/EtherOS run view 38069840261 --json jobs --jq '...'
lint (EtherOS-owned code only; base/ structurally excluded) | success
$ gh --repo Nolai2010/EtherOS run view 38071828408 --json jobs --jq '...'
lint (EtherOS-owned code only; base/ structurally excluded) | success
```

配套基线新增 `.clang-format`（16 行，LLVM + IndentWidth 4 / ColumnLimit 100 / `DeriveLineEnding: true`），`kernel/interfaces/router_if.h` 的 5 行排版改动即为该基线的产物（`git diff v0.4.0-m4..HEAD -- kernel/interfaces/router_if.h`，纯宏对齐与签名合行，无语义变更）。

判定：**PASS** —— 字面达成（三工具配置齐备、base/ 结构性排除、CI 绿）。信号厚度声明见口径差异 2。

---

## M5-04 spec-consistency job 存在且绿

### 结构取证（ci.yml 现版本，内联 python 四段检查）

- (a) `docs/index.md` 悬空检查：双基准（docs/ 相对 → 仓库根相对），含空白的反引号片段按命令行过滤（ci.yml:148-156）
- (b) acceptance-standard 里程碑章节头 M0..M5 存在性（ci.yml:157-161）
- (c) `.etherkit/AGENTS.md` 的 `spec/*.md` 引用存在性（ci.yml:162-166）
- (d) `plugin.schema.json` 的 `schema_version.const == "1"` 锚点（ci.yml:167-170）

分工记档：ci.yml:134-135 明示「etherkit-consistency 管生成物漂移/slogan/make check/index 存在性（test -f）；本 job 管 index 每条被引文档的真实悬空 + spec 锚点 + schema 版本锚点。两者无重复门禁」。对照 `ci.yml:25-26`（etherkit-consistency 仅 `test -f docs/index.md`，不查悬空），**确无重复门禁**。

### 独立取证一：抽出内联 python 本机实跑

把 ci.yml:142-174 的内联脚本按 YAML 缩进去缩进后抽出到 `%TEMP%/m5acc/spec_check.py`（1543 字节，未落进仓库），在本机仓库根执行：

```
$ C:/Users/JunYa/.workbuddy/binaries/python/versions/3.13.12/python.exe %TEMP%/m5acc/spec_check.py
spec consistency: OK
exit=0
```

### 独立取证二：四组自造反例（验完全部还原）

| # | 反例操作 | 期望 | 实测输出 | exit |
|---|---|---|---|---|
| 1 | `plugin.schema.json` 的 `schema_version.const` 改为 `"2"` | FAIL | `plugin.schema.json schema_version anchor drifted from "1"` | 1 |
| 2 | `docs/index.md` 追加悬空引用 `` `docs/definitely-missing-doc.md` `` | FAIL | `docs/index.md references missing doc: docs/definitely-missing-doc.md` | 1 |
| 3a | 删除 `acceptance-standard.md` 的 `## M4 · ...` 章节头（唯一子串） | FAIL | `acceptance-standard.md missing section: M4` | 1 |
| 3b | 删除 `acceptance-standard.md` 的 `## M1 · 底座基线(归档...)` 章节头 | 见下 | `spec consistency: OK`（**放行**） | 0 |
| 4 | `.etherkit/AGENTS.md` 追加 `` `spec/no-such-spec-file.md` `` | FAIL | `.etherkit/AGENTS.md references missing spec: spec/no-such-spec-file.md` | 1 |

反例 3b 说明（已知 Minor 实测复现，非本次新发现）：判据用子串 `f"## {m}" not in std`，而 `acceptance-standard.md:30` 存在 `## M1+ · 占位`，故真实 `## M1` 章节被删也会被 `"## M1" in std` 放过。实测 3b exit=0 确证该盲区存在。控制器已裁定记为遗留、不阻塞。

### 还原核验

```
$ git checkout -- plugins/schema/plugin.schema.json docs/index.md docs/development/acceptance-standard.md .etherkit/AGENTS.md
$ git status --short
（空）
$ C:/Users/JunYa/.workbuddy/binaries/python/versions/3.13.12/python.exe %TEMP%/m5acc/spec_check.py
spec consistency: OK
exit=0
```

### CI 取证

run 38070906802 与 38071828408：`spec & docs reference consistency (anti context-drift) | success`。

判定：**PASS** —— 本机正例通过 + 4 组反例命中（1/2/3a/4 正确 FAIL），非"脚本恒真"；3b 盲区按裁定记档。

---

## M5-05 ci.yml 达八 job，push/PR 全绿

run 序列（最新在前）：

```
$ gh --repo Nolai2010/EtherOS run list --branch feat/m5-ci --limit 12 --json databaseId,displayTitle,conclusion,createdAt,event
38071828408  ci(dco): use PR event SHAs instead of origin/<base_ref>        success  2026-10-10T17:27:43Z  push
38070906802  ci: add spec-consistency job (index dangling + spec anchors)   success  2026-10-10T17:14:14Z  push
38069840261  ci: cppcheck explicit file list (kernel/ dir form found no files) success 2026-10-10T16:58:42Z push
38069483688  ci: add lint job (clang-format + cppcheck + pyflakes, own code only) failure 2026-10-10T16:53:23Z push
38068373204  ci: add dco job (PR + push dual-event, merge commits exempt)   success  2026-10-10T16:36:47Z  push
38067370084  chore: add CC0-1.0 license text (REUSE compliance, M5 license job) success 2026-10-10T16:22:03Z push
38066638828  ci: add license job (reuse lint, plan A)                       failure  2026-10-10T16:11:18Z  push
```

最新 run **38071828408** 的八个 job 名字与 conclusion 逐条（`gh run view 38071828408 --json jobs`）：

| # | job name | conclusion |
|---|---|---|
| 1 | etherkit single-source consistency | success |
| 2 | plugin manifest schema & config consistency (M2) | success |
| 3 | license (reuse lint, submodules excluded per spec 5 / risk 2) | success |
| 4 | dco (Signed-off-by on every commit, merges exempt) | success |
| 5 | lint (EtherOS-owned code only; base/ structurally excluded) | success |
| 6 | spec & docs reference consistency (anti context-drift) | success |
| 7 | build ToaruOS base (upstream builder image) | success |
| 8 | vm smoke (QEMU headless boot evidence) | success |

job 数 = 8 ✅，八个名字与标准 M5-05 列举的 `etherkit-consistency / plugin-schema / license / dco / lint / spec-consistency / build / vm-smoke` 一一对应（CI 展示名为各 job 的 `name:` 字段）✅，全 success ✅。

判定：**PASS-with-note** —— push 事件八 job 全绿实证；note：**PR 事件无 run 可取证**（该分支 7 个 run 全为 `push` 事件，本机亦无法发起 PR，见口径差异 1），故"push/PR 全绿"中的 PR 半句未获实证。

---

## M5-06 逐 job 递进纪律

实测 run 序列（按时间升序）与 job 数 / 结论：

| 序 | run | 触发提交主题 | job 数 | 结论 | 当次新增/变化 |
|---|---|---|---|---|---|
| 1 | 38066638828 | ci: add license job (reuse lint, plan A) | 5 | **failure** | +license（license 红） |
| 2 | 38067370084 | chore: add CC0-1.0 license text | 5 | success | license 修绿 |
| 3 | 38068373204 | ci: add dco job (PR + push dual-event...) | 6 | success | +dco（一次即绿） |
| 4 | 38069483688 | ci: add lint job (clang-format + cppcheck + pyflakes) | 7 | **failure** | +lint（cppcheck 目录形式红） |
| 5 | 38069840261 | ci: cppcheck explicit file list | 7 | success | lint 修绿 |
| 6 | 38070906802 | ci: add spec-consistency job | 8 | success | +spec-consistency（一次即绿） |
| 7 | 38071828408 | ci(dco): use PR event SHAs instead of origin/<base_ref> | 8 | success | dco PR 分支口径加固 |

形态核对：job 加入顺序 **license → dco → lint → spec-consistency**，与标准要求的顺序逐字一致 ✅；每次只加一个 job、绿灯后再上下一个（run 1 红 → run 2 绿后才加 dco；run 4 红 → run 5 绿后才加 spec-consistency）✅。

「先本地模拟再 CI 实跑」证据：
- license：本机 reuse 6.2.0 lint 164/164 合规（本报告 M5-01 实跑）✅
- spec-consistency：本机抽出内联脚本正例 + 4 组反例（本报告 M5-04 实跑）✅
- lint：本机仅复现 pyflakes（exit 0）；clang-format / cppcheck 本机无工具链，**未取证** ❌
- dco：本机脚本级模拟 push 口径 9/9 Signed-off-by ✅

判定：**PASS-with-note** —— 递进形态与顺序在 run 序列上确凿；note：lint 的「本地模拟」环节本机因缺 clang-format/cppcheck 无法复现，仅由 CI 内 run 4 红 → run 5 绿的迭代间接取证。

---

## M5-07 旧四 job 零回退

```
$ git diff v0.4.0-m4..HEAD -- .github/workflows/ci.yml
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 3a0b31e..ad680d7 100644
@@ -65,6 +65,114 @@ jobs:
+  license:
...（+108 行，全部为 license / dco / lint / spec-consistency 四 job 的新增块）
   build:
     # 上游官方构建路径:toaruos/build-tools 镜像自带预构建工具链 /root/gcc_local,
```

- diff 形态为**单一 hunk、纯插入**：`+108 / -0`，无任何删除行 → etherkit-consistency / plugin-schema / build / vm-smoke 四个 job 零删除 ✅
- 行号位移仅来自插入（hunk 头 `@@ -65,6 +65,114 @@`）✅
- run 38071828408 中四 job 仍以原名出现且全 success：`etherkit single-source consistency` / `plugin manifest schema & config consistency (M2)` / `build ToaruOS base (upstream builder image)` / `vm smoke (QEMU headless boot evidence)` ✅

全量改动清单（确认无夹带无关文件）：

```
$ git diff v0.4.0-m4..HEAD --stat
 .clang-format                           |  16 +++++
 .github/workflows/ci.yml                | 108 ++++++++++++++++++++++++++++
 LICENSES/CC0-1.0.txt                    | 121 ++++++++++++++++++++++++++++++++
 docs/development/acceptance-standard.md |  12 ++++
 kernel/interfaces/router_if.h           |  15 ++--
 5 files changed, 263 insertions(+), 9 deletions(-)
```

五个文件全部为 M5 直接产物：`.clang-format`（lint 基线）、`ci.yml`（四 job）、`LICENSES/CC0-1.0.txt`（license 合规）、`acceptance-standard.md`（+12 为 M5 章节判据本身）、`kernel/interfaces/router_if.h`（clang-format 基线产物）。**无夹带** ✅

判定：**PASS** —— 另按控制器提示确认：dco job 在验收前由 `85c5af9` 修复（PR 分支改用 `pull_request.base.sha..head.sha`）属 M5 新增 job 的自身迭代，**不计入 M5-07 回退**。

---

## 门禁消音反向检查（红线）

仅在**新增四 job 区间**（ci.yml 第 68–174 行）内 grep：

```
$ sed -n '68,174p' .github/workflows/ci.yml | grep -nE '\|\| true|continue-on-error|set \+e|exit 0|--include-submodules|--error-exitcode|--Werror'
56:        run: find kernel tools plugins \( -name '*.c' -o -name '*.h' \) -type f | xargs -r clang-format --dry-run --Werror
61:        # 未放宽 --error-exitcode,未加 --suppress 掩盖真实告警。
62:        run: find kernel \( -name '*.c' -o -name '*.h' \) -print0 | xargs -0 -r cppcheck --language=c --enable=warning --error-exitcode=1
```

命中判读（**全部为"在位"证据，非消音**）：

| 红线项 | 结果 |
|---|---|
| `\|\| true` | 区间内零命中 ✅ |
| `continue-on-error` | 区间内零命中 ✅ |
| `set +e` | 区间内零命中（仅有 `set -e`，方向相反）✅ |
| `exit 0` | 区间内零命中 ✅ |
| 被删的 `--Werror` | 未删，ci.yml:123 在位 ✅ |
| 被放宽的 `--error-exitcode` | 未放宽，`--error-exitcode=1` 在位（ci.yml:129）✅ |
| 被加的 `--include-submodules` | 零命中，license 未加 ✅ |

对照：全文 grep 命中的 `|| true` 位于 ci.yml:34（etherkit slogan 守卫）、196/270-277（build/vm-smoke）、290（vm-smoke），`exit 0` 位于 ci.yml:286（vm-smoke 断言成功路径）——**均在既有四 job 内，M5 未触碰，按裁定不计**。

判定：**PASS** —— 新增四 job 无任何门禁消音。

---

## 结论

| 编号 | 判定 |
|---|---|
| M5-01 license job（reuse lint + submodule 防御断言） | PASS |
| M5-02 dco job（PR/push 双事件 + merge 豁免） | PASS-with-note |
| M5-03 lint job（clang-format/cppcheck/pyflakes + base/ 排除） | PASS |
| M5-04 spec-consistency（index 悬空 + 章节头 + spec 锚点 + schema 锚点） | PASS |
| M5-05 八 job 全绿 | PASS-with-note |
| M5-06 逐 job 递进纪律 | PASS-with-note |
| M5-07 旧四 job 零回退 | PASS |
| 门禁消音红线检查 | PASS |

**总计：标准条目 M5-01 ~ M5-07 共 7 条，7/7 PASS（其中 3 条 PASS-with-note）；红线检查 1/1 PASS。阻塞缺陷数 0。**

---

## 口径差异与遗留

1. **PR 事件无法真机实证 → M5-02 / M5-05 记 note**（控制器已裁定，不计 FAIL）：本机代理拦截 POST，`gh pr create` 报 GraphQL 权限错、REST `POST /pulls` 404、直连 curl HTTP 000；本项目自 M0 起一律本地 `git merge --no-ff` 直推、不走 PR。因此 dco 的 PR 事件分支**仅结构性实现 + 本地脚本级模拟，未真机实证**；M5-05 的 "push/PR 全绿" 中 PR 半句同样**未获实证**（feat/m5-ci 全部 7 个 run 均为 push 事件）。这是环境限制而非实现缺陷，但白纸黑字记明：若日后具备 PR 条件，需补一次真机 PR run 验证 `pull_request.base.sha..head.sha` 口径。

2. **M5-03 静态检查信号很薄**（控制器已裁定，字面 PASS 但不构成质量背书）：全仓自有 C 代码仅 `kernel/interfaces/router_if.h` 一个头文件（实测 `find kernel tools plugins -name '*.c' -o -name '*.h'` → 1 个），故 clang-format 实核 1 文件、cppcheck 核 1 个头文件且无 TU（无真实编译单元分析）。pyflakes 覆盖 4 个 python 文件。**该 job 当前承载的信号不构成对 EtherOS 代码质量的背书**，仅证明门禁管线已点亮。

3. **spec-consistency 章节头子串判定盲区**（控制器已裁定，记档不阻塞）：判据为 `f"## {m}" not in std`，而 `acceptance-standard.md:30` 存在 `## M1+ · 占位`，导致真实 `## M1` 章节被删仍放行。来源为计划脚本原文，实现逐字落地。本报告反例 3b 实测复现（删 `## M1 · 底座基线(归档...)` → exit 0 放行），确证盲区存在。建议后续改为行首锚定正则（如 `re.search(rf'^## {m}\b', std, re.M)`）。

4. **dco job 的验收前修复不算回退**（控制器提示）：`85c5af9` 将 PR 分支从 `origin/<base_ref>` 改为 `pull_request.base.sha..head.sha`（规避 actions/checkout#2219）。dco 系 M5 新增 job，其自身在验收前的迭代**不落入 M5-07 的零回退口径**；M5-07 仅约束 M5 开工前就有的 etherkit-consistency / plugin-schema / build / vm-smoke。

5. **cppcheck 目录形式改为显式文件列表**（风险 A 预裁定，已在 ci.yml:125-128 记档）：`kernel/` 下只有 `.h`，cppcheck 扫目录报 "could not find or open any of the paths given."，属"找不到文件"而非真实告警；改为 `find kernel \( -name '*.c' -o -name '*.h' \) -print0 | xargs -0 -r cppcheck ...`。**未放宽 `--error-exitcode`、未加 `--suppress`**，非消音（红线检查已确认）。

6. **本报告未登记进 `docs/index.md`**：验收者铁律限制改动仓库文件（唯一例外即本报告本身），且 `docs/index.md` 的「新增/移动文档必须更新本表」规则按 M4 报告先例由关门任务（控制器代笔 plumbing）补登。**需补一行**：`| docs/reports/2026-10-06-m5-acceptance.md | M5 独立验收报告（7/7 PASS，3 条 PASS-with-note） |`（经本机校验：该引用在 spec-consistency 的双基准检查下走仓库根基准可解析，登记后不会造成悬空 FAIL）。

7. **本机未取证项（声明，不含推断）**：clang-format 与 cppcheck 本机无工具链，M5-03 / M5-06 的这两项本机验证**未执行**，结论基于 ci.yml 结构核对 + CI run 实证。

8. **反例还原已核验**：4 组反例涉及 `plugins/schema/plugin.schema.json`、`docs/index.md`、`docs/development/acceptance-standard.md`、`.etherkit/AGENTS.md`，全部 `git checkout --` 还原；验收收尾 `git status --short` 为空。反例脚本位于 `%TEMP%/m5acc/spec_check.py`，未落进仓库。

---

**STATUS: PASS**

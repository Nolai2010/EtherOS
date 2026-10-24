# M13 独立验收报告 —— translator 直通模式（裸 `.desktop` 原样翻译）

- **STATUS**：**PASS**（M13-01 ~ M13-06 六条全 PASS，其中 M13-02 / M13-04 / M13-06 各带 1 条记账口径 note，均不阻塞）
- **区间**：`e1ba72c..9c38add`，共 **7 个非合并提交**（`e136ba2` → `a2e2f64` → `acfbd62` → `49c4594` → `742a689` → `558425c` → `9c38add`）
- **被验对象**：`I:/etheros`，分支 `feat/m13-translator-passthrough`，HEAD `9c38addd0af2b5fe59b60fb7d314e917cf6e7b65`
- **对照基线**：tag `v0.12.0-m12` = `e1ba72cd5ce65d4797c440ecdf56cedb8f5ff845`（M12 合并进 main 的提交）
- **执行日期**：2026-10-25
- **依据**：`docs/development/acceptance-standard.md` §`## M13 · translator 直通模式（裸 \`.desktop\` 原样翻译）`（M13-01~M13-06）
- **口径**：偏严。全部判据**自己实跑取证**，不引用实现方/审查方的结论；基线对照用**三路独立工作树**（m12 树 + m12 translator / m12 树 + HEAD translator / HEAD 树）把"translator 变了"与"树变了"两个变量拆开；CI 取证走 `gh` GET 且 headSha 逐字核对；夹具与产物全程只落 `/tmp/m13-acc/**`；**未修改仓库任何既有文件**（验收前后 `git status --porcelain` 均为空）
- **写操作范围**：**仅新建本报告一个文件**；未改 ci.yml / translator.py / README / acceptance-standard.md，未推 tag、未动 main

---

## 0. 被验对象定位

```
$ git rev-parse --abbrev-ref HEAD && git rev-parse HEAD
feat/m13-translator-passthrough
9c38addd0af2b5fe59b60fb7d314e917cf6e7b65

$ git status --porcelain
（空输出——工作区干净）

$ git log --oneline e1ba72c..HEAD
9c38add docs(ci): M13 smoke negative-count comment accuracy (five to seven)
558425c ci: M13 smoke add empty-file + Type=Link passthrough negatives (review F-1)
742a689 docs(compat): register desktop-entry in directory semantics (M10 leftover)
49c4594 docs(ci): M10 smoke negative-case comment accuracy (XOR layer, M13-04)
acfbd62 ci: desktop-entry passthrough smoke (M13)
a2e2f64 feat(compat): desktop-entry passthrough mode (--payload-only)
e136ba2 docs: add M13 acceptance criteria (controller-verified)
```

七提交与任务书一致 ✅

---

## M13-01 直通模式存在

**判据**：`translator.py` 支持 `--payload <.desktop>` 无 `--manifest` 直译（二选一互斥 + 直通 `--out` 必填），成功 `status: "translated"` 并真实产出 manifest v2 + 包装 payload。

### 取证 1：富样本直通正例

夹具 `/tmp/m13-acc/rich.desktop`（含 `[Desktop Entry]`、`Type=Application`、`Name=Rich Probe App`、`Exec=/usr/bin/x`、`Icon`、`Terminal=false`、`Comment`、`Categories=Utility;`、本地化键 `Name[zh_CN]=富`、未知键 `X-Probe=1`）：

```
$ python3 plugins/compat/desktop-entry/translator.py \
    --payload /tmp/m13-acc/rich.desktop --out /tmp/m13-acc/pt
exit=0
{
  "plugin": "rich-probe-app",
  "source_format": "desktop-entry",
  "target_format": "etheros-native",
  "protocols": ["desktop-entry"],
  "status": "translated",
  "kind": "descriptor-level",
  "source_payload": "...\\m13-acc\\rich.desktop",
  "manifest": "...\\m13-acc\\pt\\plugin.json",
  "payload": "...\\m13-acc\\pt\\rich-probe-app.payload",
  "steps": ["parse-desktop-entry", "normalize-name", "emit-manifest-v2", "emit-wrapper-payload"],
  "note": "descriptor-level translation: ... NOT loaded, NOT run. ipa/exe and plugins/optional/douyin/ remain stub (差异点 2)."
}

$ ls -la /tmp/m13-acc/pt/
-rw-r--r--  395  plugin.json
-rw-r--r--  552  rich-probe-app.payload
```

exit 0 ✅ / `status=translated` ✅ / `plugin=rich-probe-app`（`Rich Probe App` 按 README 归一化规则）✅ / 两个产物真实存在 ✅ / stderr 0 字节 ✅

### 取证 2：二选一互斥与 `--out` 必填

```
$ translator.py --out <OUT>                       # 都不给
translator: give exactly one of --manifest/--payload                              exit=2
$ translator.py --payload <rich>                  # 直通缺 --out
translator: passthrough mode (--payload without --manifest) requires --out — there is no manifest directory to default to   exit=2
```

两条均 exit 2、给出原因、无输出目录 ✅（完整七条见 M13-04）

判定：**PASS**

---

## M13-02 向后兼容（带 `--manifest` 的既有调用逐字节不变）

**判据**：带 `--manifest` 的全部既有调用行为与输出逐字节不变（对 v0.12.0-m12 基线比对），`route_plugins --run douyin` 链路不变。

### 取证方法：三路工作树，把两个变量拆开

任务书给的是"HEAD translator 注入 m12 树"的单一对照。那只能证明"新 translator 在新旧树上行为一致"，**证明不了"新 translator 与旧 translator 行为一致"**——而后者才是 M13-02 真正要的。故本报告加做第三路，构成严格的变量分离：

| 代号 | 工作树 | translator |
|---|---|---|
| **A** | m12 树（`/tmp/m13-acc-base` @ `e1ba72c`） | **m12 原版**（sha256 `197cc61b…`） |
| **B** | m12 树（同一棵树） | **HEAD 版**（sha256 `2773ad49…`） |
| **C** | HEAD 树（`I:/etheros` @ `9c38add`） | HEAD 版 |

A→B 只变 translator，B→C 只变树。A 与 B 在**同一棵树、同一命令行**下运行，因此可做**零归一化**的逐字节 `cmp`。

### 取证 1：A vs B —— 同树同参数，零归一化逐字节 `cmp`

```
# 形式一：显式 --out /tmp/m13-acc/base（A 先跑、产物移走；B 用同一路径重跑）
$ cmp truem12/stdout.declared.json base/stdout.declared.json   → STDOUT IDENTICAL
$ cmp truem12/declared/plugin.json base/plugin.json            → plugin.json IDENTICAL
$ cmp truem12/declared/demo-desktop-app.payload base/demo-desktop-app.payload → payload IDENTICAL

# 形式二：缺省 --out（写入 <manifest 目录>/translated/，两种既有调用形式都覆盖）
$ cmp truem12/stdout.dflt.json base/stdout.dflt.json           → STDOUT(dflt) IDENTICAL
$ cmp truem12/dflt/plugin.json base/dflt/plugin.json           → plugin.json(dflt) IDENTICAL
$ cmp truem12/dflt/demo-desktop-app.payload base/dflt/demo-desktop-app.payload → payload(dflt) IDENTICAL

$ wc -c truem12/stderr.declared.txt base/stderr.declared.txt truem12/stderr.dflt.txt base/stderr.dflt.txt
0 ... 0 ... 0 ... 0 total   （四次 stderr 全为空）
```

两种既有调用形式（`--out` 显式 / `--out` 缺省）**全部 6 项 `cmp` 逐字节相同**，stderr 全空 ✅

### 取证 2：B vs C —— 跨树，位置归一化后相同

跨树时 `source_payload` / `manifest` / `payload` 三条键与包装 payload 的 `# source descriptor:` 行必然含不同的绝对路径（见 known notes ③）。用 `pnorm.py` 做**唯一一种**变换（路径 → 文件名 / 末两段）后逐字节比对：

```
$ python3 pnorm.py '[["json","base/stdout.declared.json","head/stdout.declared.json"],
                     ["payload","base/demo-desktop-app.payload","head/demo-desktop-app.payload"]]'
[json]  raw bytes equal     : False  (A sha256=369a7ba2…  B sha256=8cbb0771…)
        position-normalized : True   (A sha256=7e374d42…  B sha256=7e374d42…)
        key set equal       : True
[payload] raw bytes equal     : False
        position-normalized : True   (A sha256=79a2cef9…  B sha256=79a2cef9…)

$ cmp base/plugin.json head/plugin.json   → 逐字节相同（manifest 内不含绝对路径，可原始比对）
```

manifest 产物跨树**原始逐字节相同** ✅

### 取证 3：`route_plugins --run douyin` 三路一致

```
$ sha256sum truem12/route.stdout base/route.stdout head/route.stdout
ec43cba2db83dcd9ae2ca4c02161b083421ae922d8288f96caafe0e49a40bc5a  truem12/route.stdout
ec43cba2db83dcd9ae2ca4c02161b083421ae922d8288f96caafe0e49a40bc5a  base/route.stdout
ec43cba2db83dcd9ae2ca4c02161b083421ae922d8288f96caafe0e49a40bc5a  head/route.stdout
```

三路 stdout **原始逐字节相同**（路径无关），douyin 仍为 `status: "stub-plan-only"`（口径未动）✅

判定：**PASS**（带 note ③：跨树比对需位置归一化；同树 A/B 对照不依赖任何归一化）

---

## M13-03 直通产物过硬校验

**判据**：过 `validate_plugins.py --file`（schema v2）；id 由 Name 归一化、撞名即拒（无自撞名例外）；输出键名集合与声明模式相同。

### 取证 1：过硬校验

```
$ python3 tools/validate_plugins.py --file /tmp/m13-acc/pt/plugin.json
plugins validation: OK
validate exit=0
```

直通产物 manifest 通过 schema v2 校验 ✅

### 取证 2：键名集合与声明模式逐字相同

```
pt  manifest keys : ['capabilities','container','name','payload','protocols','schema_version','translator','type','uninstallable','version']
reg manifest keys : ['capabilities','container','name','payload','protocols','schema_version','translator','type','uninstallable','version']
equal : True

共同字段值比对：
  schema_version  pt='2'                  reg='2'                  equal=True
  type            pt='compat-bridge'      reg='compat-bridge'      equal=True
  uninstallable   pt=True                 reg=True                 equal=True
  container       pt={'desktop':'windowed'} reg={'desktop':'windowed'} equal=True
  protocols       pt=['desktop-entry']    reg=['desktop-entry']    equal=True
  translator      pt='plugins/compat/...' reg='plugins/compat/...' equal=True
  capabilities    pt=['desktop.category.utility'] reg=['desktop.category.utility']
  name            pt='rich-probe-app'     reg='demo-desktop-app'  （预期不同）
```

### 取证 3：撞名即拒，**无**"重翻译自身"例外（关键对照）

同一个 id `demo-desktop-app` 在两种模式下的待遇必须相反，否则"无例外"就是空话：

```
$ translator.py --payload neg/selfid.desktop --out <OUT>     # 直通，Name=Demo Desktop App
translator: normalized plugin id 'demo-desktop-app' (from Name='Demo Desktop App') collides
            with an existing plugin id in plugins/{builtin,optional,dev} — refuse to overwrite
            another plugin (差异点 4)
passthrough exit=2   outdir=no

$ translator.py --manifest plugins/optional/demo-desktop-app/plugin.json --out <OUT>   # 声明，同名
declared exit-path status=translated plugin=demo-desktop-app
declared exit=0
```

直通拒、声明收 ✅ —— 例外**只**存在于声明模式，直通模式确实无例外（约束 65 / 差异点 4）✅

判定：**PASS**

---

## M13-04 负例（七条，逐条实跑）

**判据**：`--manifest` 与 `--payload` 同时给出 → 拒；直通缺 `--out` → 拒；直通 `Name` 撞名 → 拒；既有负例（无 Exec / 非法格式 / 空文件 / Type≠Application）在直通模式同样拒。

七条共用输出目录 `<OUT>=/tmp/m13-acc/neg-out`，每条前先 `rm -rf`：

| # | 负例 | 命令（省略 `translator.py` 前缀） | exit | stdout | 输出目录 | stderr 原因 |
|---|---|---|---|---|---|---|
| ① | 参数互斥 | `--manifest <demo>/plugin.json --payload rich.desktop --out <OUT>` | 2 | 0 字节 | 无 | `give exactly one of --manifest/--payload` |
| ② | 直通缺 `--out` | `--payload rich.desktop` | 2 | 0 字节 | 无 | `passthrough mode (--payload without --manifest) requires --out — there is no manifest directory to default to` |
| ③ | 直通撞名 | `--payload douyin.desktop --out <OUT>` | 2 | 0 字节 | 无 | `normalized plugin id 'douyin' (from Name='Douyin') collides with an existing plugin id in plugins/{builtin,optional,dev} — refuse to overwrite another plugin (差异点 4)` |
| ④ | 无 `Exec` | `--payload noexec.desktop --out <OUT>` | 2 | 0 字节 | 无 | `desktop entry has no Exec= (or it is empty) — nothing to forward into the wrapper payload` |
| ⑤ | 非法 JSON | `--payload bad.desktop --out <OUT>` | 2 | 0 字节 | 无 | `payload is not a freedesktop desktop entry: no [Desktop Entry] section (looks like JSON, not a desktop entry)` |
| ⑥ | 空文件 | `--payload empty.desktop --out <OUT>` | 2 | 0 字节 | 无 | `payload 'empty.desktop' is empty (0 bytes / blank) — nothing to translate` |
| ⑦ | `Type=Link` | `--payload link.desktop --out <OUT>` | 2 | 0 字节 | 无 | `desktop entry Type='Link' is not supported — only Type=Application maps to a compat-bridge plugin (Type=Link/Directory have no Exec payload to bridge)` |

```
=== 汇总：输出目录是否残留 ===
no output dir (OK)
```

七条全部：exit 2 ≠ 0 ✅ / stderr 有原因 ✅ / 无输出目录 ✅ / stdout 0 字节（拒绝即不伪装成功）✅

补充探针（超出检查单）：`--manifest` 与 `--payload` **都不给** → 同因 `give exactly one of --manifest/--payload`，exit 2，无输出目录 ✅

判定：**PASS**（带 note ①：M10 step 里同名的三条内容负例现已被 XOR 层吞掉，见 known notes）

---

## M13-05 诚实边界

**判据**：README 与 compat 契约同步写明直通模式语义（翻译产物非用户声明、描述符级非二进制）；零新输出键；不得宣称可运行 `.desktop`。

### 取证 1：夸大宣称 grep —— 零命中

```
$ grep -rn "支持运行\|可以运行\|能运行" plugins/compat/desktop-entry plugins/compat/README.md
grep exit=1        # 无匹配 ✅

# 扩大口径复扫（超出检查单）
$ grep -rnE "支持运行|可以运行|能运行|能够运行|可直接运行|运行 \.desktop|\.desktop 应用|原生运行|真正执行|可执行" \
    plugins/compat/desktop-entry plugins/compat/README.md
exit=1             # 零命中 ✅
```

全仓范围的同模式命中仅有 5 处，经逐条实读**均非违规**：`progress.md:178`（该行是**禁止**此宣称的裁定原文）、`task-m10-4-review.md` / `task-m13-4-review.md`（记录 grep 本身）、`2026-10-24-m10-acceptance.md`（记录 grep 本身）、`RELEASE_NOTES.md:69`（"**不得**据此宣称"的否定式表述）。无可运行宣称 ✅

### 取证 2：直通节存在且写明"翻译产物非用户声明"

```
$ grep -n "直通\|passthrough" plugins/compat/desktop-entry/README.md
62:## 直通模式（--payload-only）
73:- **产物是翻译产物，不是用户声明**：直通模式生成的 manifest 由本 translator 推导生成（id 由 `Name` 归一化而来），与手写的源声明 JSON 性质不同；它同样只是描述符级翻译的产物，见上方诚实边界。

$ grep -n "直通" plugins/compat/README.md
24:- **真 translator(M13 起二选一)**:…直通产物是**翻译产物非用户声明**、仍是描述符级翻译(诚实边界见 `desktop-entry/README.md`)。
```

`## 直通模式（--payload-only）` 独立成节（:62-73）✅；"产物是翻译产物，不是用户声明"明写（:73）✅；compat 契约 `plugins/compat/README.md:24` 同步 ✅；描述符级边界在同文件 :5-11「诚实边界（先读这一节）」✅

### 取证 3：零新输出键

```
result JSON 键集合：
  passthrough : ['kind','manifest','note','payload','plugin','protocols','source_format','source_payload','status','steps','target_format']
  declared    : ['kind','manifest','note','payload','plugin','protocols','source_format','source_payload','status','steps','target_format']
  equal       : True
  symmetric diff : []
```

两模式 result JSON 键集合**逐字相同、对称差为空** ✅（约束 66）

### 取证 4：本地化/未知键不进 manifest

```
zh_CN      in manifest: False
X-Probe    in manifest: False
Icon       in manifest: False
Terminal   in manifest: False
富          in manifest: False
```

富样本的本地化键与未知键全部被逐键不采信，未泄漏进 manifest ✅

判定：**PASS**（带 note ②：README 负例计数口径与 CI/M13-04 不一致，见 known notes）

---

## M13-06 旧门禁零回退

**判据**：十 job 名与行为不变（既有 step 零改动、只追加），stub-runtime/douyin/demo-desktop-app/schema/config/release.yml 零 diff，M10 smoke 不失效。

### 取证 1：M10 smoke step 零改动（pyyaml 对象级 + run 块 sha256）

```
$ git show v0.12.0-m12:.github/workflows/ci.yml > ci.m12.yml
$ cp .github/workflows/ci.yml ci.head.yml
$ python3 cistep.py ci.m12.yml ci.head.yml "Desktop-entry translation smoke"

== job 名集合 ==
  m12  job count: 10    head job count: 10
  job names equal (ordered): True      only in m12 : []     only in head: []

== 既有 job 的 step 级对象比对 ==
  [etherkit-consistency] steps identical (7 steps)
  [plugin-schema]  既有 8 steps 逐个相等，head 追加 1 step: ['Desktop-entry passthrough smoke (M13 passthrough mode)']
  [license]        steps identical (3)      [dco]    steps identical (2)
  [lint]           steps identical (5)      [spec-consistency] steps identical (2)
  [build]          steps identical (4)      [vm-smoke]        steps identical (6)
  [build-aarch64]  steps identical (4)      [vm-smoke-aarch64] steps identical (6)

== 目标 step ==
  m12  location: job=plugin-schema step#5  name='Desktop-entry translation smoke (M10 real translator)'
  head location: job=plugin-schema step#5  name='Desktop-entry translation smoke (M10 real translator)'
  run 块 sha256  m12 : e99b438e653d4c3ba2d9bc413ab79e2b5235685e040fd3998d2a4b3b8536df85  (2107 bytes)
  run 块 sha256  head: e99b438e653d4c3ba2d9bc413ab79e2b5235685e040fd3998d2a4b3b8536df85  (2107 bytes)
  run 块逐字节相等: True
  step 对象相等: True
RESULT: ALL EQUAL
```

M10 step 的 run 块 sha256 = `e99b438e…`，与期望值逐字一致 ✅；十 job 名集合有序相同 ✅；**八个 job 的 step 完全未动**，唯一变化是 `plugin-schema` **尾部追加** 1 个 M13 step（纯追加，非插入/修改）✅

### 取证 2：敏感路径零 diff

```
$ git diff v0.12.0-m12..HEAD -- plugins/compat/stub-runtime plugins/optional/douyin \
    plugins/optional/demo-desktop-app plugins/schema config .github/workflows/release.yml \
    tools kernel base | wc -l
0
```

stub-runtime / douyin / demo-desktop-app / schema / config / release.yml / tools / kernel / base **零字节 diff** ✅（douyin 与 stub 仍是 stub，未借 M13 改口径）

### 取证 3：改动面与 DCO

```
$ git diff e1ba72c..HEAD --name-status
M	.github/workflows/ci.yml
M	docs/development/acceptance-standard.md
M	plugins/compat/README.md
M	plugins/compat/desktop-entry/README.md
M	plugins/compat/desktop-entry/translator.py
count=5                                   # 恰 5 文件 ✅

 .github/workflows/ci.yml                   | 100 ++++++++++++++++++++++++-
 docs/development/acceptance-standard.md    |  11 ++++
 plugins/compat/README.md                   |  12 +++-
 plugins/compat/desktop-entry/README.md     |  29 +++++++--
 plugins/compat/desktop-entry/translator.py |  58 +++++++++++------
 5 files changed, 182 insertions(+), 28 deletions(-)

$ git log --format=%b e1ba72c..HEAD | grep -c "Signed-off-by"
7                                         # 七提交七签名 ✅
```

### 取证 4：CI 实跑（run 40110451963）

```
$ gh run view 40110451963 --repo Nolai2010/EtherOS --json headSha,conclusion,jobs
headSha    : 9c38addd0af2b5fe59b60fb7d314e917cf6e7b65     # 逐字等于被验 HEAD ✅
conclusion : success
job count: 10
  success  license (reuse lint, submodules excluded per spec 5 / risk 2)
  success  lint (EtherOS-owned code only; base/ structurally excluded)
  success  etherkit single-source consistency
  success  build ToaruOS base (upstream builder image)
  success  plugin manifest schema & config consistency (M2)
  success  spec & docs reference consistency (anti context-drift)
  success  dco (Signed-off-by on every commit, merges exempt)
  success  build ToaruOS aarch64 base (upstream builder image)
  success  vm smoke aarch64 (QEMU headless boot evidence)
  success  vm smoke (QEMU headless boot evidence)
all success: true
```

headSha 逐字核对通过（防"陈旧 run"坑）✅ / 十 job 全 success ✅

### 取证 5：CI 日志标记

```
$ gh run view 40110451963 --repo Nolai2010/EtherOS --log --job 120920873023 \
    | grep -E 'PASSTHROUGH OK|DECLARED REGRESSION|KEY SETS|PASSTHROUGH SMOKE'
…M13 passthrough mode…  PASSTHROUGH OK /home/runner/work/_temp/m13-pt/plugin.json
…M13 passthrough mode…  DECLARED REGRESSION OK /home/runner/work/_temp/m13-reg/plugin.json
…M13 passthrough mode…  KEY SETS IDENTICAL (zero new output keys) ['capabilities','container','name','payload','protocols','schema_version','translator','type','uninstallable','version']
…M13 passthrough mode…  PASSTHROUGH SMOKE OK (M13 real passthrough + declared-mode regression)
```

四个标记**全部为运行时真实打印行**（非源码 echo 行）✅

### 取证 6：M10 smoke 在 M13 run 里不失效

```
…M10 real translator…  TRANSLATE OK /tmp/m10-translate/plugin.json
…M10 real translator…  TRANSLATED ARTIFACT LOADABLE OK ['demo-desktop-app']
```

M10 step 在 M13 的 CI run 中仍然产出真实成功标记 ✅（但也见 note ①——它绿的原因已变）

### 取证 7：job 名与 M12 基线 run 对象级比对

```
$ # M12 基线 run：40103666640（headSha e1ba72cd…，conclusion success）
run 40103666640: count=10     run 40110451963: count=10
$ diff <(job名排序) <(job名排序)   → 十个名逐条相同
```

真实 CI run 层面的十 job 名集合与 M12 基线**相同** ✅

判定：**PASS**（带 note ①）

---

## Known notes

### ① M10 三条内容负例现已被 XOR 层吞掉（记账口径，非功能缺失）

M13 把 CLI 改成 `--manifest` XOR `--payload`。M10 的 smoke step 里那三条内容负例当初正是用**两参同时给出**的合法覆盖写法写的，因此在 M13 下它们会在 XOR 层被拦下，**根本走不到内容层**。实跑取证：

```
=== M10 step 的三条内容负例在 M13 translator 下的实际拒绝层 ===
  noexec   exit=2  stderr=translator: give exactly one of --manifest/--payload
  bad      exit=2  stderr=translator: give exactly one of --manifest/--payload
  empty    exit=2  stderr=translator: give exactly one of --manifest/--payload
  → 三条均在 XOR 层被拒，非内容层

=== 同一内容负例在直通模式下的拒绝层（内容层）===
  noexec   exit=2  desktop entry has no Exec= (or it is empty) — nothing to forward into the wrapper payload
  bad      exit=2  payload is not a freedesktop desktop entry: no [Desktop Entry] section (looks like JSON, not a desktop entry)
  empty    exit=2  payload 'empty.desktop' is empty (0 bytes / blank) — nothing to translate
  link     exit=2  desktop entry Type='Link' is not supported — only Type=Application maps to a compat-bridge plugin
```

结论：M10 step 里那三条 `!` 断言**仍然为绿**（XOR 拒绝同样让命令非零退出），但测的已不是它们自称的内容门禁；内容层覆盖已**整体迁移**到 M13 passthrough step（直通模式下 4 条全部在内容层被拒，归因准确）。M10 step 的 run 块本身零改动（sha256 `e99b438e…`），因此 M13-06「既有 step 零改动」成立；但**"M10 smoke 的内容负例仍在测内容"这一说法不再成立**，记账时应按"XOR 层 + 内容层迁移至 M13 step"表述。提交 `49c4594` 已在 ci.yml 里为这条写了注释，与本报告实跑结论一致。不阻塞 M13-04 / M13-06，但建议后续里程碑把这个记账口径保留可见。

### ② README 负例计数口径与 CI/M13-04 不一致

`plugins/compat/desktop-entry/README.md:75` 标题写「负例（**六条**，各自 exit 2 + 原因）」，表格为 ①~⑥ 六行；而 `ci.yml:374` 注释写「负例**七条**(互斥两给/直通缺 --out/直通撞名 Name=Douyin/无 Exec/非法 JSON/空文件/Type=Link)」，M13-04 判据口径也是 7（Type=Link 单列）。`Type=Link` 在 README:86 以附注形式提及，未进表格，故计数差 1。属**文档记账口径差异**，非功能缺失；考虑到 `9c38add` 刚为 CI 修过同类计数准确性问题，建议后续把 README 的标题与表格对齐到七条。不阻塞 M13-05。

### ③ 跨树比对需"位置归一化"（方法论留痕）

声明模式 stdout 的 `source_payload` / `manifest` / `payload` 三条键，以及包装 payload 的 `# source descriptor:` 行，含被验对象的绝对路径。两棵树、两个输出目录必然不同，故跨树原始 `cmp` 必不相等——这是**位置**差异，不是行为差异。本报告的处理：

- **A vs B 同树同参数**的 6 项 `cmp` 是**零归一化**的逐字节相同，这是 M13-02 的主力证据；
- B vs C 跨树部分才使用归一化，且只做"路径 → 文件名 / 末两段"这一种变换，变换后的 sha256 逐字相同；
- manifest 产物自身不含绝对路径，跨树**原始**逐字节相同。

### ④ 取证环境差异

本机为 Windows + Git Bash（`/tmp` → `C:\Users\JunYa\AppData\Local\Temp`，路径分隔符为 `\`），CI 为 ubuntu-latest（路径分隔符 `/`）。本机实证与 CI 实证的结论一致，路径形态差异不影响任何判定。

---

## 结论

| 编号 | 判定 |
|---|---|
| M13-01 直通模式存在 | **PASS** |
| M13-02 向后兼容（逐字节） | **PASS**（note ③） |
| M13-03 直通产物过硬校验 | **PASS** |
| M13-04 负例七条 | **PASS**（note ①） |
| M13-05 诚实边界 | **PASS**（note ②） |
| M13-06 旧门禁零回退 | **PASS**（note ①） |

**总判定：PASS** —— M13 的直通模式真实存在且可产出过硬校验的 manifest v2 + 包装 payload；带 `--manifest` 的既有调用经三路工作树变量分离后确认为逐字节不变；七条负例各自 exit 2、明因、零产物；诚实边界与零新输出键守住；十 job 旧门禁零回退。三条 known notes 均为记账口径/方法论留痕，无一指向功能缺失或诚实性问题，不阻塞。

验收全程**未修改仓库任何既有文件**，写操作仅本报告一个新文件。

# M8 独立验收报告 —— aarch64 第二架构（spec §4 M1 目标句清偿）

- **验收者**：general-purpose-1（独立上下文，与 M8-1~M8-4 的实现者 / 复审者均不同；不替实现背书，不采信自评）
- **被验对象**：分支 `feat/m8-aarch64`，HEAD `f079fab`（`f079fab840bccc8e58866007e6829c131235d257`，提交主题 `ci: keep QEMU cmd block free of inline comments (bash cont)`）
- **区间**：`v0.7.0-m7..HEAD`，共 **6 个非合并提交**（`c9ae865` → `f079fab`），`ahead_by=6 / behind_by=0`
- **取证快照**：M8-01~M8-06 六条的判定**全部以 `f079fab`（M8 实现 HEAD）为准**。验收执行期间，M8-6 关门工作的提交 `dd939a0` 与本报告的 `ed88568` / `c570714` 并发落在同一分支上；其对 ci.yml 的追加改动**不属于本次验收对象**，但已做事后复核，见 §事后复核（并发关门提交后）。M8-01 / M8-02 / M8-05 / M8-06 的结论不受该提交影响。
- **依据**：`docs/development/acceptance-standard.md` M8 章节（M8-01~M8-06）+ `spec/2026-10-05-etheros-dev-policy.md` §4 M1 行（:191）+ M8 计划差异点 5（转正口径）
- **口径**：偏严——证据一律取自 CI 实际日志与 artifact 字节，不采信实现者报告的自述数字；M8-02 另跑**反向反例**证明断言非空转；零回退一律用 pyyaml 做 **job 级对象比对**，不做肉眼 diff
- **写操作范围**：**仅新建本报告一个文件**；未改 ci.yml / release.yml / acceptance-standard.md / spec / M1 验收报告，未推 tag、未动 main、未派子代理
- **执行日期**：2026-10-17

---

## 0. 判据存在性核验与被验对象定位

```
acceptance-standard.md:108  ## M8 · aarch64 第二架构（spec §4 M1 目标句清偿：x86-64/aarch64 可构建）
acceptance-standard.md:111-116  M8-01 / M8-02 / M8-03 / M8-04 / M8-05 / M8-06
```

六条判据齐全、逐字与 M8 计划 Step 2 提案一致，无降标、无缺条。

被验对象定位（远端实测，非本地声明）：

```
$ gh api repos/Nolai2010/EtherOS/commits/feat/m8-aarch64 --jq '.sha'
f079fab840bccc8e58866007e6829c131235d257

$ gh api repos/Nolai2010/EtherOS/actions/runs/39042486091 --jq '{head_sha,head_branch,conclusion}'
{"conclusion":"success","head_branch":"feat/m8-aarch64","head_sha":"f079fab840bccc8e58866007e6829c131235d257"}
```

**本里程碑取证 run = 39042486091**（push 触发，对应 HEAD `f079fab`，结论 `success`）。以下 M8-01 / M8-02 的证据全部出自该 run，M8-03 的"零回退"也以该 run 的十 job 结论为准。

---

## M8-01 · build-aarch64 job 存在且绿（产物含 misaka-kernel / ramdisk.igz / bootstub / kernel8.img）

**判据**：job 存在且绿；复刻 build job 的 Docker 跑法，仅换 `toaruos/build-tools:aarch64` 镜像与 `util/build-in-docker-aarch64.sh`；产物 artifact 含四个文件。验证方式：CI 绿 + 产物清单。

配方忠实度（ci.yml 实测，与 x86 build job 逐字比对）：

| 项 | x86 build job（:226-227） | aarch64 build job（:357-358） |
|---|---|---|
| `docker pull` | `toaruos/build-tools:1.99.x` | `toaruos/build-tools:aarch64` |
| `docker run -v … -w … -e LANG=C.UTF-8 -t <镜像> <入口>` | `util/build-in-docker.sh` | `util/build-in-docker-aarch64.sh` |

除上述两处外，`-v ${{ github.workspace }}/base/toaruos:/root/misaka -w /root/misaka -e LANG=C.UTF-8 -t` 完全同形；`timeout-minutes: 90` 与 x86 一致。**只换两处，符合约束 36。**

job 结论：`build ToaruOS aarch64 base (upstream builder image)` ID `117424593122`，**success**，2m13s。

产物清单（job 日志内 `ls -la artifacts/` 原文，`Collect aarch64 boot artifacts` 步骤）：

```
-rwxr-xr-x  1 runner runner   81520 Oct 17 14:53 bootstub
-rwxr-xr-x  1 runner runner 6820104 Oct 17 14:53 kernel8.img
-rwxr-xr-x  1 runner runner  254776 Oct 17 14:53 misaka-kernel
-rw-r--r--  1 runner runner 6537776 Oct 17 14:53 ramdisk.igz
```

四件齐全（判据的"+kernel8.img"亦在内）。

产物确为 aarch64 而非 x86 混装（同 job 日志，编译/链接命令行原文）：

```
aarch64-unknown-toaru-gcc … -DKERNEL_ARCH=aarch64 … -o misaka-kernel.64 \
  kernel/arch/aarch64/irq.o kernel/arch/aarch64/entry.o … kernel/arch/aarch64/pl011.o
cp misaka-kernel.64 misaka-kernel
aarch64-unknown-toaru-strip misaka-kernel
aarch64-unknown-toaru-gcc … -o bootstub kernel/arch/aarch64/bootstub/main.o …
gzip -c ramdisk.tar > ramdisk.igz
aarch64-unknown-toaru-objcopy kernel8.img.elf -O binary kernel8.img
```

artifact 实测：`etheros-aarch64-artifacts`，`size_in_bytes=13,172,680`，`expired=false`。

判定：**PASS**。

---

## M8-02 · vm-smoke-aarch64 job 存在且绿（serial 捕获 `login:`，QMP screendump 取证）

**判据**：QEMU aarch64（`-M virt -cpu cortex-a72`）headless 启动，serial 捕获 `login:`（与 x86 侧同源于 `apps/login.c:86`），QMP screendump 取证。验证方式：CI 绿 + serial 证据。

job 结论：`vm smoke aarch64 (QEMU headless boot evidence)` ID `117425051177`，**success**，28s。该 job `needs: build-aarch64`（ci.yml:387），产物取自**同一 run** 的 `etheros-aarch64-artifacts`，不存在跨 run 借产物。

QEMU 机型（ci.yml:430，job 日志回显一致）：`-M virt -m 4G -smp 4 -cpu cortex-a72`，配 `-kernel "$BOOTSTUB"` + fw_cfg 注入 `opt/org.toaruos.kernel` / `opt/org.toaruos.initrd`。

### serial 实证（不采信自评，直接取 artifact 字节）

下载 `vm-smoke-aarch64-evidence` 后实测：

```
$ cat -v serial-aarch64.log
^[[s^[[1000;1000H^[[6n^[[ulivecd login:
$ xxd serial-aarch64.log
00000000: 1b5b 731b 5b31 3030 303b 3130 3030 481b  .[s.[1000;1000H.
00000010: 5b36 6e1b 5b75 6c69 7665 6364 206c 6f67  [6n.[ulivecd log
00000020: 696e 3a20                                in:
```

即 `ESC[s` `ESC[1000;1000H` `ESC[6n` `ESC[u` + `livecd login: `，**36 字节**。

与 M1 验收报告 A5 记录的 x86 侧 `serial-com2.log` 十六进制**逐字节相同**（`1b5b 731b 5b31 3030 303b 3130 3030 481b 5b36 6e1b 5b75 6c69 7665 6364 206c 6f67 696e 3a20`）——两侧同源于 `base/toaruos/apps/login.c:86` 的 `fprintf(stdout, "%s login: ", _hostname);`，hostname 同为 `livecd`。跨架构同一字符串、同一源码出处，符合约束 37。

job 日志侧同步互证：

```
poll rounds: 1, evidence: yes
BOOT EVIDENCE OK: userspace login reached on aarch64 serial (pl011)
```

### 反向反例（证明断言非空转，而非"总能绿"）

取实现过程中**带 `-a local` 的那次失败 run** 作负对照：`39039782092`，job `117417220938` ——

```
X vm smoke aarch64 (QEMU headless boot evidence) in 5m20s (ID 117417220938)
    X Assert boot evidence (honest)
poll rounds: 60, evidence: none
NO BOOT EVIDENCE IN SERIAL
```

其 serial 内容为**完整登录后的 shell**：`ESC]1;local@livecd:~` / `local@livecd:~$` 提示符（getty `-a local` → `login -f local` 免密直登）。即：OS 全链路确实起来了、止于 `local@livecd:~$`，但**没有 `login:` 字符串**，于是 job 判红。

这一正一反两条实证共同证明：`grep -aq "login:"` 断言在 aarch64 侧**具有区分力**，绿不是靠放宽或空转得来的。

### screendump

`screen.ppm` 921615 字节，头 `P6\n640 480\n255\n`，payload 921600 = 640×480×3 精确吻合，尺寸非伪造。但其内容质量问题见 **Minor 4**（与反例帧字节全等，不具区分力）；判据中 screendump 为"辅助证据、尽力而为、失败不阻塞"（ci.yml:450 注释与 x86 侧同形态），核心断言落在 serial，故不影响本条判定。

判定：**PASS**。

---

## M8-03 · 旧八 job 零回退（ci.yml diff 为纯插入）

**判据**：ci.yml 的 diff 为纯插入，八个旧 job 名与行为不变。验证方式：`git diff v0.7.0-m7..HEAD -- .github/workflows/ci.yml` 复核。

取证方式：取 `v0.7.0-m7` 与 HEAD 两版 ci.yml 原文，**pyyaml 解析后做 job 级对象比对**（非肉眼看 diff）。实测输出：

```
=== .github/workflows/ci.yml ===
bytes: base=17149 cur=25231
text diff: pure_insertion=True added_lines=154 removed_lines=0
jobs: base=8 cur=10
base job keys: ['build','dco','etherkit-consistency','license','lint','plugin-schema','spec-consistency','vm-smoke']
cur  job keys: ['build','build-aarch64','dco','etherkit-consistency','license','lint','plugin-schema','spec-consistency','vm-smoke','vm-smoke-aarch64']
removed jobs: NONE
added jobs:   ['build-aarch64','vm-smoke-aarch64']
job objects changed: NONE
non-jobs top-level keys changed: NONE
top-level keys: base=['True','jobs','name'] cur=['True','jobs','name']
```

八条结论：

1. 纯插入：`removed_lines=0`，`added_lines=154`，`pure_insertion=True`（difflib opcode 级，无任何 delete/replace 段）。
2. 旧八 job **无一被删**。
3. 旧八 job 的**对象（steps / runs-on / name / timeout 全字段）逐一等值，`changed=NONE`** —— 不是"看起来没动"，是结构化全等。
4. 新增仅 `build-aarch64` / `vm-smoke-aarch64` 两个。
5. 非 jobs 顶层键（`name`、`on`、`permissions`）无变化；`on: push/pull_request` 触发面未动。
6. 顶层键集合不变（无新增 env / concurrency / permissions 之类的旁路改动）。
7. run 39042486091 十个 job 结论**全 `success`**（lint / dco / build / plugin-schema / spec-consistency / build-aarch64 / license / etherkit-consistency / vm-smoke-aarch64 / vm-smoke），无 skipped、无 cancelled。
8. 无消音手段：新增 job 无 `continue-on-error`、无 `|| true` 包住断言步骤（断言步骤为独立 step，`grep` 失败即 `exit 1`）。

判定：**PASS**。

---

## M8-04 · release.yml 零 diff（aarch64 产物不进发布通道）

**判据**：release.yml 零 diff，三形态维持。验证方式：diff 为空。

三重取证：

```
=== .github/workflows/release.yml ===
bytes: base=2441 cur=2441
text diff: pure_insertion=True added_lines=0 removed_lines=0
jobs: base=2 cur=2
base job keys: ['build-release','publish-release']
cur  job keys: ['build-release','publish-release']
removed jobs: NONE / added jobs: NONE
job objects changed: NONE
non-jobs top-level keys changed: NONE
```

1. **字节级**：两版同为 2441 字节，`diff` 输出 0 字节（等价于 `git diff v0.7.0-m7..HEAD -- .github/workflows/release.yml` 为空）。
2. **对象级**：pyyaml 解析后 2 个 job 的**对象全等**，顶层 `name` / `on`（含 tags + workflow_dispatch.dry_run）/ `permissions` 全等。
3. **总账级**：Compare API `v0.7.0-m7...feat/m8-aarch64` 的变更文件清单里**根本没有 release.yml**（全区间仅 2 个文件，见 M8-05）。

镜像 `toaruos/build-tools:1.99.x` + `util/build-in-docker.sh` 与 ci.yml:build 的同源关系（M6-01 注释互指）保持原样；aarch64 产物仅作 CI artifact，未进 Release，符合差异点 1。

判定：**PASS**。

---

## M8-05 · submodule / kernel / tools / config 零改动

**判据**：aarch64 构建完全发生在上游树内，EtherOS 自有树无一行改动。验证方式：diff 为空。

Compare API 全区间变更文件清单（权威，覆盖 submodule gitlink）：

```
$ gh api repos/Nolai2010/EtherOS/compare/v0.7.0-m7...feat/m8-aarch64 --jq '...'
{"ahead_by":6,"behind_by":0,"total_commits":6,"files":[
  {"additions":154,"deletions":0,"filename":".github/workflows/ci.yml","status":"modified"},
  {"additions":11,"deletions":0,"filename":"docs/development/acceptance-standard.md","status":"modified"}]}
```

**全区间仅 2 个文件、纯增（0 删除）**：

- `base/toaruos` submodule gitlink **不在清单内** → 仍锁定 `e77143fd14391d880c3ee11c1524252cdcbfd225`，未漂移、未初始化改动。
- `kernel/`、`tools/`、`config/` **零命中**；`plugins/`、`REUSE.toml`、`.etherkit/`、`spec/` 亦零命中。
- `docs/development/acceptance-standard.md` 的 +11 行即 M8-01~06 章节（M8-1 任务的既定交付），属计划 File Structure 明列，非夹带。

判定：**PASS**。

---

## M8-06 · spec 欠账清偿记档（口径差异 → 已达成）

**判据**：验收报告写明 M1 行的 aarch64 口径差异由"记档"转为"已达成"，并注明 riscv64 仍为仅评估。验证方式：报告实读（本报告即该记档）。

### ① 转正声明

> **spec §4 M1 行（`spec/2026-10-05-etheros-dev-policy.md:191`）「评估并拉取 ToaruOS（或备选），x86-64/aarch64 可构建且 GUI 启动」中的 aarch64 半句，自本里程碑起由"口径差异记档"转为"已达成"。**

**转正前状态**（引 `docs/reports/2026-10-06-m1-acceptance.md` 口径差异段 2 原文）：

> 「**aarch64 构建无独立证据**：spec M1 目标句含 "x86-64/aarch64 可构建"，但 CI build job 仅构建 x86_64（上游 builder 镜像 `toaruos/build-tools:1.99.x` 默认目标，产出 `misaka-kernel` 为 x86_64-pc-toaru），无 aarch64 构建证据。……aarch64 缺口记档供终审裁量，未计为 FAIL 项」

即：M1 时点该半句"含而未达"，以记档方式挂账。

**转正后证据**（引本里程碑 CI run）：

- 构建侧：run `39042486091` job `117424593122`（`build ToaruOS aarch64 base`）绿，产出 `misaka-kernel` / `ramdisk.igz` / `bootstub` / `kernel8.img` 四件，编译器为 `aarch64-unknown-toaru-gcc -DKERNEL_ARCH=aarch64` —— "**aarch64 可构建**"由无证据转为有实证（详见 M8-01）。
- 启动侧：同 run job `117425051177`（`vm smoke aarch64`）绿，QEMU `-M virt -cpu cortex-a72` headless 启动，pl011 串口捕获 `livecd login: `（与 x86 侧同源于 `apps/login.c:86`，字节序列逐字一致）—— "**GUI 启动**"沿用 M1 既定口径（差异段 3：以 headless QEMU 双取证 + QMP screendump 为证据，非人工目视桌面），aarch64 侧同口径达成（详见 M8-02）。
- 反证强度：同一断言在带 `-a local` 的 run `39039782092` 上判红，说明该证据不是靠放宽阈值换来的。

至此 spec §4 M1 行目标句**两个架构均无欠账**，M1 验收报告口径差异段 2 所记的缺口在本里程碑清偿。

### ② M1 验收报告原文不改写

按"版本化、不回改"惯例，**转正声明只在本 M8 报告内做出，不改 M1 报告一字**。实测确认：

```
docs/reports/2026-10-06-m1-acceptance.md : v0.7.0-m7 版 与 HEAD 版 —— IDENTICAL（字节一致）
spec/2026-10-05-etheros-dev-policy.md    : v0.7.0-m7 版 与 HEAD 版 —— IDENTICAL（字节一致）
```

M1 报告口径差异段 2 的原文（含"无 aarch64 构建证据"的表述）**原样保留**，作为转正前的历史状态证据；本报告与它互相引用，读者自行对照即可看出"记档 → 已达成"的时间线。同理 spec 原文未因本次清偿被回改。

### ③ riscv64 仍为仅评估

- `spec/2026-10-05-etheros-dev-policy.md:100`：「`arch/x86_64/`、`arch/aarch64/`（优先）；`arch/riscv64/` 等**仅评估留桩**」；§2.1「目标架构」：多架构，**优先 x86-64 与 aarch64**，其他仅评估。
- 实测：ci.yml 十个 job 中**无任何 riscv64 job**（`grep -i riscv .github/workflows/ci.yml` 零命中），也未引入 riscv64 builder 镜像或入口脚本。
- 结论：**本次只清偿 aarch64，riscv64 维持"仅评估"状态，未被顺带承诺或落地。**

判定：**PASS**（本条由本报告自身承担；三项要求①②③均已白纸黑字写明）。

---

## 夹带与 DCO 总账

```
$ gh api .../compare/v0.7.0-m7...feat/m8-aarch64 --jq '.commits[] | {sha,parents,sob}'
{"parents":1,"sha":"c9ae865","sob":true}
{"parents":1,"sha":"27cc244","sob":true}
{"parents":1,"sha":"124e2d5","sob":true}
{"parents":1,"sha":"6ff8671","sob":true}
{"parents":1,"sha":"f18f2bc","sob":true}
{"parents":1,"sha":"f079fab","sob":true}
```

- 6 个提交**全为非合并提交**（`parents=1`），**全部带 `Signed-off-by:`**（DCO 零漏）。
- 变更文件仅 2 个（见 M8-05），无计划外夹带；本报告为第 3 个文件，且是 M8-5 任务的既定交付。
- 提交主题与内容一一对应：判据入库 → build job → vm-smoke job → 环境修复（romfile/ramfb）→ gettyargs 裁定 → 注释位置修复，无"一提交打天下"。

---

## 已知 Minor 逐条独立核实（记档，不判 FAIL）

1. **ci.yml:421 注释 `apps/login.c:60 goto do_fork` 行号写错** —— 独立复核属实：取上游 `e77143fd` 的 `apps/login.c` 实测，`goto do_fork;` 在 **:66**（:86 才是 `fprintf(stdout, "%s login: ", _hostname);`，与判据一致）。注释性错误，不影响行为。**已于验收执行期间由并发的 M8-6 关门提交 `dd939a0` 订正为 `:66`**（当前 HEAD `c570714` 实测已为 `:66`），本条**不再挂账**，此处保留原始复核记录以备追溯。
2. **实现报告自评 ci.yml diff 153 行 vs 实测 154 行** —— 独立复核属实：difflib opcode 级实测 **+154 / -0**。属自评笔误，未影响判据（不论 153 还是 154，纯插入结论不变）。控制器已裁定并入 M8-6 关门处理。
3. **gettyargs 偏离上游 `aarch64.mk` shell 目标（去掉 `-a local`）** —— 独立复核属实且**认为必要**：上游 `-a local` 走免密直登，打印 `local@livecd:~$` 而**不打印** `login:`，与 M8-02 判据要求的"`login:`（同源 apps/login.c:86）"直接冲突（反例 run 39039782092 已实证）。这是判据内部一致性所要求的取舍，**定性为口径差异、非实现偏差**，控制器已裁定接受；完整口径陈述见 §口径差异与遗留 项 6。
4. **（验收新发现）aarch64 screendump 不具区分力** —— 实测：PASS run（39042486091）与反例 run（39039782092）的 `screen.ppm` **md5 全等**（`0eccb2783cde236b8e86b3906938cdbc`），两帧均 921615 B、payload 仅含 2 种字节值（0 与 0xAA）、非零占比 0.34%（3132/921600）。即该帧在"到达 login 提示"与"已登录进 shell"两种截然不同的状态下**完全一样**，作为证据不携带任何区分信息（对比 x86 侧 M1 A5 记录的 1920×1080 帧：30 字节窗口内 127 个唯一值）。判据中 screendump 明列为"辅助证据、尽力而为、失败不阻塞"（ci.yml:450），核心断言在 serial，故**不判 FAIL**；但建议后续里程碑要么硬化（确认 ramfb 是否真能取到 fbterm 帧、必要时改取帧时机或改断言），要么在判据里明示降级为"仅证明 screendump 通道可用"，避免它被当成启动证据引用。

---

## 口径差异与遗留

1. **本机 git 到 github.com 的 HTTPS 通道不可用**（代理 `CONNECT … 502`、直连超时），而 `api.github.com` 可达。故 `git diff v0.7.0-m7..HEAD -- <path>` 一类判据改以**等价取证**执行：Compare API 取全区间变更文件清单 + 两版文件原文下载 + 字节比对 + pyyaml 对象比对。三者互为交叉验证，且 M8-04 的"diff 为空"已由"字节全等 + 对象全等 + Compare 清单不出现该文件"三重确认，结论强度不低于原判据。
2. **本报告登记进 `docs/index.md`** —— 验收者铁律限制改动仓库文件（唯一例外即本报告本身），故未由本报告自行登记；**已由并发的 M8-6 关门提交 `dd939a0` 补登**（`docs/index.md` +1 行，含"6/6 PASS；aarch64 构建与启动证据，含 M1 行 aarch64 口径差异「转正」声明与 riscv64 仍仅评估记档"）。经复核该引用按 docs/ 相对基准可解析，不悬空。本条**已闭环**。
3. **aarch64 产物不进 Release** —— 差异点 1（控制器预裁定，待用户追认）：维持 M6 三形态（ISO/kernel/ramdisk，x86_64），aarch64 仅作 CI artifact。本验收按此裁定核验，M8-04 判 PASS。
4. **spec-consistency 的里程碑白名单** —— 取证快照 `f079fab` 处元组为 `("M0"…"M7")`，M8 章节不在该门禁保护范围内（被删也不会红）；属门禁增强项、非本里程碑判据，不判 FAIL。**已由并发的 M8-6 关门提交 `dd939a0` 扩到 `("M0"…"M8")`**（当前 HEAD 实测），本条**已闭环**。注意：该改动使 spec-consistency 成为相对 `v0.7.0-m7` **唯一行为发生变化**的旧 job，方向为更严，详见 §事后复核。
5. **本报告只覆盖 M8-01~M8-06** —— M8-6 关门（README 勾选、index 登记、merge --no-ff、tag `v0.8.0-m8`）不在本次验收范围，未执行、未预判。
6. **gettyargs 偏离上游（口径差异，控制器已裁定接受）** —— vm-smoke-aarch64 注入的 `opt/org.toaruos.gettyargs` 为 `/dev/ttyS0 115200 ${TERM:-xterm}`，**去掉了**上游 `base/toaruos/build/aarch64.mk` shell 目标里的 `-a local` 前缀（ci.yml:419-426 已就地记档）。理由：getty `-a local` → `login -f local` → `apps/login.c:66 goto do_fork` 免密直登，**不打印** `apps/login.c:86` 的 `"%s login: "`，与 M8-02 判据"断言 `login:`（与 x86 侧同源）"直接冲突；反例 run 39039782092 已实证该形态下 OS 全启动至 `local@livecd:~$` 却拿不到 `login:`、job 判红。除该前缀外，设备节点（pl011 首串口 `/dev/ttyS0`）、波特率（115200）、TERM（`${TERM:-xterm}`，与 x86 侧同位）均出自 `aarch64.mk`，与 x86 侧 `/dev/ttyS1 115200 xterm` 同构。**这是判据内部一致性所要求的取舍，记为口径差异，不判 FAIL。**
7. **两条已知 Minor 结转（控制器已裁定并入 M8-6 关门处理，本次不修、不判 FAIL）** —— (a) `ci.yml:421` 注释写 `apps/login.c:60 goto do_fork`，实测应为 **:66**（上游 `e77143fd` 核实）；(b) 实现报告自评 ci.yml diff **153 行**，实测 **+154 / -0**。二者均为注释/计数笔误，不影响任何判据（不论 153 还是 154，纯插入结论不变）。详见 §已知 Minor 项 1、2。

---

## 事后复核（并发关门提交后）

验收执行期间，M8-6 关门提交 `dd939a0`（`docs: M8 closeout plumbing (README + index + M8 in milestone gate)`，+2/-2 ci.yml、+2/-1 README.md、+1 docs/index.md）与本报告的提交并发落在 `feat/m8-aarch64` 上，当前 HEAD 为 `c570714`。该提交**不在 M8-01~M8-06 验收范围内**，但为避免本报告留下与 HEAD 不符的陈述，按同一方法（pyyaml job 级对象比对 + 字节比对）对当前 HEAD 复核一次：

| 复核项 | `c570714` 实测 | 与快照 `f079fab` 的关系 |
|---|---|---|
| `release.yml` vs `v0.7.0-m7` | 2441 vs 2441 **字节全等**；2 job 对象全等；`changed=NONE` | 不变，**M8-04 仍成立** |
| `ci.yml` vs `v0.7.0-m7` | `pure_insertion=False`，**added 155 / removed 1** | 快照为 `+154/-0` 纯插入；多出的 1 处 replace 即 `dd939a0` 的白名单行 |
| ci.yml job 集合 | 8 → 10，`removed=[]`，`added=[build-aarch64, vm-smoke-aarch64]` | 不变，**旧八 job 无一被删** |
| ci.yml 旧 job 对象 | **`changed=['spec-consistency']`**（唯一） | 快照为 `changed=NONE`；变化内容为白名单 `("M0"…"M7")` → `("M0"…"M8")` + 注释 `:60`→`:66` |
| `kernel/ tools/ config/ base/toaruos` | `dd939a0` 未触碰 | 不变，**M8-05 仍成立** |

对 **M8-03「旧八 job 零回退」** 的诚实结论：

- **以验收对象 `f079fab` 为准，M8-03 PASS 不变** —— 该处 ci.yml 相对 `v0.7.0-m7` 确为 `+154/-0` 纯插入、旧八 job 对象全等。这是 M8 实现本身的状态，也是本条判据要验的东西。
- **`c570714` 上 ci.yml 不再是"纯插入"** —— 多出的 1 处 replace 来自 M8-6 关门提交，**不是 M8 实现引入的**。
- **该变化不构成回退**：spec-consistency 的唯一改动是把 M8 章节纳入已存在的章节存在性门禁，方向为**更严**（原先 M8 章节被删不会红，现在会红），且未放宽任何断言、未加 `continue-on-error`、未加 suppress。按"方向只许更严"的既有惯例，属门禁增强而非回退。

建议终审时以 `f079fab` 的快照数据裁定 M8-03，并把 `dd939a0` 的门禁增强并入 M8-6 关门的复核范围，避免两条判据互相牵连。

---

## M8-06 转正声明（摘要，供终审直读）

> **spec §4 M1 行（`spec/2026-10-05-etheros-dev-policy.md:191`）「x86-64/aarch64 可构建且 GUI 启动」中的 aarch64 半句：自本里程碑起由"口径差异记档"转为"已达成"。**
>
> - **转正前**：`docs/reports/2026-10-06-m1-acceptance.md` 口径差异段 2 —— "aarch64 构建无独立证据……无 aarch64 构建证据"，缺口记档、未计 FAIL。
> - **转正后**：本里程碑 run `39042486091` —— 构建侧 job `117424593122` 产出 aarch64 四件产物（`aarch64-unknown-toaru-gcc -DKERNEL_ARCH=aarch64`）；启动侧 job `117425051177` 于 `-M virt -cpu cortex-a72` headless 下捕获 `livecd login: `（与 x86 侧字节同源）。反例 run `39039782092` 判红，证明证据非空转。
> - **原文不改写**：`docs/reports/2026-10-06-m1-acceptance.md` 与 spec 原文均实测与 `v0.7.0-m7` **字节一致**，转正声明只在本 M8 报告内做出。
> - **riscv64 仍为仅评估**：ci.yml 无任何 riscv64 job（`grep -i riscv` 零命中），依 spec:100「`arch/riscv64/` 等仅评估留桩」。

---

**总判定：M8-01 ~ M8-06 六条全部 PASS（判定以验收对象 `f079fab` 为准），阻塞缺陷 0；4 条 Minor 均为记档项 —— 1 已由并发的 `dd939a0` 订正不再挂账，2、3 控制器已裁定接受，4（aarch64 screendump 不具区分力）为本次新发现，交控制器 / M8-6 关门任务裁量。**

**STATUS: PASS**

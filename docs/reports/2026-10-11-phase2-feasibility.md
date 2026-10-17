# Phase 2 可行性调研：aarch64 构建 与 OVA 打包

- **调研者**：general-purpose-4（只读调研，未改任何上游文件；本报告与 `docs/index.md` 一行为本次唯一改动）
- **执行日期**：2026-10-17（本机时区；文件名日期沿用 M7 计划窗口 2026-10-11，与 M7-06 验收标准条目对齐）
- **被调研对象**：仓库 `I:/etheros`，分支 `feat/m7-phase2-opening`，HEAD `db62985`（`ci: fix cppcheck argv quoting exposed by second kernel header`）；submodule `base/toaruos` 锁定 `e77143fd14391d880c3ee11c1524252cdcbfd225`
- **依据**：`docs/development/acceptance-standard.md` M7-06 条 + 简报 `.superpowers/sdd/2026-10-05-etheros-m0m1-implementation/briefs/m7-t6-brief.md`
- **口径**：偏严。所有"上游是否支持"结论只写本仓 submodule 工作树里实际读到的文件与 CI 日志实测数字；查不到的一律进「未能证实项」，不编造。
- **方法边界**：只读。未 checkout / 未 reset / 未 `submodule update`；未改 `base/toaruos`（`git submodule status` 显示干净，见下）；未派子代理。

---

## 议题一：aarch64 构建

### 现状

- spec §4 M1 行字面：「**M1 底座基线** | 评估并拉取 ToaruOS（或备选），**x86-64/aarch64 可构建**且 GUI 启动 | 底座派生基线、**文件级许可清单** | `make` 成功；VM 启动见 GUI；许可清单覆盖全仓」（`spec/2026-10-05-etheros-dev-policy.md:191`）。
- M1 实际只落了 x86_64：CI 单架构（`ci.yml` 的 build job 走上游官方镜像 `toaruos/build-tools:1.99.x` + `util/build-in-docker.sh`）。M1 验收以口径差异记档（`docs/reports/2026-10-06-m1-acceptance.md:11`）：「spec M1 目标句含 "x86-64/aarch64 可构建"，但 CI build job 仅构建 x86_64……无 aarch64 构建证据。spec 出口标准字面仅要求 "`make` 成功"，已实证；aarch64 缺口记档供终审裁量，未计为 FAIL 项」。
- EtherOS 侧另有配置把 aarch64 列为第二优先架构：`config/build.toml:5` `arch_priority = ["x86_64", "aarch64"]`（riscv64 仅评估，不进构建）。
- submodule 干净度取证：

```
$ git -C I:/etheros submodule status base/toaruos
 e77143fd14391d880c3ee11c1524252cdcbfd225 base/toaruos (v2.3.0-799-ge77143fd)
$ git -C I:/etheros/base/toaruos status --short | wc -l
0
```

前缀无 `+`、零改动文件 → EtherOS 对上游零本地修改，aarch64 若构建，跑的就是上游原配方。

### 调研过程（查了什么、看到什么）

全部证据取自 submodule 工作树（已初始化，`e77143fd`）与 EtherOS CI 实测：

1. **`build/aarch64.mk` 存在且是完整构建配方**（非占位）：`ARCH=aarch64`、`TARGET=aarch64-unknown-toaru`；`system` 目标产出 `misaka-kernel ramdisk.igz bootstub kernel8.img`；带 `run` / `shell`（headless 串口）/ `run-vga` / `debug` 四个 QEMU 目标（`qemu-system-aarch64 -M virt -cpu cortex-a72`，`ramfb` + virtio 键鼠 + AC97）。第 64-65 行：内核/ramdisk 经 fw_cfg 注入（`opt/org.toaruos.kernel` / `opt/org.toaruos.initrd`）；第 81 行 headless getty 参数 `-a local /dev/ttyS0 115200`。
2. **`kernel/arch/aarch64/` 目录完整**：`arch.c bootstub/ context.S dtb.c entry.S fwcfg.c gic.c irq.S link.ld main.c mmu.c pl011.c rpi.c rpi400/ rpi_miniuart.c smp.c traceback.c virtio.c` —— 与 x86_64 并列的一级 arch 端口（另有 `rpi400/` 树莓派子目标）。
3. **官方 aarch64 Docker 构建脚本存在**：`util/build-in-docker-aarch64.sh`，内部为 `make ARCH=aarch64 util/local/bin/kuroko && make ARCH=aarch64 base/lib/libc.so && make ARCH=aarch64 -j4`。
4. **上游自带 aarch64 CI**：`base/toaruos/.github/workflows/aarch64.yml` —— `docker pull toaruos/build-tools:aarch64` → `util/build-in-docker-aarch64.sh` → 上传 `aarch64-virt`（misaka-kernel / ramdisk.igz / bootstub）与 `aarch64-rpi400`（kernel8.img）两个 artifact。即上游用一条独立镜像 tag 走 aarch64，与 x86_64 的 `1.99.x` 平行。
5. **README 佐证**：「In early 2022, the OS was further ported to aarch64.」（`base/toaruos/README.md:19`）。
6. **EtherOS 侧成本锚点（CI 实测，run `39031024713`，2026-10-17）**：build job（含 docker pull + 完整 x86_64 构建）**2m21s**；vm-smoke（QEMU TCG 启动取证）**23s**；整 run 2m48s。`gh run view 39031024713 --json jobs` 逐 job 输出见工作区报告。
7. **M1 底座调研报告 §4 早有同款证据**（`docs/reports/2026-10-06-toaruos-survey.md:76-81`）：`build/aarch64.mk`、`kernel/arch/aarch64/`（含 RPi400）、CI `aarch64.yml` 均在，结论「可构建 aarch64：满足」。

### 成本量级

| 项 | 量级 | 依据 |
|---|---|---|
| 上游源码支持 | **零成本**（已存在于锁定 SHA 的工作树） | 上述 1-5 |
| EtherOS 代码改动 | **零**（构建发生在 `base/toaruos` 内，EtherOS 自有树 `kernel/` 为不参与构建的契约桩，见 `docs/index.md:23`） | 只读调研确认 |
| CI 增量（建议的最小两步） | `build-aarch64` job ≈ 2-3 min + `vm-smoke-aarch64` job ≈ 1-3 min（TCG 估计）≈ **+4-6 min 机器时/push**；八 job 并行，wall-clock 约 +3-4 min | x86_64 build 实测 2m21s 锚定；aarch64 `system` 目标不含 ISO 打包（无 xorriso），只会更短；冒烟 TCG 时长为估计值 |
| 人力 | 复刻 build job 配方改镜像/脚本名 + 写冒烟断言：**半天以内**（纯 ci.yml 增量，两份文件参照物都在） | 上游 aarch64.yml + EtherOS build/vm-smoke 两 job 现成 |
| 持续维护 | 与上游镜像 tag 共存亡；无新增脚本债 | — |

**不建议**现在做的（防范围蔓延）：aarch64 产物进 `release.yml`（维持 M6 三形态发布，由用户裁决）；riscv64（spec 明示仅评估）。

### 结论：**建议做**（Phase 2 清偿，分两步，只动 `ci.yml`，不动 `release.yml`、不动 submodule）

一句话理由：**上游在锁定 SHA 上 aarch64 支持是完整且经官方 CI 背书的，EtherOS 侧唯一缺口是"没有自己的构建证据"，而补这个证据的全部成本是一条 CI job 的几分钟机器时 —— 这是把 spec §4 M1 目标句从"口径差异记档"变成"已达成"的最便宜窗口。**

分两步（均为未来任务的落地建议，**M7-06 不落地**）：

1. **证据清偿**：`ci.yml` 新增 `build-aarch64` job —— 复刻现有 build job，仅换 `toaruos/build-tools:aarch64` 镜像与 `util/build-in-docker-aarch64.sh` 脚本；收集 `misaka-kernel` / `ramdisk.igz` / `bootstub`（+ `kernel8.img`）上传 artifact。
2. **可启动性背书**：新增 `vm-smoke-aarch64` job —— 按 `build/aarch64.mk` `shell` 目标：`qemu-system-aarch64 -M virt -cpu cortex-a72 -kernel bootstub -append "root=/dev/ram0 migrate start=--headless"` + fw_cfg 注入 kernel/initrd + gettyargs `-a local /dev/ttyS0 115200 xterm`，`-serial file:` 捕获并断言 `login:`（与 x86_侧同一断言字符串，`apps/login.c:86` 同源）。`timeout-minutes: 20` 余量充足。

### 依据引用

- `spec/2026-10-05-etheros-dev-policy.md:191`（M1 行目标句含 aarch64）、`:36`（§2.1 目标架构「优先 x86-64 与 aarch64（ToaruOS 已覆盖）」）、`:226`（风险 3「ToaruOS 官方覆盖 x86-64 与 aarch64」）
- `docs/reports/2026-10-06-m1-acceptance.md:11`（口径差异段 2：aarch64 无独立构建证据，记档供终审裁量）
- `docs/reports/2026-10-06-toaruos-survey.md:76-81`（M1 底座调研的 aarch64 证据）
- `base/toaruos/build/aarch64.mk`、`base/toaruos/kernel/arch/aarch64/`、`base/toaruos/util/build-in-docker-aarch64.sh`、`base/toaruos/.github/workflows/aarch64.yml`、`base/toaruos/README.md:19`
- `config/build.toml:5`（arch_priority 第二项）

---

## 议题二：OVA 打包

### 现状

- spec §4 M6 行字面含「ISO/VM/OVA」（`:196`）；§5 发布段「`tag` 触发 `release.yml` → 构建 ISO/VM/OVA → 上传 GitHub Release」（`:216`）。
- M6 已裁定 **OVA 降级 Phase 2**（差异点 8，YAGNI），`RELEASE_NOTES.md:39-41` 白纸黑字：「**OVA 尚未支持（降级至 Phase 2，差异点 8）**……不做 vmdk/ovf 打包（YAGNI）。如需虚拟机镜像，请直接使用 `image.iso` 自行安装或转换……**不以任何形式声称 OVA 已支持**。」
- 现状产物（v0.6.0-m6 发布资产实测，`docs/reports/2026-10-06-m6-acceptance.md:236-238`）：`image.iso` 7,593,984 B（≈7.59 MB，BIOS+EFI 双引导）、`misaka-kernel` 274,384 B（≈274 KB）、`ramdisk.igz` 6,772,626 B（≈6.77 MB），**合计 ≈14.64 MB**。可启动性由 `ci.yml` vm-smoke（QEMU headless 捕获 `login:`）背书。
- `release.yml` collect 步骤只收 `*.iso` / `misaka-kernel` / `*.igz` 三类，无 vmdk/ovf 产物（M6-05 反向检查已实证）。

### 调研过程（查了什么、看到什么）

1. **ISO → OVA 的标准步骤链**（业界通行的 OVF/OVA 形态，非本仓发明）：① 得到可启动磁盘/光盘介质；② `qemu-img convert -O vmdk -o subformat=monolithicSparse`（VirtualBox 兼容；VMware 亦接受 VMDK/VHD）；③ 手写 OVF 描述文件（VirtualHardware、存储控制器、光驱、启动顺序）；④ 对包内每个文件算 SHA1 生成 `.mf` 清单；⑤ `tar` 打成 `.ova`。导入 VirtualBox/VMware 时二者消费 OVF 中的磁盘引用。
2. **上游没有可复刻的 OVA 目标**：`util/` 下的 `mkdisk.sh` 是 FAT 磁盘镜像工具（`mkfs.fat` + 灌文件，服务于 EFI FAT 镜像），**不是** OVA/磁盘安装镜像工具；上游无 ovf/vmdk/ova 相关目标或模板。若做，模板是 EtherOS 侧新稿。
3. **体积上限已从官方文档核实**（GitHub Docs《About releases》）：单个 Release 最多 1000 个资产；**每个文件必须 < 2 GiB**；**Release 总大小与带宽用量无限制**。→ 14.6 MB 量级再翻一倍也完全不是门槛；"GitHub Release 上限/流量成本"不构成反对理由，但也构不成支持理由。
4. **膨胀量级取决于形态选择**：以 ISO 作光盘介质 + monolithicSparse VMDK，OVA ≈ ISO 量级 + 十几 KB 描述文件，Release 总量 14.6 MB → ≈23 MB；若图省事做"完整 VM 磁盘"且用非稀疏/固定容量格式（如 2 GiB 虚拟磁盘），OVA 会到 GB 级 —— 形态选择是体积的关键变量。
5. **验证债**：VirtualBox 侧可在 GH runner 上自动化（装 `virtualbox` 包 + `VBoxManage importvm` 无头导入验证，安装耗时约 2-4 min，估计值）；**VMware 侧无法在 runner 上自动化**（闭源、runner 不可装），只能人工抽查一次 —— 双 hypervisor 承诺意味着永久的人工验证尾巴。

### 成本量级

| 项 | 量级 |
|---|---|
| 实现（最小路径，若将来做） | qemu-img 转换 + 单 OVF 模板 + mf + tar ≈ **半天**；`release.yml` collect/publish 各加一行即自动带出（发布通道已通） |
| CI 时间增量 | 转换+打包 ≈ 秒级；若加 VirtualBox 导入冒烟 ≈ +2-4 min/发布（仅 tag 触发，不影响每次 push 的 CI） |
| Release 体积增量 | ≈ +8 MB（≈23 MB 总量），远低于 2 GiB/文件上限；总量与带宽无官方限制 |
| 持续维护 | OVF/VMDK 模板 + 双端导入验证（VMware 人工）为长期债；上游不提供对应目标，无同步红利 |

### 收益面

- 目标用户（想在 VMware/VirtualBox 里"双击导入"的人）与 ISO 用户**高度重叠**：`image.iso` 是 BIOS+EFI 双引导可启动镜像，两个 hypervisor 里"新建 VM → 挂 ISO → 启动"即可完成同样的事，只多三四步手工操作。`RELEASE_NOTES.md:40` 已经给出这句零成本指引（"请直接使用 `image.iso` 自行安装或转换"）。
- 当前阶段（Phase 2 开门、`v0.6.0-m6` prerelease、用户基数小）**没有新的需求信号**推翻 M6 的 YAGNI 记档；本次调研亦未发现任何用户侧证据（未检索 issue，仓库早期无外部反馈记录）。

### 结论：**建议不做**（维持 M6 差异点 8 降级；设触发条件，留最小路径备查）

一句话理由：**OVA 省下的只是 ISO 用户三四步手工操作，代价却是 vmdk/ovf 模板加 VirtualBox/VMware 双端导入验证的长期维护债，收益与成本在当前阶段严重不对称 —— 把 RELEASE_NOTES 里那句 ISO 指引维护好，就是现阶段的最优解。**

触发条件（满足其一再重议）：出现真实用户的 OVA 导入需求反馈；Phase 3 稳定版（v1.0.0）发布前统一产物形态；上游出现官方 OVA/磁盘镜像目标可复刻。

若触发，最小实现路径（供未来任务直接取用）：`qemu-img convert -O vmdk -o subformat=monolithicSparse image.iso etheros.vmdk`（ISO 作光盘介质，避免制造 GB 级磁盘镜像）→ 单 OVF 模板（声明光驱 + 启动顺序光盘优先）→ `sha1sum` 生成 `.mf` → `tar` 成 `etheros.ova`；`release.yml` collect 步骤加一行；CI 加 `VBoxManage importvm` 无头验证；VMware 侧人工验证一次并记档。

### 依据引用

- `spec/2026-10-05-etheros-dev-policy.md:196`（M6 行）、`:216`（§5 发布段）
- `RELEASE_NOTES.md:33-41`（OVA 降级记档 + ISO 替代指引）
- `docs/reports/2026-10-06-m6-acceptance.md:236-238`（资产实测体积）、`:304-317`（M6-05 OVA 降级 PASS 记档）
- GitHub Docs《About releases》（资产 2 GiB/文件、总量与带宽无限制，2026-10-17 检索）
- `base/toaruos/util/mkdisk.sh`（上游仅 FAT 镜像工具，无 OVA 目标）

---

## 未能证实项（诚实边界）

| # | 项 | 状态与原因 |
|---|---|---|
| 1 | `toaruos/build-tools:aarch64` 镜像可拉取、可构建成功 | **未能本地证实**：本机环境无 docker（`docker --version` 退出 127），不拉镜像、不跑构建。依据仅为上游 `base/toaruos/.github/workflows/aarch64.yml` 的字面使用。一次未来 CI 实跑即可证实或证伪 —— 这本身是"建议做"的论据之一。 |
| 2 | aarch64 QEMU TCG 冒烟实测时长 | **未能证实**：本机无 QEMU、无 KVM。报告中 1-3 min 为按 x86_64 侧 23s 与 arm TCG 一般倍数的**估计值**，已标注。 |
| 3 | VMware Workstation 导入 OVA 的实际体验 | **未能证实**：闭源软件、本机与 runner 均不可装。OVF/VMDK 跨 VMware 兼容性按业界通行形态论述，未实测。 |
| 4 | 上游 `util/build-toolchain.sh` 无 aarch64 命中 | **已证实为负面事实**：该脚本只构建 x86_64 工具链；上游 aarch64 镜像的工具链来源不在本仓可见范围内（镜像内部构建方式未证实）。不影响结论（镜像由上游官方提供）。 |
| 5 | 是否存在等 OVA 的用户 | **未能证实（且无证据表明存在）**：未检索外部渠道；M6 的 YAGNI 记档是现有唯一裁定记录。 |

---

## 与 M7 验收的关系

- **M7-06 对齐**：`docs/development/acceptance-standard.md:105` 要求「可行性调研：`docs/reports/2026-10-11-phase2-feasibility.md` 给出 aarch64 构建与 OVA 打包的结论（建议做/不做）、依据与成本量级；**M7 不落地实现**」。本报告即该交付物：议题一结论**建议做**（附两步最小落地路径）、议题二结论**建议不做**（附触发条件），均给出依据与成本量级；**M7 不落地实现**由下条零改动证明。
- **本次交付对 `.github/workflows/` 的增量 diff 为空**：落稿时实测 `git diff db62985 -- .github/workflows/` 为 0 字节（`--stat` 亦 0 行）；M7-06 提交只含两个文档文件，commit 后 `git diff db62985..HEAD -- .github/workflows/` 同值（回执见工作区报告 `task-m7-6-report.md`）。

- `git diff v0.6.0-m6..HEAD -- .github/workflows/` **非空**，但其内容全部来自 M7-06 之前已合入的 M7 任务交付（非本次调研所为），逐 commit 归属如下：

| 提交 | 归属 | 内容 |
|---|---|---|
| `763905d` | M7-01 | spec-consistency 硬化（行首锚定 + 空候选集断言） |
| `63350fe` | M7-02 | lint 空集断言 + 里程碑元组扩到 M7 |
| `ee41bf7` | M7-05 | plugin-schema job 末尾追加 load plan smoke |
| `db62985` | M7-5 连带修复 | cppcheck argv quoting（第二个内核头触发） |

  上述改动的门禁零回退属性由各自任务的验收负责（acceptance-standard M7-01/02/05/07）；M7-06 既不新增也不修改任何 CI job 与 release 产物逻辑。完整 diff 输出如下（已逐 hunk 核对：无新增 job、无 release 产物逻辑变更、八 job 名称与 M6 时一致）：

<details>
<summary>git diff v0.6.0-m6..HEAD -- .github/workflows/（完整输出，83 行，逐字）</summary>

```diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 958781b..80b7660 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -65,6 +65,12 @@ jobs:
           python3 tools/route_plugins.py --run hello-plugin
           python3 tools/route_plugins.py --run douyin
 
+      - name: Load plan smoke (M7 load_plugins)
+        run: |
+          python3 tools/load_plugins.py | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['status']=='plan-only'; print('LOAD PLAN OK', len(d['enabled']))"
+          printf '[plugins]\nenabled = ["no-such-plugin"]\n' > /tmp/bogus.toml
+          ! python3 tools/load_plugins.py --config /tmp/bogus.toml
+
   license:
     name: license (reuse lint, submodules excluded per spec 5 / risk 2)
     runs-on: ubuntu-latest
@@ -120,13 +126,24 @@ jobs:
       - name: Install tools
         run: sudo apt-get update && sudo apt-get install -y --no-install-recommends clang-format cppcheck && python3 -m pip install --quiet pyflakes
       - name: clang-format (C under kernel/ tools/ plugins/ only)
-        run: find kernel tools plugins \( -name '*.c' -o -name '*.h' \) -type f | xargs -r clang-format --dry-run --Werror
+        # M7-3 空集断言:旧写法 `find … | xargs -r …` 在目标集为空时 xargs 不执行
+        # 任何东西、退出 0 —— 门禁静默通过(kernel/ tools/ plugins/ 被改名或清空
+        # 也不会红)。改为先收集列表并断言非空,再把列表喂给工具。
+        # 未放宽 --Werror;find 起点仍严格限定 kernel tools plugins(结构性排除 base/)。
+        run: |
+          FILES=$(find kernel tools plugins \( -name '*.c' -o -name '*.h' \) -type f)
+          test -n "$FILES" || { echo "::error::no C/H files found under kernel/ tools/ plugins/"; exit 1; }
+          printf '%s\n' "$FILES" | xargs clang-format --dry-run --Werror
       - name: cppcheck (kernel/)
         # 目录形式实证失效(run 38069483688):"could not find or open any of the
         # paths given." —— kernel/ 下只有 .h,cppcheck 扫目录时找不到可检文件,
         # 属"找不到文件"而非真实告警,故改用显式文件列表(风险 A 预裁定)。
         # 未放宽 --error-exitcode,未加 --suppress 掩盖真实告警。
-        run: find kernel \( -name '*.c' -o -name '*.h' \) -print0 | xargs -0 -r cppcheck --language=c --enable=warning --error-exitcode=1
+        # M7-3 空集断言:同上,目标集为空必须先红而非静默通过。
+        run: |
+          FILES=$(find kernel \( -name '*.c' -o -name '*.h' \) -type f)
+          test -n "$FILES" || { echo "::error::no C/H files found under kernel/"; exit 1; }
+          printf '%s\n' "$FILES" | xargs -d '\n' cppcheck --language=c --enable=warning --error-exitcode=1
       - name: pyflakes (python tools)
         run: python3 -m pyflakes tools/*.py plugins/compat/stub-runtime/*.py
 
@@ -147,17 +164,35 @@ jobs:
           fails = []
           # (a) index dangling check: try docs/-relative then repo-root-relative.
           # Backticked snippets containing whitespace are command lines, not paths.
+          # M5 裁定 1(保留,不可删):含空白字符的反引号片段按命令行跳过,否则
+          # index.md 里的 `python3 tools/validate_plugins.py` 会被当成路径而假红。
           text = (docs / "index.md").read_text(encoding="utf-8")
+          scanned = 0
+          candidates = 0
           for p in sorted(set(re.findall(r'`([^`]+?\.(?:md|py|json|toml|sh))`', text))):
+            scanned += 1
             if any(ch.isspace() for ch in p):
               continue
+            candidates += 1
             cand = p[2:] if p.startswith("./") else p
             if not (docs / cand).exists() and not (root / cand).exists():
               fails.append(f"docs/index.md references missing doc: {p}")
+          # M7-01 空候选集不再静默通过:0 个候选意味着正则失效或 index.md 被清空,
+          # 旧写法下 0 次循环直接 OK(静默通过)。此处必须 FAIL。
+          if candidates < 1:
+            fails.append(f"docs/index.md yielded 0 path candidates ({scanned} backticked snippet(s) scanned); regex or index content broke")
           # (b) acceptance-standard milestone sections present
-          std = (docs / "development" / "acceptance-standard.md").read_text(encoding="utf-8")
-          for m in ("M0", "M1", "M2", "M3", "M4", "M5"):
-            if f"## {m}" not in std:
+          # M7-01 行首锚定:旧写法 f"## {m}" not in std 是子串匹配,文档里的
+          # `## M1+ · 占位` 会让真正的 `## M1` 章节被删也放行(门禁形同虚设)。
+          # 定稿形式:整行等于 `## {m}`,或以 `## {m} ` (结尾带空格)开头。
+          # 于是 `## M1+ · 占位` 二者皆不满足(不再掩盖真 M1 的缺失),
+          # 而 `## M1 · 底座基线(归档...)` 满足后者,仍被认可。
+          std_lines = (docs / "development" / "acceptance-standard.md").read_text(encoding="utf-8").splitlines()
+          # M7-01 白名单扩到 M7:旧元组停在 M5,M6/M7 两个已入库章节不受本道门禁
+          # 保护(删了也不红)。二者当前确实存在于 acceptance-standard.md,扩了是
+          # 门禁增强、不会假红。方向只许更严。
+          for m in ("M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7"):
+            if not any(line == f"## {m}" or line.startswith(f"## {m} ") for line in std_lines):
               fails.append(f"acceptance-standard.md missing section: {m}")
           # (c) spec anchor referenced by .etherkit/AGENTS.md
           agents = (root / ".etherkit" / "AGENTS.md").read_text(encoding="utf-8")
```

</details>

  （以上为 `git diff v0.6.0-m6..HEAD -- .github/workflows/` 逐字输出（83 行）；`release.yml` 无任何 hunk。）
- **本地验证**（托管 python `3.13.12`，全绿）：`tools/check_kernel_boundary.py` 通过；`tools/validate_plugins.py` 通过；`tools/load_plugins.py > /dev/null` OK（`status=plan-only`）；spec-consistency index 悬空检查复跑 `spec consistency: OK`（本报告入库行与 M6 行修正均不悬空）。完整输出见工作区报告 `task-m7-6-report.md`。
- **CI**：本次推送后的 run（八 job）结果见工作区报告回执。

---

融汇万端（Connect the Unconnectable.）

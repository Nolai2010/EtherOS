# M1 独立验收报告（T14）

- 日期：2026-10-06 ｜ 验收者：acceptance-checker（T14，独立上下文，只读核验）
- 仓库：I:/etheros ｜ 分支：feat/m0-m1 ｜ HEAD：1318a54（1318a54839fc373f1c27d29e1ff5d56fb8770c1f）
- 依据：brief `.superpowers/sdd/2026-10-05-etheros-m0m1-implementation/briefs/t14-m1-acceptance.md`；spec `spec/2026-10-05-etheros-dev-policy.md` §4 M1 行
- 口径：偏严——逐条实跑命令取证据，不接受口头声明/报告转述；假通过=未达

## 口径差异（brief 要求记档段）

1. **acceptance-standard.md 无 M1 章节**：该文件仅有 M0 章节与 "M1+ 占位"（声明 M1 验收标准"在对应里程碑启动时由用户确认后追加"，至今未追加）。按 brief 规则"若与 spec §4 M1 行有出入以 spec 为准"，本验收直接以 spec §4 M1 行（目标：评估并拉取 ToaruOS；产出：底座派生基线 + 文件级许可清单；出口标准：`make` 成功；VM 启动见 GUI；许可清单覆盖全仓）为验收依据，逐条映射为 A1–A9 实测项。
2. **aarch64 构建无独立证据**：spec M1 目标句含 "x86-64/aarch64 可构建"，但 CI build job 仅构建 x86_64（上游 builder 镜像 `toaruos/build-tools:1.99.x` 默认目标，产出 `misaka-kernel` 为 x86_64-pc-toaru），无 aarch64 构建证据。spec 出口标准字面仅要求 "`make` 成功"，已实证；aarch64 缺口记档供终审裁量，未计为 FAIL 项（依据：出口标准与 brief 核验方式均未列 aarch64 实测）。
3. **"VM 启动见 GUI" 的证据口径**：以 CI headless QEMU 双串口捕获 + QMP screendump 为证据（fbterm 内核控制台帧），非人工目视 GUI 桌面。该选型已在台账 Task 11 裁定（本机无 QEMU、CI headless），本验收按此口径核验证据真实性。
4. **REUSE lint 降级**：本机无 `reuse` 模块（`python -m reuse lint` → `No module named reuse`），按 brief 预案降级为 "REUSE.toml + LICENSES/ 存在 + SPDX 行抽查"。

## 逐条核验

### A1 上游 submodule 锁定（spec：评估并拉取 ToaruOS / 底座派生基线）

命令：
```
git -C I:/etheros submodule status
git -C I:/etheros diff --submodule=log base/toaruos
git -C I:/etheros/base/toaruos status --porcelain
```
证据（原文）：
```
 e77143fd14391d880c3ee11c1524252cdcbfd225 base/toaruos (v2.3.0-799-ge77143fd)
---DIFF---
（空输出）
---PORCELAIN---
（空输出）
```
判定：**PASS** —— 锁定于 e77143fd14391d880c3ee11c1524252cdcbfd225，与 brief 预期 SHA 一致；无本地改动、无漂移。

### A2 CI 最新 run 三 job 全绿（spec：CI 构建通道）

命令：
```
gh run list -R Nolai2010/EtherOS --branch feat/m0-m1 --limit 3
gh api repos/Nolai2010/EtherOS/actions/runs/37387961480 --jq '{head_sha,head_branch,conclusion}'
```
证据（原文）：
```
completed	success	ci: add vm-smoke QEMU headless boot evidence job (T11)	...	37387961480	2m55s
{"conclusion":"success","head_branch":"feat/m0-m1","head_sha":"1318a54839fc373f1c27d29e1ff5d56fb8770c1f"}

✓ etherkit single-source consistency in 6s (ID 112025943035)
✓ build ToaruOS base (upstream builder image) in 2m25s (ID 112025943314)
✓ vm smoke (QEMU headless boot evidence) in 24s (ID 112026712528)
```
判定：**PASS** —— 最新 run 37387961480 对应 HEAD 1318a54，consistency + build + vm-smoke 三 job 全绿。

### A3 `make` 成功（spec 出口标准①；本机 Windows 不可构建属已知事实 Ruling 4，构建证据取 CI）

命令：
```
gh run view --job=112025943314 -R Nolai2010/EtherOS --log
```
证据（原文摘录，build job 日志尾部）：
```
Writing to 'stdio:image.iso' completed successfully.
cat boot/mbr.sys image.dat > image.iso
-rw-r--r--  1 runner runner 7589888 Oct  5 23:23 image.iso
-rwxr-xr-x  1 runner runner  274384 Oct  5 23:23 misaka-kernel
```
判定：**PASS** —— 上游 builder 镜像内完成 base OS 构建，产出 7.6MB 可启动 ISO 与 misaka 内核二进制。

### A4 CI artifacts 可查

命令：
```
gh api repos/Nolai2010/EtherOS/actions/runs/37387961480/artifacts --jq '.artifacts[] | {name,size_in_bytes,expired}'
```
证据（原文）：
```
{"expired":false,"name":"vm-smoke-evidence","size_in_bytes":16828}
{"expired":false,"name":"etheros-boot-artifacts","size_in_bytes":13668955}
```
判定：**PASS** —— `etheros-boot-artifacts` 与 `vm-smoke-evidence` 双件均在且未过期。

### A5 VM 冒烟证据：serial 真实 + screendump 真帧（spec 出口标准②"VM 启动见 GUI"，口径见差异段 3）

命令：
```
gh run download 37387961480 -R Nolai2010/EtherOS -n vm-smoke-evidence -D .
xxd serial-com2.log
gh run view --job=112026712528 -R Nolai2010/EtherOS --log
```
证据（原文）：
- artifact `serial-com2.log` 十六进制（含 ANSI 光标序列前缀）：
```
1b5b 731b 5b31 3030 303b 3130 3030 481b 5b36 6e1b 5b75 6c69 7665 6364 206c 6f67
696e 3a20
```
  即 `\x1b[s\x1b[1000;1000H\x1b[6n\x1b[u` + `livecd login: `
- 证据源头（`base/toaruos/apps/login.c:86`）：`fprintf(stdout, "%s login: ", _hostname);`（hostname=livecd）
- CI job 日志断言（原文）：`BOOT EVIDENCE OK: userspace login reached on serial (COM2)`
- `screen.ppm` 头：`P6\n1920 1080\n255\n`，2,073,600 像素；采样字节范围 0–187、30 字节窗口 127 个唯一值 → 非全黑、非平凡帧
判定：**PASS** —— serial 证据与 artifact、CI 日志、上游源码三点互证一致；screendump 为真实渲染帧。

### A6 VM 冒烟报告落盘：docs/reports/m1-vm-smoke.md（brief 核验方式明文要求）

命令：
```
ls -la I:/etheros/docs/reports/
Glob **/*vm-smoke* （全仓）
```
证据（原文）：
```
2026-10-06-m0-acceptance.md
2026-10-06-toaruos-survey.md
（无 m1-vm-smoke.md；全仓无任何 *vm-smoke* 文件）
```
判定：**FAIL** —— 报告文件不存在。VM 冒烟的执行证据本身已在 CI 中齐备（见 A5），但 brief 要求的"docs/reports/m1-vm-smoke.md 存在、含 serial 真实摘录、与 CI evidence artifact 对得上"未满足。

### A7 Makefile 转发：`make check` 本地实跑

命令：
```
cd I:/etheros && make check; echo EXIT=$?
```
证据（原文）：
```
bash tools/check-skeleton.sh
skeleton check: OK
EXIT=0
```
判定：**PASS** —— 断言全过，exit 0。

### A8 文件级许可清单（spec：M1 关键产出 + 出口标准③"许可清单覆盖全仓"；§6 风险 2 诚实口径）

命令：
```
读 docs/license-inventory.md 全文
```
证据（原文摘录）：
- 覆盖面：自有内容 MIT（REUSE.toml `path=["**"]`）、许可文件本身 CC0-1.0、底座 UIUC/NCSA 原样保留、kuroko MIT（含第二版权人）、binutils-gdb/gcc GPL-3（构建期边界"待法务口径确认，非定论"）、DejaVu 字体列为缺口追踪项
- 结论段（原文）：`**宣布"纯 MIT"尚缺,暂不宣布**(spec §6 风险 2 口径:M1 只出清单)`
判定：**PASS** —— 覆盖 MIT/NCSA/GPL/DejaVu 边界，未宣称纯 MIT，开放项如实记档。

### A9 REUSE 基线（brief 预案：lint 降级，原因见差异段 4）

命令：
```
python -m reuse lint  → No module named reuse（降级）
ls LICENSES/ && head -30 REUSE.toml
grep -rl "SPDX-License-Identifier" …（排除 base/toaruos）
```
证据（原文）：
```
MIT.txt
version = 1
[[annotations]] path = ["**"] … SPDX-License-Identifier = "MIT"
[[annotations]] path = ["LICENSE","NOTICE","LICENSES/**"] … SPDX-License-Identifier = "CC0-1.0"
.agent/rules/04-license-workflow.md（等 5+ 文件含 SPDX 头）
```
判定：**PASS（降级核验）** —— REUSE.toml + LICENSES/MIT.txt 存在且映射完整，SPDX 行抽查命中。

## 结论

- 实测项总数：**9**（A1–A9）
- PASS：**8** ｜ FAIL：**1**（A6）
- FAIL 缺口清单：
  - **A6**：`docs/reports/m1-vm-smoke.md` 未落盘。缺什么：一份入库的报告文件，内含 serial 真实摘录（可直接引用 artifact `serial-com2.log` 的 `livecd login: ` 字节序列与 CI 日志 `BOOT EVIDENCE OK` 断言），并与 run 37387961480 的 `vm-smoke-evidence` artifact 对应。修复建议：由实现者补写该报告（证据已全部在 CI 侧存在，仅文档化缺失）。
- 附带记档（非 FAIL）：aarch64 无独立构建证据（口径差异段 2）；acceptance-standard.md M1 章节缺失（口径差异段 1）。

STATUS: FAIL

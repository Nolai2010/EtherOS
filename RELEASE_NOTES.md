# EtherOS 发布说明

## ① v0.6.0-m6 —— Phase 1 收官

`v0.6.0-m6` 是 **Phase 1 的收官里程碑**:打通"打 tag → 自动构建 → GitHub Release"的发布通道,
此前三个里程碑的成果在本版本一并通过该通道对外交付。

本版本包含:

- **M4 内建插件归位**:`plugins/builtin/` 四个内建插件实体(shell / files / settings / mon)落位,
  `CORE_MANIFEST.toml` 收紧为仅声明内核边界,`tools/check_kernel_boundary.py` 常驻守卫内核边界。
- **M5 CI 六项点亮**:ci.yml 补齐 license / dco / lint / spec-consistency 四项后达 **八 job 全绿**
  (etherkit-consistency、plugin-schema、license、dco、lint、spec-consistency、build、vm-smoke)。
- **M6 发布通道**:新增 `.github/workflows/release.yml`,`on push tags 'v*'` 触发构建并发布 GitHub Release;
  另支持 `workflow_dispatch`(默认 `dry_run=true`)只出产物、不建 Release,用于发布前演练。

**产物清单**(三形态,均来自 `toaruos/build-tools:1.99.x` + `util/build-in-docker.sh` 同一配方):

| 产物 | 说明 |
|---|---|
| `image.iso` | 可启动光盘镜像(BIOS + EFI 双引导);与 ci.yml `vm-smoke` job 消费的 ISO 同源同配方 |
| `misaka-kernel` | 内核映像 |
| `*.igz` | initrd / ramdisk |

## ② 版本策略(语义化版本惯例)

- 本仓库延续 **`v0.x.0-mN`** 版本惯例:次版本号 `x` 对应里程碑序号,`-mN` 为该里程碑的收官标记
  (如 M6 关门 tag 为 `v0.6.0-m6`)。
- **`-mN` 后缀在 semver 中即预发布形态**,因此凡 `-mN` 标签创建的 GitHub Release **一律标记 prerelease**
  (`--prerelease`),不冒充正式版。
- **`v1.0.0` 不在本版本切换**:是否切 `v1.0.0` 留待 Phase 1 收官后由用户决策,本版本不做预判、不提前占用。

## ③ 产物形态与降级记档

**已支持的三形态产物**:`image.iso`(可启动 ISO)、`misaka-kernel`(内核)、`*.igz`(ramdisk)。
可启动性由 ci.yml `vm-smoke` job 背书:该 job 以 QEMU headless 启动同一配方产出的 ISO,
捕获 serial 上的 `login:` 作为内核与用户态均已真正跑起来的证据。

**OVA 尚未支持(降级至 Phase 2,差异点 8)**:本次发布 **不提供 OVA / VMDK / OVF 虚拟机镜像**,
不做 vmdk/ovf 打包(YAGNI)。如需虚拟机镜像,请直接使用 `image.iso` 自行安装或转换。
此项在验收标准 `docs/development/acceptance-standard.md` M6-05 条与验收报告中均如实记档,**不以任何形式声称 OVA 已支持**。

---

## ④ 后续里程碑摘要

- **v0.7.0-m7(Phase 2 开门)**:门禁硬化(spec-consistency 章节头行首锚定 + 空候选集断言、lint 空集断言)、`CONTRIBUTING.md`、
  装载契约(`kernel/interfaces/loader_if.h` + `loader-contract.md`)与用户态装载计划生成器 `tools/load_plugins.py`
  (输出 `status: "plan-only"`,**如实声明未真正装载**)、aarch64/OVA 可行性调研。
- **v0.8.0-m8(第二架构)**:CI 新增 `build-aarch64` 与 `vm-smoke-aarch64` 两 job(十 job 全绿)。
  spec §4 M1 行「x86-64/**aarch64** 可构建」的 aarch64 半句**由"口径差异记档"转为"已达成"**
  (转正声明见 `docs/reports/2026-10-17-m8-acceptance.md`;M1 验收报告原文按"版本化不回改"惯例未改写)。
  riscv64 仍为**仅评估**,未进构建。aarch64 产物**不进发布通道**(仍为 x86_64 三形态)。
- **v0.9.0-m9(schema v2,破坏性变更)**:
  - **⚠️ 破坏性变更**:插件 manifest 契约由 **v1 升到 v2**,`plugin.schema.json` 的 `schema_version.const` 由 `"1"` 改为 `"2"`;
    **v2 不做双版本共存** —— `schema_version` 为 `"1"` 的 manifest 会被 `tools/validate_plugins.py` **明确拒绝**并给出迁移提示。
    迁移方式:把 manifest 里的 `"schema_version": "1"` 改为 `"2"` 即可(字段集合除新增可选 `dependencies` 外与 v1 逐字相同)。
    依据 spec §2.4「任何字段变更 = schema_version 变更」。
  - **新增可选字段 `dependencies`**:插件 id 数组(元素命名规则与 `name` 一致),用于声明依赖;
    自依赖 / 重复 / 引用不存在的 id 由 validator 拒绝,**依赖环**与"依赖的插件未被启用"由 `tools/load_plugins.py` 在生成装载计划时拒绝。
  - **装载顺序改为依赖拓扑序**:`load_order` 由依赖拓扑决定(被依赖者在前);无依赖时退化为既有目录序,
    因此**现有零依赖插件的装载顺序与升级前完全一致**(已用 v0.8.0-m8 基线逐项比对实证)。
  - 装载器仍属 **plan-only**(只生成装载计划,未真正装载/启动任何插件),启动期装载属后续里程碑。

---

融汇万端(Connect the Unconnectable.)

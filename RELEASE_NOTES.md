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

融汇万端(Connect the Unconnectable.)

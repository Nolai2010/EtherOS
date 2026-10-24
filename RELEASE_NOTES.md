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
- **v0.10.0-m10(compat 层首个真翻译,描述符级)**:
  - `plugins/compat/desktop-entry/translator.py` 首次**真正翻译**:把 freedesktop `.desktop` 桌面条目(纯文本描述符)
    翻译为 EtherOS 插件 manifest v2 + 包装 payload,成功时输出 `status: "translated"`(区别于 M3 stub 的 `"stub-plan-only"`)。
  - **诚实边界(重要)**:这是**描述符级翻译,不是二进制指令翻译** —— 不解析 exe/ipa/apk 二进制容器、
    不做指令集解码/系统调用转换/沙箱内执行;`Exec=` 只作字符串原样转发进包装 payload。
    `status: "translated"` 只表示产物已真实写出,**不表示已装载、更不表示已运行**;不得据此宣称"支持运行 .desktop 应用"。
  - 端到端闭环:外部 payload → translator → manifest v2(过 `validate_plugins.py`)→ `load_plugins.py` 纳入装载计划
    (示例 `plugins/optional/demo-desktop-app/`;未启用时正确落 `skipped`,既有零依赖插件的装载顺序逐项不变)。
  - 已知边界:`--manifest` 源声明 JSON 为必需参数(沿用 M3 契约),裸 `.desktop` 直通翻译需后续接口扩展;
    `Name` 归一化按 schema `^[a-z]` 首字符规则截断前导数字(如 `3D Viewer` → `d-viewer`,已在 translator README 记档)。
  - `plugins/optional/douyin/`(protocols: ["ipa"])与 `plugins/compat/stub-runtime/` **仍为 stub**,不因本里程碑改口径。
  - 本里程碑同时硬化门禁:lint 的 pyflakes 目标扩至 `plugins/compat/*/*.py`(覆盖新 translator)、
    spec-consistency 里程碑白名单扩至 M10。
- **v0.11.0-m11(装载闭环:load 原语首次真正执行)**:
  - `tools/load_state.py`(新)消费 `tools/load_plugins.py` 的装载计划,**物化装载状态**:`registry`(顺序与计划
    `load_order` 逐项相等)+ `routes`(协议激活表,仅已装载且声明该协议的 compat-bridge)+ `isolation`
    (派生声明,计划级 `PER_PLUGIN`,**非强制**);成功 `status: "loaded"`。
  - **诚实边界(重要)**:`loaded` = **宿主侧已登记 + 路由已激活**,**不表示已启动、更不表示已运行**;
    内核侧装载与镜像内启动期装载(`/etc/os/config.toml` 覆盖 + 真实加载)仍属后续里程碑(spec 约束 29)。
  - **装载产物被真实消费**:`tools/route_plugins.py --load-state <文件>` 从装载状态解析协议路由
    (如 `ipa` → douyin 链);未启用插件的协议不进激活表;缺省路径(无 `--load-state`)行为逐字不变。
  - 拒绝语义前移至装载期:plan/tree 漂移(条目 id 不存在 / payload 引用不符 / `load_order` 不一致 /
    输入非 plan-only 计划)→ 非 0 退出明因;两个已装载插件声明同一协议 → 装载期 `EAMBIGUOUS` 拒绝。
  - `tools/load_plugins.py`(M7 计划契约)**一字未改**;schema、`config/default.toml`、`[compat]` 开关
    (`enabled = false`)均未动;CI 十 job 名不变(plugin-schema 纯末尾追加 load-state smoke 一步)。
  - 已知边界:① 逆序 `load_order` 的计划会被装载器照单接受(与契约集合口径字面一致,真实生产者不可达,
    如需更严须契约+实现同步改);② `route_plugins.py` 的 FAIL 信息走 stdout(M3 既有约定,新代码沿用)。

---

融汇万端(Connect the Unconnectable.)

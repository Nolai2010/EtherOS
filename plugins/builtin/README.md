# plugins/builtin/ —— 内建不可卸载插件集(shipped plugins)

原"系统应用/服务/驱动"概念的归宿:`uninstallable:false`。
与 optional 插件**结构完全同构**,区别仅是 manifest 标志——"系统应用"不是特权阶层。

## 归位口径(M4,清单层归位)

M4 已归位首批成员 **shell / files / settings / mon**:系统能力以插件形态**声明与包装**
(清单层归位,计划差异点 1 口径;spec §3.2"内核之外皆插件"的结构落点)。每个成员是
manifest + 包装桩 payload,**如实声明 stub 性质与上游实体位置**(约束 19),不冒充实体的
"运行";上游对应实体(终端/文件浏览器/设置/性能监控程序)在 vendored 底座 `base/toaruos`
内部**原样保留**(约束 3/18),M4 不搬迁、不包装其内部实现。窗口化真集成属后续里程碑。

vendored 树零改动与 kernel/ 边界由 CI 守卫把关:`tools/check_kernel_boundary.py`
(etherkit-consistency job 每次运行;CI 非递归 checkout 下 submodule 本地漂移子检查打印
SKIP 明示跳过,其余检查照常)。

## 成员表(M4 已归位首批 4 件)

| name | capabilities | 上游实体(base/toaruos 内,原样保留) | payload | 语义 |
|---|---|---|---|---|
| `shell` | `sys.shell` | 终端程序 | `payload/shell` | 包装桩:echo stub 声明,不实现 shell 逻辑 |
| `files` | `fs.browse` | 文件浏览器 | `payload/files` | 包装桩:echo stub 声明,不实现文件浏览 |
| `settings` | `sys.settings` | 设置程序 | `payload/settings` | 包装桩:echo stub 声明,不实现设置界面 |
| `mon` | `sys.perfmon` | 性能监控程序 | `payload/mon` | 包装桩:echo stub 声明,不实现性能监控 |

成员规则:

- manifest 一律 `plugin.json`(schema v1,约束 20 零变更);`uninstallable:false` 由
  validator 目录规则强制(`tools/validate_plugins.py` 职责 4d:builtin ⇒ uninstallable==false)。
- payload 为 `#!/bin/sh` + echo 的确定性包装桩,输出
  `EtherOS builtin stub: <name> (wrapper declaration; upstream entity lives in base/toaruos, not relocated by M4)`。
- builtin 隐式启用(约束 12):不进 `config/default.toml [plugins] enabled`(enabled 只管 optional)。

## 后续成员(规划中,未归位)

驱动/服务包装桩属后续里程碑(计划差异点 3:首批不做——上游驱动在内核侧,"驱动即插件"
语义已由 CORE_MANIFEST `forbidden_in_kernel` 声明);原规划成员 window-manager /
file-manager / settings / perf-monitor / 各系统服务 / 各驱动 中,settings 已以 settings 桩、
perf-monitor 已以 mon 桩归位,file-manager 对应 files 桩。

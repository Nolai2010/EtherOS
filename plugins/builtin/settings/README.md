# plugins/builtin/settings —— 内建设置插件（清单层归位包装桩）

本插件是系统能力"设置"的插件形态**声明与包装**（清单层归位，计划差异点 1 口径）：
`uninstallable:false`（validator 目录规则），payload 为**包装桩脚本**，仅输出 stub 声明，
**不冒充实体的"运行"**（约束 19）。

上游对应实体（设置程序）在 vendored 底座 `base/toaruos` 内部**原样保留**（约束 3/18），
M4 不搬迁、不包装其内部实现；窗口化真集成属后续里程碑。

- manifest：`plugin.json`（schema v1 零变更，约束 20）
- payload：`payload/settings`（`#!/bin/sh` + echo，确定性输出供 CI grep）

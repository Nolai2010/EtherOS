# plugins/builtin/ —— 内建不可卸载插件集(shipped plugins)

原"系统应用/服务/驱动"概念的归宿:`uninstallable:false`。
成员规划:shell / window-manager / file-manager / settings / perf-monitor / 各系统服务 / 各驱动。
与 optional 插件**结构完全同构**,区别仅是 manifest 标志——"系统应用"不是特权阶层。
M4 完成归位(把底座既有对应物重分类进本目录)。

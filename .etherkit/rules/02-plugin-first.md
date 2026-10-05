# 02 · 插件优先铁律（Plugin-First Iron Rules）

1. **内核零格式知识**：禁止向 `kernel/` 添加文件系统格式、应用格式（ipa/exe/apk）、设备协议逻辑、UI 或驱动代码。格式兼容一律在 `plugins/compat/` 用户态兼容运行时实现。
2. **新增能力 = 声明式 JSON + 同级二进制**：写类 MCP 的 `plugin.json`（含 `protocols`/`capabilities`/`container`/`uninstallable` 字段），把二进制放同级目录。示例：装抖音 = `plugins/optional/douyin/douyin.json`（`protocols:["ipa"]`）+ `douyin.ipa`。
3. **一切系统能力皆插件**：需要"系统应用"时，放 `plugins/builtin/` 并标 `uninstallable:false`；可选功能放 `plugins/optional/`。禁止在内核或独立目录硬编码非插件实体。
4. **不早期重写底座**：优先评估 ToaruOS，保留其原生目录与构建系统，仅叠加；不要为了"纯净"重构内核。
5. **跨形态自适应**：同一插件经 manifest `container` 字段声明 PC 窗口化 / 手机全屏或分屏，由 shell（内建插件）选择容器策略，不为形态复制代码。
6. **CORE_MANIFEST.toml 是内核边界的唯一声明处**：清单之外的能力必须是插件。CI 将来会校验。

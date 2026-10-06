# hello-plugin

EtherOS M2 首个 optional 示例插件（M2-03 验收对象）。

- `plugin.json`：native 插件 manifest，`uninstallable: true`，容器声明 `desktop: windowed`（跨形态适配"至少其一"裁定口径）。
- `payload/hello`：**占位桩文件**。插件加载与运行属 M3 范围，M2 仅交付"通过 schema/validator 校验的 manifest 契约"，呼应 spec `spec/2026-10-05-etheros-dev-policy.md` §6 风险 4"目标形态不是首版承诺"。M3 将以真实二进制替换本桩。

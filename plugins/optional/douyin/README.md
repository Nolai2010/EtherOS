# douyin —— compat-bridge 桩插件（M3-02 验收对象）

首个 compat-bridge 示例（spec §2.2 douyin 示例语义；manifest 按 M2 约束 14 统一命名 `plugin.json`）。

- `plugin.json`：`type: "compat-bridge"`、`protocols: ["ipa"]`、`uninstallable: true`、`container.desktop: "windowed"`（跨形态适配"至少其一"裁定口径）；`translator` 指向 `plugins/compat/stub-runtime/translator.py`（validator 断言其真实存在，M3-02）。
- `payload/douyin.ipa`：**占位桩，不被解析、不被执行**（Global Constraint 17）——仅用于验证声明/路由/translator 链路。
- 本插件是验收桩：真翻译属 Phase 2 逐格式立项 —— spec `spec/2026-10-05-etheros-dev-policy.md` §6 风险 4「目标形态不是首版承诺」。

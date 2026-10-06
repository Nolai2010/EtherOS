# hello-plugin

EtherOS M2 首个 optional 示例插件（M2-03 验收对象）。

- `plugin.json`：native 插件 manifest，`uninstallable: true`，容器声明 `desktop: windowed`（跨形态适配"至少其一"裁定口径）。
- `payload/hello`：可执行 POSIX sh 脚本 demo（M3 实体化，兑现 M2 Task 4 记档"M3 换真二进制"——sh 脚本即可，真二进制不必要）。仅打印确定性问候，不加载任何外部格式；真实应用运行/窗口化渲染属 Phase 2，呼应 spec `spec/2026-10-05-etheros-dev-policy.md` §6 风险 4"目标形态不是首版承诺"。

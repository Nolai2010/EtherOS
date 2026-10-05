# plugins/ —— 绝对核心目录

EtherOS 的一切扩展能力的家。内核之外没有非插件实体。

| 子目录 | 语义 | uninstallable |
|---|---|---|
| `schema/` | `plugin.json` schema(MCP 式原语 + `container` + `uninstallable`) | — |
| `compat/` | 兼容运行时/翻译器(加载 ipa/exe/apk…) | 内建 |
| `builtin/` | 内建不可卸载插件:驱动/服务/shell/文件管理器/设置/性能监控 | `false` |
| `optional/` | 可选可替换插件:计算器/记事本/douyin… | `true` |
| `dev/` | 开发插件:AI Agent 规则(与系统能力插件隔离的特殊类) | — |
| `<name>/` | 具体插件,如 `optional/douyin/`(douyin.json + douyin.ipa) | 按类 |

新增能力 = 写声明式 `plugin.json` + 同级二进制;**不给内核改代码**。
schema 定义 M2 交付;当前为骨架占位。

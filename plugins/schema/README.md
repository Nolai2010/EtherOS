# plugins/schema/ —— plugin.json 契约(M2 · schema v1)

本目录承载插件 manifest 的稳定契约:`plugin.schema.json`(JSON Schema Draft 2020-12,`schema_version` 锁定 `"1"`)。
契约即稳定扩展契约(spec §2.4):**任何字段变更 = schema_version 变更**,并在提交信息注明 spec 依据(M2 锁定 v1,不为便利私自加字段)。
结构约束由 schema 表达;目录级规则、payload 存在性与配置一致性由 validator 语义层(`tools/validate_plugins.py`)执行。

## 字段语义表

字段集合逐字锚定 spec/2026-10-05-etheros-dev-policy.md §2.2/§3.2,无 spec 外字段:

| 字段 | 类型 | 约束 | spec 依据 |
|---|---|---|---|
| schema_version | const `"1"` | 必填;契约版本锁定 v1 | §2.4 契约版本化 |
| name | string | 必填;正则 `^[a-z][a-z0-9-]*$`;全树唯一(validator 断言) | §3.2 插件目录即插件 |
| version | string | 必填;semver 正则 | §1 发布策略(语义化版本) |
| type | enum | 必填;`native` \| `compat-bridge` | §2.2 两类插件 |
| uninstallable | boolean | 必填;目录规则见下节 | §2.2/§3.2 |
| payload | string | 必填;相对本插件目录的路径;允许含 `..` 的跨目录引用,解析后文件必须真实存在(validator 断言) | §2.2 「同级二进制」 |
| container | object | 必填;`desktop` ∈ {`windowed`}、`mobile` ∈ {`fullscreen`,`split`};**desktop/mobile 至少其一(台账 Ruling:跨形态适配语义)**;minProperties 1 | §2.2 跨形态适配 |
| protocols | array[string] | compat-bridge 必填且非空;native 可选 | §2.2(douyin.json 示例 `protocols:["ipa"]`) |
| translator | string | compat-bridge 必填;路径前缀必须为 `plugins/compat/` | §2.2 翻译运行时 |
| capabilities | array[string] | 可选;MCP 式原语,M2 不做语义路由 | §2.2 |
| tools | array[string] | 可选;MCP 式原语,M2 不做语义路由 | §2.2 |
| resources | array[string] | 可选;MCP 式原语,M2 不做语义路由 | §2.2 |

> **「MCP 式」边界**:M2 只落**字段形态**对齐(capabilities/tools/resources 原语),不做 MCP 协议/传输/会话语义——路由与 IPC 实跑属 M3+。

## 目录 uninstallable 规则(validator 语义层,spec §3.2)

| 目录 | uninstallable | 说明 |
|---|---|---|
| `plugins/builtin/` | 必须 `false` | 内建不可卸载插件集(shell/服务/驱动/文件管理器等) |
| `plugins/dev/` | 必须 `false` | 开发插件(AI Agent 规则,特殊类,隔离于系统能力插件) |
| `plugins/optional/` | 必须 `true` | 可选可替换插件(计算器、抖音兼容包等) |

违反即 validator FAIL(对应验收 M2-03/M2-05)。

## manifest 命名约定

- 统一使用 **`plugin.json`**(M2 示例一律如此);
- 应用级别名 **`<name>.json`**(如 `douyin.json`)为 spec §2.2 允许形态,validator 同时收录;
- validator 扫描 `plugins/{builtin,optional,dev}/*/` 下的 `*.json`,排除 README;零 manifest 即报错(防静默空过)。

## 校验

```bash
python3 tools/validate_plugins.py                    # 全树校验 + config [plugins] 一致性
python3 tools/validate_plugins.py --file <manifest>  # 单文件校验(负例循环用,跳过 config 一致性)
python3 tools/validate_plugins.py --config <toml>    # 覆盖默认 config/default.toml
```

依赖 `jsonschema`(CI `plugin-schema` job 已安装)。全过打印 `plugins validation: OK`(exit 0);任何失败逐条打印 `FAIL: <文件> <原因>`(exit 1)。

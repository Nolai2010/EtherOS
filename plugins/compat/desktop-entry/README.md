# desktop-entry —— `.desktop` 描述符级翻译器（M10 compat 层首个真翻译实现）

`translator.py` 把外部应用的 freedesktop 桌面条目（`.desktop`）描述符文本，真正翻译成 EtherOS 插件 manifest v2 + 一个包装 payload。

## 诚实边界（先读这一节）

- 这是**描述符级翻译**：输入是纯文本描述符，输出是插件声明（manifest v2）+ 包装 payload。
- 它**不是二进制指令翻译**：不解析 exe/ipa/apk，不做指令集解码，不做系统调用转换，不在沙箱内执行任何东西。
- `Exec=` 只作**字符串原样转发**进包装 payload（Global Constraint 47）；本 translator 与任何 EtherOS 工具都**不执行**它。包装 payload 只是翻译链路的**产物与证据**（纯数据）。
- `status: "translated"` 只表示**产物已真实写出**，**不表示已装载、更不表示已运行**；启动期装载仍属后续里程碑（与 M7 装载器 `status: "plan-only"` 同理）。
- `plugins/optional/douyin/`（protocols: `["ipa"]`）与 `plugins/compat/stub-runtime/translator.py` **仍是 stub**，不因本里程碑出现真实现而改口径（差异点 2）：二进制格式翻译属 spec §6 风险 8 明示的后期项。

## 字段映射表

| `.desktop` 字段 | manifest v2 字段 / 去向 | 规则 |
|---|---|---|
| `Name` | `name` | **必须归一化**（见下）。缺失或空 → 拒绝（exit 2）。 |
| `Type=Application` | `type: "compat-bridge"` | 仅 `Application` 接受；`Link` / `Directory` 拒绝并说明；无 `Type` 拒绝。 |
| `Exec` | 包装 payload 的 `Exec=` 行 | 逐字字符串转发；缺失或空 → 拒绝（负例①）。**不解析、不执行**。 |
| `Comment`（可选） | 包装 payload 的 `Comment=` 行 | **不进 manifest**：schema v2 为 `additionalProperties: false`，无自由文本字段可放。只在包装 payload 中保留。 |
| `Categories`（可选） | `capabilities` | 分号切分，逐 token 归一化后前缀 `desktop.category.`（如 `AudioVideo` → `desktop.category.audiovideo`）。无 `Categories` 则**不生成** `capabilities` 字段。 |
| — | `schema_version: "2"` | M9 起的 v2 契约。 |
| — | `version: "0.1.0"` | 合法 semver，由翻译器生成。 |
| — | `uninstallable: true` | optional 目录规则（validator 职责 4d）。 |
| — | `container.desktop: "windowed"` | 桌面条目是桌面形态描述符，逐字映射。 |
| — | `protocols: ["desktop-entry"]` | 本 translator 只处理这一个格式。 |
| — | `translator: "plugins/compat/desktop-entry/translator.py"` | 指回本 translator。 |
| `Icon` / `Terminal` / `TryExec` / `MimeType` 等其它键 | 忽略 | 当前不做语义映射，逐键不采信（不假装支持）。 |
| 本地化键 `Name[xx]=` / `Comment[xx]=` | 忽略 | 只取未本地化的键。 |
| 非 `[Desktop Entry]` 段（如 `[Desktop Action x]`） | 忽略 | 防同名键污染。 |
| 行续接（`\` 结尾） | 不受理 | 当前不做续接解析。 |
| 重复 `Key=` | 取**首次出现值** | `setdefault`（translator.py:109）；freedesktop 规范下重复键属非法输入，此处不报错、取首次值继续。 |

## `name` 归一化规则（差异点 4）

`.desktop` 的 `Name` 常含大写、空格与标点，而 manifest 要求 `^[a-z][a-z0-9-]*$`。归一化按序执行：

1. **小写化**：`Demo Desktop App` → `demo desktop app`
2. **非字母数字字符 → `-`**：→ `demo-desktop-app`（空格变 `-`）
3. **折叠连续 `-`**：`A -- B` → `a-b`
4. **去前导非字母**（含 `-` 与数字，因首字符必须是 `[a-z]`）：`3D Viewer` → `3d-viewer` → `d-viewer`
5. **去尾 `-`**：`App!` → `app-` → `app`

例：`Demo Desktop App` → `demo-desktop-app`；`3D Viewer` → `d-viewer`（数字前导被剥，规则使然，非误判）。

**冲突即拒绝**：归一化后的 id 若与 `plugins/{builtin,optional,dev}` 中已声明的插件 id 撞名，翻译器**拒绝并说明**（exit 2），绝不覆盖另一个插件。唯一例外是**重翻译自身**：源声明里已叫这个名字时允许（幂等重跑）。

## CLI（沿用 M3 契约）

```
translator.py --manifest <源声明 JSON> [--payload <.desktop 路径>] [--out <输出目录>] [--name <覆盖 id>]
```

- `--payload` 缺省时取 manifest 的 `payload` 字段（相对 manifest 所在目录解析）。
- `--out` 缺省为 `<manifest 所在目录>/translated`。
- `exit 0` = 已真实写出 `plugin.json` + `<id>.payload`，并打印结果 JSON（`status: "translated"`）。
- `exit 2` = 拒绝（入口不可用 / 非 desktop-entry / 缺关键字段 / id 冲突），打印原因、**不产出**。

stdlib only（与 `plugins/compat/stub-runtime/translator.py` 同族），不导入/链接任何 `kernel/` 代码（约束 11）。

## 负例（三条，各自 exit 2 + 原因）

| 负例 | 触发 | 结果 |
|---|---|---|
| ① 缺 `Exec` | `[Desktop Entry]` 有 `Name` + `Type=Application` 但无 `Exec` | exit 2，`desktop entry has no Exec= … nothing to forward into the wrapper payload` |
| ② 非法格式 | payload 塞一段 JSON（首行 `{`） | exit 2，`payload is not a freedesktop desktop entry: no [Desktop Entry] section (looks like JSON, not a desktop entry)` |
| ③ 空文件 | payload 为 0 字节/全空白 | exit 2，`payload '<file>' is empty (0 bytes / blank) — nothing to translate` |

另有 `Type=Link` / `Type=Directory` 拒绝、非 UTF-8 二进制 payload 拒绝、id 冲突拒绝，均 exit 2 并说明。

## 不做什么

- 不运行 `.desktop` 应用，不模拟任何指令集，不做沙箱内执行。
- 不解析/执行二进制 payload（`ipa`/`exe`/`apk` 仍是 stub 占位）。
- 不做窗口化渲染、不做 MCP 协议/传输/会话语义（capabilities 仅字段形态对齐）。

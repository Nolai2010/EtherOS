# demo-desktop-app —— M10 端到端示例（由 `.desktop` 翻译而来的插件）

M10 的端到端实证插件：外部格式描述符 `app.desktop` → `plugins/compat/desktop-entry/translator.py` 真翻译 → 产物过 v2 校验 → 纳入 `tools/load_plugins.py` 装载计划。

## 内容

- `app.desktop`：**外部格式（freedesktop 桌面条目）占位**，格式真实（有 `[Desktop Entry]` / `Type=Application` / `Name` / `Exec`），`Exec` 指向无害命令 `/bin/echo`。
- `plugin.json`：v2 manifest，`type: "compat-bridge"`、`protocols: ["desktop-entry"]`、`translator` 指向 `plugins/compat/desktop-entry/translator.py`；目录级规则 optional ⇒ `uninstallable: true`；`payload` 指向外部描述符 `app.desktop`。

## 诚实边界

- 这是**描述符级翻译**的示例，**不是二进制指令翻译**：没有解码任何指令，没有映射任何系统调用，没有在沙箱内执行外部程序。
- `Exec=` 只作字符串转发，`app.desktop` **不被执行**（约束 17：foreign payload 只装载引用、永不执行）。
- 本插件在 `config/default.toml` 的 `[plugins] enabled` 中默认**未启用**（差异点 5：M10 验证的是 translator 能力，不是打开运行期兼容开关）；端到端实证时临时启用、验完还原。
- `plugins/optional/douyin/`（`ipa`）与 `plugins/compat/stub-runtime/` 仍是 stub，不因本示例改口径。

## 复跑翻译

```
python3 plugins/compat/desktop-entry/translator.py \
  --manifest plugins/optional/demo-desktop-app/plugin.json --out /tmp/m10-translate
python3 tools/validate_plugins.py --file /tmp/m10-translate/plugin.json
```

产物为 `/tmp/m10-translate/plugin.json` 与 `/tmp/m10-translate/demo-desktop-app.payload`。

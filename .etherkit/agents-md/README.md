# agents-md/ —— AGENTS.md 系工具的补充说明

## 定位

AGENTS.md 系工具（Codex/OpenCode/Amazon Q/Zed/goose/Devin 等）原生读取仓库根 `AGENTS.md`，
无需为本目录生成任何文件；根 `AGENTS.md` 由 `.etherkit/AGENTS.md` 生成。

此处只放各工具的**补充说明**：根契约之外的专属行为提示（如该工具特有的
指令链机制、生成物边界、参数上限），不重复根契约内容。

## 现有文件

| 文件 | 适用工具 | 内容 |
|---|---|---|
| `codex-notes.md` | Codex | `.codex/agents/` 生成物边界、指令链顺序、`project_doc_max_bytes` 上限 |

## 新增补充文件的规则

- 命名：`<tool>-notes.md`（如 `opencode-notes.md`）。
- 内容只放该工具专属、与其他工具不重复的提示；通用规则一律写 `.etherkit/AGENTS.md`。

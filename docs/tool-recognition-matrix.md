# 工具识别矩阵(Tool Recognition Matrix)

> 本矩阵是 **M0 出口标准第 2 条**(".etherkit/ 复制+生成后 25+ 工具可识别")的复核证据。
> 全部路径由生成器 `.etherkit/generate.sh` 产出;脚本断言见 `tools/verify-tool-map.sh`(33 项路径全过)。
> 工具识别机制以 **2026-10-05 联网核实**为准,与 spec §3.4 映射表同源(spec/2026-10-05-etheros-dev-policy.md)。

## 矩阵

| 工具 | 原生路径 | 识别机制 | 验证状态 |
|---|---|---|---|
| Codex | `AGENTS.md`;`.codex/agents/builder.toml`、`.codex/agents/test-author.toml`、`.codex/agents/acceptance-checker.toml`、`.codex/agents/reviewer.toml`、`.codex/agents/visual-reviewer.toml` | AGENTS.md 原生读 + 专属文件(agents TOML) | script-verified |
| GitHub Copilot | `AGENTS.md`;`.github/copilot-instructions.md`;`.github/skills/etheros-workflow/SKILL.md` | AGENTS.md 原生读 + 专属文件 | script-verified |
| Cursor | `AGENTS.md`;`.cursor/rules/01-project-context.mdc`;`.cursor/rules/04-license-workflow.mdc` | AGENTS.md 原生读 + 专属文件(.mdc 规则) | script-verified(tool-side behavior untested) |
| Cline | `AGENTS.md`;`.clinerules/` | AGENTS.md 原生读 + 专属文件 | script-verified |
| Devin | `AGENTS.md`;`devin.md` | AGENTS.md 原生读 + 专属文件(单文件) | script-verified |
| Zed | `AGENTS.md`;`.zed/rules` | AGENTS.md 原生读 + 专属文件 | script-verified |
| Windsurf | `AGENTS.md`;`.windsurfrules` | AGENTS.md 原生读 + 专属文件 | script-verified |
| Roo Code | `AGENTS.md`;`.roo/rules/` | AGENTS.md 原生读 + 专属文件 | script-verified |
| Amazon Q | `AGENTS.md`;`.amazonq/rules/` | AGENTS.md 原生读 + 专属文件 | script-verified |
| Continue | `AGENTS.md`;`.continue/rules/` | AGENTS.md 原生读 + 专属文件 | script-verified |
| Augment | `AGENTS.md`;`.augment/rules/` | AGENTS.md 原生读 + 专属文件 | script-verified |
| Antigravity | `AGENTS.md`;`.agent/rules/` | AGENTS.md 原生读 + 专属文件 | script-verified |
| goose | `AGENTS.md` | AGENTS.md 原生读 | script-verified |
| OpenCode | `AGENTS.md` | AGENTS.md 原生读 | script-verified |
| Gemini CLI | `AGENTS.md`;`GEMINI.md`(经 context.fileName 可配) | AGENTS.md 原生读 | script-verified |
| Claude Code | `CLAUDE.md`;`.claude/rules/`;`.claude/skills/etheros-workflow/SKILL.md` | 专属文件(根 CLAUDE.md + .claude/rules + .claude/skills) | script-verified |
| Trae | `.trae/rules/` | 专属文件 | script-verified |
| Kiro | `.kiro/steering/` | 专属文件 | script-verified |
| JetBrains AI | `.aiassistant/rules/` | 专属文件 | script-verified |
| Tabnine | `.tabnine/guidelines/` | 专属文件 | script-verified |
| OpenHands | `.openhands/microagents/` | 专属文件 | script-verified |
| Aider | `CONVENTIONS.md`;`.aider.conf.yml`(read: 引入) | 专属文件 | script-verified |
| Bolt | `bolt.instructions.md` | 专属文件(devin.md 类单文件) | script-verified |
| Lovable | `lovable.instructions.md` | 专属文件(devin.md 类单文件) | script-verified |
| Replit | `.replit/ai-rules` | 专属文件(devin.md 类单文件) | script-verified |
| 豆包工作 | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| ChatGPT Projects/GPTs | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| Kimi 工作模式 | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| 千问办公 | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| 智谱清言/GLM | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| 文心一言 | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| 腾讯元宝/混元 | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| OpenClaw | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| Coze/扣子 | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| Dify | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |
| 飞书/钉钉 AI | `.etherkit/prompts/system-prompt.md`(粘贴源) | 降级粘贴(不承诺自动加载) | manual-paste |

## 验证状态口径

- `script-verified`:路径存在性由 `tools/verify-tool-map.sh` 断言(33 项:21 个文件 + 12 个目录),另含 `diff -q AGENTS.md .etherkit/AGENTS.md` 一致性抽查。
- `manual-paste`:聊天类工具无文件级识别机制,需人工将 `.etherkit/prompts/system-prompt.md` 内容粘贴为系统提示词;不承诺自动加载。
- `script-verified(tool-side behavior untested)`:文件存在已断言,但工具对 frontmatter 等元数据的具体解析行为属工具侧行为,未实测。

## 一致性说明

- 行覆盖与 `tools/verify-tool-map.sh` 断言清单一一对应;断言清单内路径当前全部由 `bash .etherkit/generate.sh` 产出。
- 生成物纪律:根 `AGENTS.md`/`CLAUDE.md`/.cursor 等均为生成物,禁手改;改规则只改 `.etherkit/` 源后重新生成。

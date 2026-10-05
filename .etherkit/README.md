# .etherkit/ —— EtherOS Agent 脚手架（项目同步单一事实源）

## 这是什么

**项目同步**载体：EtherOS 项目自身的 Agent 开发上下文（契约、规则、子代理角色）随本仓库走。
换电脑 / 换 AI 工具时，**clone 仓库即用**，无需与完全没有上下文的 Agent 重新沟通。

> ⚠️ 边界：这是**项目同步**，不是**技能分发**——本目录内容只服务 EtherOS 本项目，
> 不发布到技能市场、不装进个人 skills 目录、不追求跨项目复用。

## 结构（5 类 + 子代理）

| 目录 | 用途 | 生成去向（generate.sh） |
|---|---|---|
| `AGENTS.md` | 工具无关项目契约（**唯一事实源**） | 根 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`、`devin.md`、`bolt/lovable.instructions.md`、`.replit/ai-rules`、`CONVENTIONS.md`(Aider)、`.github/copilot-instructions.md` |
| `rules/` | 项目规则（按主题分文件） | `.cursor/rules/*.mdc`、`.clinerules/`、`.trae/rules/`、`.roo/rules/`、`.amazonq/rules/`、`.continue/rules/`、`.augment/rules/`、`.kiro/steering/`、`.aiassistant/rules/`、`.tabnine/guidelines/`、`.openhands/microagents/`、`.agent/rules/`、`.claude/rules/`、单文件系 `.windsurfrules`、`.zed/rules` |
| `skills/` | SKILL.md 格式技能 | `.claude/skills/`、`.github/skills/` |
| `subagents/` | 固定五角色 TOML | `.codex/agents/` |
| `prompts/` | 聊天/工作型 AI 降级模板（豆包/Kimi/千问/智谱/元宝/OpenClaw/Coze/Dify…） | 不生成；按平台手工粘贴，不承诺自动加载 |
| `frameworks/` | LangGraph/AutoGen/CrewAI/n8n/Zapier 节点提示词 | 不生成；构建编排图时直接引用 |
| `agents-md/` | AGENTS.md 系工具的补充说明（Codex/OpenCode/Amazon Q/Zed/goose…原生读根 AGENTS.md，无需生成） | — |

## 使用规则（三条）

1. **改规则只改 `.etherkit/` 内的源文件**，然后运行 `bash .etherkit/generate.sh`，把源文件与生成物一并提交。
2. **禁止手改任何生成物**（根 `AGENTS.md`、`.cursor/`、`.clinerules/` 等）——CI 的 `etherkit-consistency` job 会重新生成并比对，手改必挂。
3. 新工具接入 = 在 `generate.sh` 里加一行映射（映射表见本 README 上表），不动规则内容。

## 迁移到新电脑（三选一，由弱到强）

1. **clone 即用**：生成物已提交，各工具打开仓库即读到完整上下文（推荐，零操作）。
2. clone 后跑一次 `bash .etherkit/generate.sh`（自愈/补齐本机特有工具）。
3. 聊天型 AI（无法读仓库）：把根 `AGENTS.md` 内容或 `prompts/system-prompt.md` 粘贴进其系统提示词/工作模式。

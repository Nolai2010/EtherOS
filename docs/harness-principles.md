# Harness 原则:.etherkit 项目同步

本仓库的 AI 协作基础设施遵循以下原则(细节见 `.etherkit/README.md`):

1. **单一事实源**:所有 Agent 契约/规则/角色定义只写在 `.etherkit/`,别处皆是生成物。
2. **生成物纪律**:根 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`、`.cursor/rules/`、`.clinerules/`、`.trae/rules/`、`.github/copilot-instructions.md`、`.codex/agents/` 等**禁止手改**;改 `.etherkit/` → `bash .etherkit/generate.sh` → 源与产物一并提交。
3. **项目同步,非技能分发**:`.etherkit/` 只服务 EtherOS 本项目,不发布市场、不装个人 skills 目录、不求跨项目复用。
4. **clone 即用**:生成物随仓库提交,新电脑 clone 后任何支持仓库指令文件的工具立刻获得完整上下文(AGENTS.md 为 20+ 工具跨工具标准)。
5. **防漂移三重保险**:①生成物不手改纪律;②CI `etherkit-consistency` job 重新生成并 `git diff --exit-code` 比对;③文档索引制(docs/index.md)。
6. **降级有预案**:不支持仓库指令文件的聊天/工作型 AI 用 `.etherkit/prompts/system-prompt.md` 粘贴降级,不承诺自动加载。

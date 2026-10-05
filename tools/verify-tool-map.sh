#!/usr/bin/env bash
# tools/verify-tool-map.sh — M0 出口标准"25+ 工具可识别"的路径断言脚本。
# 断言清单与 docs/tool-recognition-matrix.md 一一对应;生成器为 .etherkit/generate.sh。
set -euo pipefail
cd "$(dirname "$0")/.."

# 生成物文件(逐项 [ -f ])
FILES=(
  AGENTS.md
  CLAUDE.md
  GEMINI.md
  devin.md
  bolt.instructions.md
  lovable.instructions.md
  .replit/ai-rules
  CONVENTIONS.md
  .aider.conf.yml
  .windsurfrules
  .zed/rules
  .github/copilot-instructions.md
  .claude/skills/etheros-workflow/SKILL.md
  .github/skills/etheros-workflow/SKILL.md
  .cursor/rules/01-project-context.mdc
  .cursor/rules/04-license-workflow.mdc
  .codex/agents/builder.toml
  .codex/agents/test-author.toml
  .codex/agents/acceptance-checker.toml
  .codex/agents/reviewer.toml
  .codex/agents/visual-reviewer.toml
)

# 生成物目录(逐项 [ -d ])
DIRS=(
  .clinerules
  .trae/rules
  .roo/rules
  .amazonq/rules
  .continue/rules
  .augment/rules
  .kiro/steering
  .aiassistant/rules
  .tabnine/guidelines
  .openhands/microagents
  .agent/rules
  .claude/rules
)

missing=0
total=0

for f in "${FILES[@]}"; do
  total=$((total + 1))
  if [ ! -f "$f" ]; then
    echo "MISSING: $f"
    missing=$((missing + 1))
  fi
done

for d in "${DIRS[@]}"; do
  total=$((total + 1))
  if [ ! -d "$d" ]; then
    echo "MISSING: $d"
    missing=$((missing + 1))
  fi
done

# 一致性抽查:根生成物与 .etherkit 源一致
if ! diff -q AGENTS.md .etherkit/AGENTS.md; then
  echo "DIFF: AGENTS.md differs from .etherkit/AGENTS.md"
  missing=$((missing + 1))
fi

if [ "$missing" -gt 0 ]; then
  echo "tool map: FAILED ($missing missing/diff, $total paths asserted)"
  exit 1
fi

echo "tool map: ${total}/${total} OK"
exit 0

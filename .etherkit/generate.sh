#!/usr/bin/env bash
# EtherOS .etherkit/generate.sh —— 项目同步生成器
# 单一事实源: .etherkit/  |  产物: 各 AI 工具的原生项目级配置
# 用法: 在仓库根目录运行  bash .etherkit/generate.sh
# 规则: 只改 .etherkit/ 源文件后重跑本脚本; 禁止手改任何生成物。
set -euo pipefail
shopt -s nullglob

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KIT="$ROOT/.etherkit"
cd "$ROOT"

count=0
emit() { # emit <dst> <src...> : 依序拼接源文件
  local d="$1"; shift; mkdir -p "$(dirname "$d")"; : > "$d"
  local f; for f in "$@"; do [ -f "$f" ] && { cat "$f" >> "$d"; printf '\n' >> "$d"; }; done
  echo "  + $d"; count=$((count+1))
}
emitcp() { # emitcp <dst> <src> : 原样复制
  local d="$1" s="$2"; mkdir -p "$(dirname "$d")"; cp "$s" "$d"
  echo "  + $d"; count=$((count+1))
}
emitdir() { # emitdir <dstdir> <src...> : 平铺复制到目录
  local d="$1"; shift; mkdir -p "$d"
  local f n=0; for f in "$@"; do cp "$f" "$d/"; n=$((n+1)); done
  echo "  + $d/ ($n files)"; count=$((count+n))
}

RULES=( "$KIT"/rules/*.md )
SRC="$KIT/AGENTS.md"

echo "[EtherOS] 项目同步: .etherkit/ -> 各工具原生配置"

# ---------- 1) 跨工具标准: AGENTS.md 系 ----------
emitcp "AGENTS.md" "$SRC"
emitcp "CLAUDE.md" "$SRC"   # Claude Code
emitcp "GEMINI.md" "$SRC"   # Gemini CLI
emitcp "devin.md"  "$SRC"   # Devin
emitcp "bolt.instructions.md"    "$SRC"
emitcp "lovable.instructions.md" "$SRC"
emitcp ".replit/ai-rules"        "$SRC"
emitcp "CONVENTIONS.md"          "$SRC"   # Aider conventions
mkdir -p "$ROOT"
cat > "$ROOT/.aider.conf.yml" <<'EOF'
# 生成物: 由 .etherkit/generate.sh 维护, 勿手改
read: CONVENTIONS.md
EOF
echo "  + .aider.conf.yml"; count=$((count+1))

# ---------- 2) 单文件规则系(拼接) ----------
if [ ${#RULES[@]} -gt 0 ]; then
  emit ".windsurfrules" "${RULES[@]}"   # Windsurf / Devin Desktop
  emit ".zed/rules"     "${RULES[@]}"   # Zed
fi

# ---------- 3) 目录规则系(原样平铺复制) ----------
if [ ${#RULES[@]} -gt 0 ]; then
  for d in ".clinerules" ".trae/rules" ".roo/rules" ".amazonq/rules" \
           ".continue/rules" ".augment/rules" ".kiro/steering" \
           ".aiassistant/rules" ".tabnine/guidelines" \
           ".openhands/microagents" ".agent/rules" ".claude/rules"; do
    emitdir "$d" "${RULES[@]}"
  done
fi

# ---------- 4) Cursor 项目规则(.mdc, 附 frontmatter) ----------
if [ ${#RULES[@]} -gt 0 ]; then
  mkdir -p .cursor/rules
  local_b=""
  for f in "${RULES[@]}"; do
    local_b="$(basename "$f" .md)"
    { printf -- '---\ndescription: "EtherOS 项目规则(由 .etherkit/generate.sh 生成, 勿手改)"\nalwaysApply: true\n---\n\n'
      cat "$f"; printf '\n' ; } > ".cursor/rules/$local_b.mdc"
    echo "  + .cursor/rules/$local_b.mdc"; count=$((count+1))
  done
fi

# ---------- 5) GitHub Copilot ----------
emitcp ".github/copilot-instructions.md" "$SRC"

# ---------- 6) Skills(Claude Code / Copilot) ----------
for d in "$KIT"/skills/*/; do
  [ -f "${d}SKILL.md" ] || continue
  name="$(basename "$d")"
  mkdir -p ".claude/skills/$name" ".github/skills/$name"
  cp -r "$d". ".claude/skills/$name/"
  cp -r "$d". ".github/skills/$name/"
  echo "  + .claude/skills/$name + .github/skills/$name"; count=$((count+2))
done

# ---------- 7) Codex 固定子代理 ----------
tomls=( "$KIT"/subagents/*.toml )
if [ ${#tomls[@]} -gt 0 ]; then
  mkdir -p .codex/agents
  emitdir ".codex/agents" "${tomls[@]}"
fi

echo ""
echo "[EtherOS] 完成: 共生成 $count 个文件/目录"
echo "  修改规则请编辑 .etherkit/ 后重跑本脚本; 禁止手改生成物。"

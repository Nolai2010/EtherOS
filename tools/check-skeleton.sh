#!/usr/bin/env bash
# 结构校验:M0 空构建 = 骨架完整性断言(不编译任何 C 代码)
set -euo pipefail
cd "$(dirname "$0")/.."
fail=0
for d in spec docs kernel arch/x86_64 arch/aarch64 plugins/schema plugins/compat \
         plugins/builtin plugins/optional plugins/dev config packages sdk themes \
         base/toaruos \
         .etherkit .github/workflows; do
  [ -d "$d" ] || { echo "MISSING DIR: $d"; fail=1; }
done
for f in LICENSE NOTICE CORE_MANIFEST.toml AGENTS.md config/default.toml \
         config/build.toml LICENSES/MIT.txt REUSE.toml .etherkit/generate.sh; do
  [ -f "$f" ] || { echo "MISSING FILE: $f"; fail=1; }
done
grep -q "protocol-route" CORE_MANIFEST.toml || { echo "CORE_MANIFEST 缺内核三能力声明"; fail=1; }
[ "$fail" -eq 0 ] && echo "skeleton check: OK"
exit $fail

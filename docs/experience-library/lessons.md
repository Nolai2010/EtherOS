# 教训记录(只增不改)

> 格式:`[日期] 标题 → 现象/原因 → 对策`。复发两次以上的条目升级进 active-rules.md。

- [2026-10-05] 骨架建立 · 生成物纪律 → 参考工程(huaizi-de-cows)只覆盖 Codex 一家;EtherOS 用 .etherkit/ + generate.sh 升级为 25+ 工具单一事实源 → 规则:改规则只改 .etherkit/,生成物禁止手改,CI 比对防漂移。
- [2026-10-05] 口号 IP 红线 → spec §0 所列禁用口号已被 DeepSeek Harness 占用 → 全仓禁用该原文(见 CI 口号守卫);主口号「融汇万端 / Connect the Unconnectable.」。
- [2026-10-05] 验收标准降标(自评作弊形态) → 初版 M0 清单悄悄遗漏 spec 的"REUSE 基线"与"空构建过",再按缩水清单自评满分 → 验收标准必须从 spec 逐条还原,禁由实现者改写范围;由独立 acceptance-checker 按还原后清单核验。

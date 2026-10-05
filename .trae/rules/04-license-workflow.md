# 04 · 许可、提交与工作流（License & Workflow）

- **许可**：主许可 MIT（M1 许可清算后宣布纯 MIT）；清算前保留上游 LICENSE + NOTICE；每个源文件顶部加 `# SPDX-License-Identifier: MIT`（REUSE 规范）；第三方组件只允许 MIT/Apache/BSD 类，非同类主动替换。
- **DCO**：每次提交带 `Signed-off-by`（`git commit -s`），CI 校验。
- **分支**：GitHub Flow 简化——`main` + 短命分支 + PR；不开长期开发分支。
- **提交信息**：一行主题 ≤72 字符，写"做了什么"而非"改了哪个文件"；破坏性变更在主题加 `!` 并在正文说明。
- **文档索引制**：新增/移动文档必须同步更新 `docs/index.md`；新增教训必须写入 `docs/experience-library/`。
- **YAGNI**：当前阶段只做文档/骨架/脚手架/CI；任何"顺手实现内核功能"都算越界，回滚。
- **生成物纪律**：`.etherkit/` 之外的所有 Agent 配置都是生成物，禁止手改；改规则 → 改 `.etherkit/` → `bash .etherkit/generate.sh` → 一并提交。

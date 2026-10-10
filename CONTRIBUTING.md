# CONTRIBUTING —— 贡献流程

> EtherOS —— 融汇万端 (Connect the Unconnectable.)
> 本文件是贡献者入口,三段:DCO 签核、分支惯例、验收闭环。完整 11 步开发流程见根 `AGENTS.md`。

## 1. DCO:每次提交都要签核

本项目采用 [DCO 1.1](https://developercertificate.org/),提交必须带 `Signed-off-by`:

```bash
git commit -s -m "主题一行,不超过 72 字符"
```

- CI 的 `dco` job 逐条校验 push/PR 内的提交;缺签核直接红,构不成本项目的有效贡献。
- **merge commit 豁免**:本项目以 `git merge --no-ff` 合并里程碑分支,该合并提交惯例上不带签核
  (与 GitHub DCO app 对合并提交的豁免同款),已按 M5-02 记档。**非合并提交一律不豁免**。
- 本地漏签的补救:`git rebase --signoff`(仅限尚未推送的提交;已推送的共享分支请补新提交,不要强推)。

## 2. 分支与 tag 惯例

- 每个里程碑一个**短命分支**:`feat/m<N>-<slug>`(例:`feat/m7-phase2-opening`)。
  日常提交只推自己的里程碑分支,不直接推 `main`。
- 里程碑收官:`git merge --no-ff` 合入 `main`,保留分支史(因此才有上面的 merge commit 豁免)。
- 关门 tag:`v0.x.0-mN`(annotated,`git tag -a`)。`release.yml` 在 `push tags 'v*'` 时自动构建
  并发布 GitHub Release(ISO / kernel / ramdisk 三形态),标记 prerelease;发布说明取自 `RELEASE_NOTES.md`。

## 3. 验收闭环

- **实现者 ≠ 审查者(Builder ≠ Reviewer)**:同一任务的写实现与做审查必须是不同角色/不同上下文,
  见 `docs/builder-reviewer-separation.md`。
- **禁止自评通过**:每条验证必须实跑,并在该里程碑的验收报告里贴完整命令与输出;没跑的条目写
  "未验证",不得写成通过。
- 每个里程碑有**独立验收报告**入 `docs/reports/`(例:`docs/reports/2026-10-06-m6-acceptance.md`),
  逐条对应 `docs/development/acceptance-standard.md` 中该里程碑的条目。
- **验收未过不合门、不打 tag**。遗留项如实记档(PENDING / PASS-with-note / 口径差异),不冒充实测通过。
- 教训沉淀到 `docs/experience-library/lessons.md`(只增不改);复发 ≥2 次的问题升格进
  `docs/experience-library/active-rules.md`。

## 相关文档

| 文档 | 用途 |
|---|---|
| `docs/development/acceptance-standard.md` | 当前验收标准(外部合格线:不得自行新增、改写或降低) |
| `docs/builder-reviewer-separation.md` | 写实现 ≠ 审查的规则与理由 |
| `docs/index.md` | 文档索引(新增/移动文档必须同步更新该表) |
| `docs/experience-library/lessons.md` | 教训库(只增不改) |

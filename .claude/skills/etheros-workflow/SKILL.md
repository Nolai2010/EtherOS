---
name: etheros-workflow
description: 在 EtherOS 仓库执行任何开发/修复任务前，加载 11 步对抗式开发流程与五角色协作规则。
---

# EtherOS 开发流程（etheros-workflow）

## 触发场景

在 EtherOS 仓库做任何实现/修复/测试任务之前，先加载本技能。

## 前置输入清单（缺一即向主控要，不得猜路径）

1. spec 路径
2. 验收标准路径（docs/development/acceptance-standard.md）
3. 测试入口
4. 允许读写范围
5. 返回要求

## 流程指针

- 严格按根 `AGENTS.md` 的「必须严格遵守的开发流程（11 步）」执行，不得自行发明或裁剪流程。
- 固定角色定义见 `.etherkit/subagents/`：
  `builder` / `test-author` / `acceptance-checker` / `reviewer` / `visual-reviewer`。

## 硬规则摘引

- **写实现的 Agent ≠ 审查的 Agent**（不同上下文）；**禁止自评**。
- 一个修复一个核验：每次修复后必须重跑测试确认。
- **假覆盖 = 未覆盖**：验收标准必须有真实测试覆盖。
- 教训写入 `docs/experience-library/lessons.md`（已解决问题、复发规则与教训）。

## 完成判据

测试 + visual-reviewer（如涉视觉）+ reviewer + 主控复核全部通过；
报告须含：改动清单、覆盖的验收标准编号、验证方式与输出、残余风险。

# 子 Agent 派发指南

固定角色定义在 `.etherkit/subagents/`(*.toml,Codex 生成到 `.codex/agents/`)。

## 派发前检查单(主 Agent 必须给全,缺一子 Agent 返回"缺少必要输入")

1. spec 路径(如 `spec/2026-10-05-etheros-dev-policy.md` 或后续版本 spec)
2. 验收标准路径(`docs/development/acceptance-standard.md`)
3. 测试策略/用例/入口路径
4. 允许读取、允许修改、禁止修改的文件范围
5. 返回要求(结论格式、证据形式)

## 角色速查

| 角色 | 读写 | 职责 | 红线 |
|---|---|---|---|
| `builder` | workspace-write | 按 spec+验收标准实现 | 不改验收标准;不当审查者;不手改生成物 |
| `test-author` | workspace-write(限 docs/与测试) | 把标准翻译成可断言测试 | 不写实现;不把〔待定〕写死 |
| `acceptance-checker` | read-only | 逐条核对标准↔测试映射 | 假覆盖=未覆盖;偏严 |
| `visual-reviewer` | read-only | 对照基准核对真实截图 | 不接受示意图;不写代码 |
| `reviewer` | read-only | 先标准符合性后代码质量 | 不因"已自称通过"跳过核对 |

## 上下文分离(硬规则)

- 同一轮任务里,写实现的 Agent 不得担任 reviewer / visual-reviewer / acceptance-checker。
- 子 Agent 结论不等于最终结论:主 Agent 必须统一复核改动并运行必要验证。

# plugins/compat/stub-runtime —— 翻译运行时雏形（STUB）

M3 兼容桩最小闭环的 translator 实体（M3-01 验收对象）。

## 调用契约

```
python3 plugins/compat/stub-runtime/translator.py --manifest <plugin.json 路径> [--payload <路径>]
```

- 读取 compat-bridge manifest（非 compat-bridge → exit 2 拒绝，不输出计划）。
- payload 缺省取 manifest 的 `payload` 字段（相对 manifest 所在目录解析），`--payload` 可覆盖。
- 向 stdout 输出结构化「翻译计划」JSON：`source_format` / `target_format` / `steps[]` / `status: "stub-plan-only"`。

## stub 边界声明（Global Constraint 16）

- **只出计划，不翻译**：不解析 exe/ipa/apk 等任何真实格式内容，不执行任何 payload，绝不伪装成功翻译。
- steps（unpack / translate-syscalls / launch）仅为 Phase 2 真翻译的**阶段示意**，本 stub 不执行其中任何一步。
- 真翻译（指令集/系统调用/GUI 语义）属 Phase 2 逐格式立项 —— spec `spec/2026-10-05-etheros-dev-policy.md` §6 风险 4「目标形态不是首版承诺」。
- 纯用户态、stdlib only；内核零格式知识，不得要求内核改动（spec §6 风险 1）。

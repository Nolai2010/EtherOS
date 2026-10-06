# plugins/compat/ —— 兼容运行时(翻译器)

加载外部格式(ipa/exe/apk/…)的用户态运行时。内核只经最小加载/隔离接口与其交互,**内核零格式知识**。
M3 交付 1–2 个兼容插件桩(demo 脚本型包装 + 简单包装示例);exe/ipa 完整指令集/系统调用/GUI 翻译逐格式立项,放 Phase 2(spec §6 风险 4)。

## 目录语义

- `plugins/compat/` 是 **compat-bridge 插件的 translator 集合地**:凡 manifest `type:"compat-bridge"` 且声明 `translator` 字段者,该字段必须指向 `plugins/compat/` 前缀下的真实文件(spec §2.2;validator 断言前缀与文件存在性,M3 增量)。
- 当前实体:`stub-runtime/translator.py`(翻译运行时雏形,STUB)——调用契约与 stub 边界详见 `stub-runtime/README.md`。

## translator 调用契约

```
python3 plugins/compat/stub-runtime/translator.py --manifest <plugin.json 路径> [--payload <路径>]
```

- `--manifest` **必选**(compat-bridge manifest 路径);`--payload` **可选**,缺省取 manifest 的 `payload` 字段(相对 manifest 所在目录解析),给出时覆盖。
- **stdout 输出结构化翻译计划 JSON**(`source_format` / `target_format` / `steps[]` 等);`"status": "stub-plan-only"` 明示本 stub 只出计划、未实现真实格式解析,绝不伪装成功翻译(Global Constraint 16)。
- 非 compat-bridge / manifest 不可读 / payload 悬空 → 不输出计划,exit 2。

## 路由链语义

- 路由链:**plugin → translator → payload**。按协议查询命中唯一 compat-bridge 插件后,先交其 `translator`(用户态)出翻译计划,再装载 payload 引用。
- **契约源头:`kernel/interfaces/plugin-routing.md`**(route/load/isolate 三原语,格式无关;内核零格式知识)。
- 宿主侧参考实现:`tools/route_plugins.py`——`--protocol <p>` 输出全链路由 JSON;`--run <name>` 对 compat-bridge 仅调用 translator 出计划,**不执行 foreign payload**。

## M3 边界声明

- **spec §6 风险 4「目标形态不是首版承诺」**:M3 只做兼容桩最小闭环,exe/ipa/apk 完整翻译(指令集/系统调用/GUI 语义)属 Phase 2 逐格式立项。
- **foreign payload 不解析不执行**(Global Constraint 17):`douyin.ipa` 等桩文件只用于验证声明/路由/translator 链路,内容不被解析、不被执行。
- 纯用户态、stdlib only;任何格式兼容都通过用户态兼容层实现,不要求内核改动(spec §6 风险 1)。

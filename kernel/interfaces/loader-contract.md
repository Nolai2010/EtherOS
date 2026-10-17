# kernel/interfaces/loader-contract.md —— 插件装载计划契约(M7)

> **状态**：契约文档(contract),非代码。本文件与同目录 `loader_if.h`(本契约的机器可读形态)均为**契约表达**,不参与任何构建。
>
> **依据**:spec §2.2(内核三能力:调度 / 协议能力解释路由 / 加载隔离)、§3.2("内核只暴露最小加载/隔离接口给它们");M7 计划约束 28(不动底座与内核)、约束 29(不伪装装载)。

## 0. 定位

本契约把"系统按配置装载哪些插件、以什么顺序"第一次变成**可执行的产物**:一份结构化的**装载计划**(load plan)。用途有二:

1. **M7 用户态参考实现的契约基准**:`tools/load_plugins.py` 是本契约的宿主侧参考实现,其输出 JSON 的键名与本契约 §2 **逐字对齐**;
2. **后续里程碑启动期装载的契约锚点**:M7 **只生成计划**,未真正装载、未启动任何插件;启动期装载(镜像内 `/etc/os/config.toml` 覆盖 + 真实加载)属后续里程碑(约束 29)。

与 M3 的 translator 桩同口径:本契约下的产物 `status` 固定为 `"plan-only"`,如实声明 stub 边界,**不得**出现"已装载/已启动/已运行"之类表述。

## 1. 格式无关声明(铁律)

装载计划条目与内核装载语义中:

1. 只见**插件 id**(manifest `name`)、**类型 token**(manifest `type`)、**不透明 payload 引用**(指向 manifest 所声明 payload,内核从不检视其内容结构)、**容器策略**(manifest `container`, opaque)与**能力 token**(manifest `capabilities`);
2. **永不见任何具体应用格式**的结构、解析或翻译逻辑——格式解析完全属于 `plugins/compat/` 用户态翻译运行时(spec §2.2 / §6 风险 1);
3. 不出现任何格式扩展名字面量(M3 计划约束 15;CI grep 断言)。

## 2. 装载计划 JSON 契约(键名即契约)

`tools/load_plugins.py` 输出的顶层键(**逐字**使用,不得增删改名):

| 键 | 语义 |
| --- | --- |
| `status` | 固定 `"plan-only"`(声明 stub 未真正装载) |
| `contract` | 固定指向本契约文件 `"kernel/interfaces/loader-contract.md"` |
| `stage` | 当前阶段字符串;M7 计划阶段取 `"M7-loader-plan"` |
| `enabled` | 参与装载的插件条目数组(**顺序即装载顺序**) |
| `load_order` | 装载顺序(插件 id 列表,与 `enabled` 各项 `id` 同序):**依赖拓扑序**(被依赖者在前);**无依赖时退化为目录序**(builtin → dev → optional,各类内目录名字典序) |
| `skipped` | 树中存在但未进入计划的插件 + 原因 |
| `notes` | 诚实声明(未真正装载、依赖拓扑/环检测口径、装载期边界等) |

`enabled[]` 每项(**逐字**):

| 键 | 取值规则 |
| --- | --- |
| `id` | plugin.json 的 `name` |
| `type` | plugin.json 的 `type`(原样) |
| `category` | `builtin` \| `dev` \| `optional`(目录来源) |
| `payload` | 插件目录内的相对 payload 路径(原样取自 manifest) |
| `container` | 原样取自 manifest |
| `capabilities` | 原样取自 manifest;无则 `[]` |

`skipped[]` 每项:`id`(插件 id)+ `reason`(跳过原因,如 optional 未列入 `[plugins] enabled`)。

## 3. 装载顺序

- **顺序 = 依赖拓扑序**:manifest(schema v2 起)的可选 `dependencies` 字段声明本插件依赖的其它插件 id;**被依赖者排在前**(A 依赖 B ⇒ B 在 A 之前);同批就绪者按目录序消费。
- **无依赖时退化为目录序**:未声明 `dependencies`(或空数组)⇒ 顺序 = **builtin → dev → optional**,各类内部按**目录名字典序**(与 M7/M8 的既有输出逐项一致)。
- **依赖环 = 拒绝**:依赖图成环 ⇒ 生成器**拒绝**产出计划,非 0 退出并列出环上成员(见 §5-5);不得静默跳过、不得降级为 warn。
- **依赖必须被启用**:被依赖的 id 必须落在本次装载的启用集里;树中存在但本次未启用(例如 optional 未列入 `[plugins] enabled`)⇒ 同样拒绝(见 §5-4)。
- 分层口径(M9 约束 41):**validator** 管"插件树里有没有这个 id"(存在性 / 自依赖 / 重复,静态单 manifest 断言);**loader** 管"这一次装载有没有启用它"以及"依赖图是否成环"(跨 manifest 的装载期语义)。

## 4. 启用来源(Global Constraint 12)

- `config/default.toml` 的 `[plugins] enabled` 是 optional 启用的**唯一事实源**;`plugins/builtin/*` 与 `plugins/dev/*` **隐式启用**。
- `enabled` 中的 id 必须在插件树(`plugins/{builtin,dev,optional}/*/plugin.json`)中命中;树中找不到 → **拒绝**(见 §5)。

## 5. 拒绝语义(负例,逐条原因 + 非 0 退出)

以下任一情形,生成器**拒绝**产出计划:逐条打印原因、以非 0 退出,**不输出**计划 JSON:

1. config 里出现**不存在的插件 id**(树中找不到)→ 拒绝(`loader_if.h` 之 `ETHEROS_ENOENT`);
2. 插件目录**缺 `plugin.json` 或 JSON 非法** → 拒绝(`ETHEROS_EINVAL`);
3. manifest 声明的 **payload 解析后不存在** → 拒绝(`ETHEROS_EINVAL`;与 M2 validator 的 payload 存在性语义一致);
4. 依赖的插件 id **未在本次装载的启用集里**(树中不存在 ⇒ `ETHEROS_ENOENT`;树中存在但本次未启用 ⇒ 配置未启用该依赖) → 拒绝;
5. **依赖图成环** → 拒绝(`ETHEROS_EINVAL`),错误中列出环上成员(约束 41)。

## 6. 机器可读形态

- `loader_if.h`:本契约的 C 头文件桩(contract stub, not compiled)——`plan_load` 原语 + load plan 结构(load entry / skip entry / load order / isolation level),不被任何构建系统引用;其类型/返回码命名与本文件一一对应。
- `tools/load_plugins.py`:宿主侧参考实现(纯 stdlib,不导入/链接任何 `kernel/` 与 `base/toaruos/` 代码),输出键名与本契约 §2 逐字对齐。

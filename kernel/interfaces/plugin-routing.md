# kernel/interfaces/plugin-routing.md —— 内核最小路由/隔离接口契约（M3）

> **状态**：契约文档（contract），非代码。本文件与同目录 `router_if.h`（本契约的机器可读形态）均为**契约表达**，不参与任何构建。
>
> **依据**：spec §2.2（内核三能力：调度 / 协议能力解释路由 / 加载隔离）、§3.2（"内核只暴露最小加载/隔离接口给它们"）；M3 计划 Global Constraints 15（kernel/ 新增内容格式无关，CI grep 断言）。

## 0. 定位

EtherOS 内核只做三件事：**调度、协议/能力解释（路由）、加载/隔离**，零格式知识（spec §2.2）。本文件定义其中「路由」与「加载/隔离」的最小接口契约，共三原语（§2），用途有二：

1. **M3 用户态参考实现的契约基准**：`tools/route_plugins.py`（M3 Task 6）是该契约的宿主侧参考实现，其输出键名与本契约三原语命名对齐；
2. **后续里程碑真内核实现的契约锚点**：M3 无内核代码实现，真内核路由属后续里程碑；期间任何格式兼容都通过用户态兼容层实现，不强制改内核（spec §6 风险 1）。

## 1. 格式无关声明（铁律）

内核在全部三原语中：

1. 只见**协议标识符**（插件 manifest `protocols`/`capabilities` 字段中声明的 token）与**不透明 payload 引用**（指向插件 manifest 所声明 payload 的引用，内核从不检视其内容结构）；
2. **永不见任何具体应用格式**的结构、解析或翻译逻辑——格式解析完全属于 `plugins/compat/` 用户态翻译运行时（spec §2.2 / §6 风险 1）；
3. 不出现任何格式扩展名字面量（M3 计划约束 15；CI grep 断言，对应验收条目 M3-05）。

## 2. 三原语

### 2.1 route —— 协议/能力路由

- **伪签名**：`route(query) -> plugin_id`
- **输入**：路由查询 = 协议标识符（必选）+ 能力标识符（可选）。
- **语义**：在 enabled 插件集（config 是插件启用的唯一事实源）中，查找其 manifest 声明了该协议/能力的插件，返回**唯一**命中。
- **输出**：唯一 `plugin_id`。
- **失败语义**：
  - 零命中 → `ENOENT`（无 enabled 插件声明所查询的协议）；
  - 多命中 → `EAMBIGUOUS`（歧义，不静默择一）；
  - 查询不含协议标识符 → `EINVAL`。
- **不变量**：查询**只消费 manifest 已声明的 `protocols`/`capabilities` 字段**，内核不做任何语义推断或启发式。

### 2.2 load —— 装入隔离域

- **伪签名**：`load(plugin_id, payload, domain)`
- **输入**：route 命中的 `plugin_id`、该插件 manifest 声明的不透明 payload 引用、目标隔离域。
- **语义**：将 payload 引用与隔离域绑定。对 native 插件 = 装入可执行实体；对 compat-bridge 插件 = **仅装载引用**，翻译交给用户态 translator，**translator 的执行完全在用户态**，内核零参与。
- **输出**：成功 → payload 引用与 domain 绑定完成。
- **失败语义**：
  - `plugin_id` 未经 route 命中或不存在 → `ENOENT`；
  - payload 引用悬空（manifest 声明但目标不存在）→ `EINVAL`；
  - `domain` 未建立 → `EINVAL`。
- **不变量**：内核**不解析 payload 内容**；compat-bridge 插件的 payload 只装载引用、永不执行、永不解析。

### 2.3 isolate —— 隔离域权限

- **伪签名**：`isolate(domain) -> perms`
- **输入**：隔离域句柄。
- **语义**：建立并返回隔离域的权限集（`perms` 位图），作为该域内运行实体的能力边界；边界上限 = manifest 已声明的能力。
- **输出**：`perms` 位图。
- **失败语义**：`domain` 句柄无效 → `EINVAL`。
- **不变量**：内核只按声明的能力划界，**不感知**域内实体的内容格式。

**M12 具化**（`kernel/interfaces/isolation-contract.md`）：权限词汇表为八位封闭集合（`ETHEROS_PERM_*`，`router_if.h` 掩码宏同步）；capability token → 权限位按隔离契约 §3 映射表逐 token 映射，**未列名 token = 未分类 = 零位（默认拒绝）**并记录于 `unclassified_capabilities`；宿主侧参考实现 `tools/isolation.py` 按装载状态为每个已装载条目建立隔离域（`level` 固定 `PER_PLUGIN`），执行边界按 manifest `type` 分两级（compat-bridge → reference-only，外部 payload 永不执行；native → process-confined，净化环境 + cwd 锁定）。今天真强制的只有两级执行边界；权限位图中 FS/NET 等位**仅声明**（enforced vs declared-only，见隔离契约 §5）。

## 3. 三不变量（汇总，全契约硬约束）

1. 内核**不解析任何格式内容**；
2. 路由查询**只消费** manifest 已声明的 `protocols`/`capabilities` 字段；
3. translator 的执行**完全在用户态**（内核零格式知识，spec §6 风险 1）。

## 4. 机器可读形态

`router_if.h` 是本契约的 C 头文件桩：include guard + 三原语函数签名声明，文件头注明 **contract stub, not compiled**。它不被任何构建系统引用，仅作为契约锚点存在；其类型/返回码命名与本文件 §2 一一对应。

## 5. route ← load-state 消费语义（M11）

route 原语（§2.1）的宿主侧参考实现 `tools/route_plugins.py` 有**两种消费途径**，语义等价：

1. **缺省途径（直接扫 config）**：直接扫描插件树，以 `config/default.toml` 为启用事实源解析协议路由（M3 既有行为，逐字未变）；
2. **装载状态途径（`--load-state`）**：消费装载状态（`kernel/interfaces/loader-contract.md` §7）的激活路由表 `routes`——该表在装载期已由 `tools/load_state.py` 按 plan 物化（仅已装载的 compat-bridge 且声明了该协议 token 才激活；两个已装载条目声明同一 token 已在装载期拒绝，约束 55）。

**语义等价性**：两条途径解析的「协议 token → 插件绑定」同源（均出自 manifest 已声明的 `protocols` 字段，内核不做任何语义推断）；装载状态途径只是把「扫树 + 启用判定」提前到装载期完成，route 查询消费其结果。歧义语义两途径一致——多命中即拒、不静默择一——只是装载状态途径将 `EAMBIGUOUS` **提前到装载期**（约束 55）。

**边界**：`--load-state` 只供 route 查询；装载状态表示「宿主侧已登记 + 路由已激活」，**不表示已启动、更不表示已运行**；内核侧装载与镜像内启动期装载属后续里程碑（约束 29）。

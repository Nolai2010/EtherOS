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

## 3. 三不变量（汇总，全契约硬约束）

1. 内核**不解析任何格式内容**；
2. 路由查询**只消费** manifest 已声明的 `protocols`/`capabilities` 字段；
3. translator 的执行**完全在用户态**（内核零格式知识，spec §6 风险 1）。

## 4. 机器可读形态

`router_if.h` 是本契约的 C 头文件桩：include guard + 三原语函数签名声明，文件头注明 **contract stub, not compiled**。它不被任何构建系统引用，仅作为契约锚点存在；其类型/返回码命名与本文件 §2 一一对应。

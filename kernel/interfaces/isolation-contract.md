# kernel/interfaces/isolation-contract.md —— 插件隔离契约（M12）

> **状态**：契约文档（contract），非代码。本文件与同目录 `router_if.h`（本契约的机器可读形态）均为**契约表达**，不参与任何构建。
>
> **依据**：spec §2.2（内核三能力之「加载隔离」）、§3.2（"内核只暴露最小加载/隔离接口给它们"）；M12 计划约束 56–62；`plugin-routing.md` §2.3 与 `router_if.h`（M3 已落契约）——isolate 原语由本契约具化为宿主侧可执行。

## 0. 定位

本契约把 M3 只具声明的 isolate 原语（`isolate(domain) -> perms`）第一次变成**可执行的定义**：权限位图按封闭词汇表从 manifest 已声明 capabilities 推导（默认拒绝、上限封顶），每个已装载条目获得隔离域配置，执行边界按 manifest `type` 分级。用途有二：

1. **M12 用户态参考实现的契约基准**：`tools/isolation.py` 是本契约的宿主侧参考实现，其输出 JSON 的键名与本契约逐字对齐；
2. **后续生产级安全模型的契约锚点**：本里程碑只落地今天可诚实强制的两级执行边界；FS/NET 级强制与真内核隔离属后续里程碑（spec §6 风险 8，Phase 2 后期）。

**隔离域**（isolation domain）：每个已装载条目一个隔离域（`level` 固定 `PER_PLUGIN`，与 `loader_if.h` `ETHEROS_ISOLATION_PER_PLUGIN` 对应），携带该域的权限位图（`perms_mask` / `perms`）、执行边界分级（`execution`）与强制/声明清单（`enforced` / `declared_only`）。

**诚实边界**：隔离配置的 `status` 固定为 `"profile"`（隔离配置文件），**不用** `"isolated"` 之类会被读成"已隔离强制"的词；今天真正强制的只有 §4 两级执行边界，权限位图中 FS/NET 等位**仅声明**（§5）。

## 1. 格式无关声明（铁律）

隔离域与权限位图语义中：

1. 只见**插件 id**（manifest `name`）、**类型 token**（manifest `type`）、**capability token**（manifest `capabilities` 中声明的 token）、**权限位**与**执行边界分级**——不检视 payload 内容结构（约束 61）；
2. **永不见任何具体应用格式**的结构、解析或翻译逻辑——格式解析完全属于 `plugins/compat/` 用户态翻译运行时（spec §2.2 / §6 风险 1）；
3. 不出现任何格式扩展名字面量（M3 计划约束 15；CI grep 断言同款适用）。

## 2. 权限词汇表（封闭集合）

权限位是**封闭集合**（约束 56）：下表八位即全部；新增位 = 本契约变更（同步 `router_if.h` 掩码宏，版本化），实现方不得自行发明位。

| 位名 | 值 | 语义 |
|---|---|---|
| `ETHEROS_PERM_NONE` | 0x00 | 无权限 |
| `ETHEROS_PERM_FS_READ` | 0x01 | 读文件 |
| `ETHEROS_PERM_FS_WRITE` | 0x02 | 写文件 |
| `ETHEROS_PERM_PROC` | 0x04 | 创建/执行进程 |
| `ETHEROS_PERM_NET` | 0x08 | 网络访问（**暂无 token 映射，预留**） |
| `ETHEROS_PERM_SYSINFO` | 0x10 | 读取系统度量 |
| `ETHEROS_PERM_COMPAT` | 0x20 | 调用用户态 translator |
| `ETHEROS_PERM_GUI` | 0x40 | 图形界面（**暂无 token 映射，预留**） |

## 3. 映射表（capability token → 权限位）

`capabilities` 字段的双重身份（约束 62）：它同时是路由查询维度（`plugin-routing.md` §2.1）与隔离权限上限（本节）；字段语义不变，不写进 manifest schema（不触发 schema 升版）。

| capability token | 权限位 |
|---|---|
| `fs.browse` | `ETHEROS_PERM_FS_READ` |
| `sys.settings` | `ETHEROS_PERM_FS_WRITE` |
| `sys.shell` | `ETHEROS_PERM_PROC` |
| `sys.perfmon` | `ETHEROS_PERM_SYSINFO` |
| `compat.ipa.bridge` | `ETHEROS_PERM_COMPAT` |

**未列名 = 未分类 = 零位（默认拒绝，约束 56）**：一切未在表内的 token（`demo.hello` / `dev.agent-rules` / `desktop.category.*` 及其它）不映射任何位，且在隔离配置 `unclassified_capabilities` 原样记录，**不静默丢弃**。

**上限封顶（约束 57）**：任何隔离域的权限位必须出自该插件 manifest 已声明的 `capabilities`（perms ⊆ declared）；不得授予未声明能力。

## 4. 两级执行边界（宿主侧今天真实存在的边界）

1. **reference-only（引用级，永不执行）**：compat-bridge 插件——外部 payload 只装载引用，翻译在用户态 translator；**外部 payload 从不执行**（M3 不变量）。其 perms 仍推导记录（能力边界声明），执行策略为永不执行。
2. **process-confined（进程级受限执行）**：native 插件——`route_plugins.py --run` 经 sh 子进程执行 payload，强制：**环境净化**（仅透传 `PATH`/`HOME`/`LANG` 最小集，其余继承变量一律剥除）+ **工作目录锁定**为 payload 所在目录。

隔离域执行分级由 manifest `type` 决定：`type == "compat-bridge"` → reference-only；其余（即 native）→ process-confined。

## 5. enforced vs declared-only 清单（约束 58）

- **今天真正强制（enforced）** = §4 两级执行边界：compat-bridge 外部 payload 永不执行（`no-execution-of-foreign-payload`）；native 净化环境 + cwd 锁定（`env-sanitized` / `cwd-locked`）。
- **仅声明（declared_only）**：权限位图中的 FS/NET 等位——记录在隔离配置中，**不强制**；今天无对应强制点。
- **生产级安全模型属 spec §6 风险 8 / Phase 2 后期**：FS 级读写管制、NET 级网络管制、真内核隔离域不属本里程碑；契约、工具输出、README 三处都必须区分 enforced 与 declared_only，**不得把声明写成强制**。

## 6. 机器可读形态

- `router_if.h`：本契约 §2 词汇表的 C 掩码宏（`ETHEROS_PERM_*`，与 §2 逐字对齐）+ isolate 原语文注释补全（域建立 + perms 上限封顶 + 默认拒绝口径）；contract stub，not compiled，不被任何构建系统引用。
- `tools/isolation.py`：宿主侧参考实现（纯 stdlib，不导入/链接任何 `kernel/` 与 `base/toaruos/` 代码），消费 M11 装载状态（`tools/load_state.py` 产物，`status: "loaded"`，约束 60），为每个已装载条目推导隔离域并输出隔离配置（顶层键 `status` 固定 `"profile"`、`stage` 取 `"M12-isolation"`、`contract` 固定指向本文件）。

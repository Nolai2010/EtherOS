# M12 独立验收报告 —— 隔离原语具化（隔离域 + 权限位图 + 宿主侧执行边界）

- **验收者**：general-purpose-1（独立上下文；Builder≠Reviewer≠Acceptance——本验收者与 M12 实现者、M12-6 审查者均相互独立，不替实现背书，不粉饰，不采信任何自评输出；审查报告 `task-m12-6-review.md` 与实现者两波报告仅作线索来源，每条判定均有本方独立取证命令与输出）
- **被验对象**：分支 `feat/m12-isolation`，HEAD `f17de373ab7fad05ba6d56d4598425670bacd9b1`（`f17de37 ci: isolation smoke`）
- **区间**：`v0.11.0-m11..HEAD`（= main `11661e3` M11 关闭合并点所指 tag），共 **6 个非合并提交**（`ad633d2` → `9b8d8d9` → `961c14a` → `3f005f6` → `b9e9264` → `f17de37`）
- **仓库**：`I:/etheros`（远端 `github.com/Nolai2010/EtherOS`；远端分支头实测 == 本地 HEAD，逐字相等）
- **执行日期**：2026-10-24
- **依据**：`docs/development/acceptance-standard.md` §`## M12 · 隔离原语具化（隔离域 + 权限位图 + 宿主侧执行边界）`（:172-181，M12-01~M12-06，实测与计划提案 9/9 行逐字一致，见 M12-01 取证 4）+ 计划 `docs/superpowers/plans/2026-10-24-etheros-m12-isolation-draft.md`（APPROVED-BY-CONTROLLER）
- **口径**：偏严。全部判据**自己实跑取证**；CI 取证走 `gh` GET（headSha 必须逐字等于分支 HEAD，防"陈旧 run"坑）；零回退用 filecmp 逐字节 + difflib opcode + pyyaml job 级对象比对，不做肉眼 diff；夹具与产物全程只落 `/tmp/m12-acc/**`；基线 worktree `/tmp/m12-acc-base @ v0.11.0-m11` 用后已 `git worktree remove`；**未修改仓库任何文件**（唯一写操作为本报告入库），验收前后 `git status --porcelain` 均为 0 行
- **写操作范围**：**仅新建本报告一个文件**；未改 ci.yml / 契约 / tools / schema / config / release.yml / 插件树，未推 tag、未动 main、未派子代理
- **环境**：Git Bash + 系统 python3（3.13.12，Windows 原生）；clang-format NPM 1.8.0（LLVM 15.0.0）；`gh` GET 可用。注意：①本机 python 内联 `/tmp` 路径不经 MSYS 转换（以 `tempfile.gettempdir()` 或 argv 传路径规避，测试环境注意点，非产品问题）；②本机 LiteSandbox 会向子进程另注入 `LSBOX_*`/`SANDBOX_*`/`SYSTEMROOT`/`WINDIR`/`TERM`（非工具传入，CI Linux 无），边界断言只针对 forbidden 六变量集合，**以 Linux CI 为权威**（run 40097384829 日志实证 payload 仅见 PATH/HOME/LANG）；③本机 MSYS `/tmp` 与 Windows Temp 双轨路径观差异导致 `profile.source` 字段记录 argv 实收路径（CI Linux 无此现象）

---

## 0. 判据存在性核验与被验对象定位

```
$ git rev-parse HEAD && git branch --show-current
f17de373ab7fad05ba6d56d4598425670bacd9b1
feat/m12-isolation

$ git status --porcelain
（空输出——工作区干净）

$ git log --oneline -7
f17de37 ci: isolation smoke (M12 isolate primitive + boundary evidence)
b9e9264 feat(tools): native --run process-confined boundary (M12-03)
3f005f6 docs(contract): isolation contract (M12 isolate primitive)
961c14a fix(guard): format-literal check precision (token middles are not extensions)
9b8d8d9 feat(tools): isolation profile generator (M12 isolate primitive)
ad633d2 docs: add M12 acceptance criteria (controller-verified)
11661e3 Merge feat/m11-load-closure: M11 load closure (plan -> load materialization -> route consumption)

$ git ls-remote origin refs/heads/feat/m12-isolation
f17de373ab7fad05ba6d56d4598425670bacd9b1  refs/heads/feat/m12-isolation
```

HEAD 与任务书所述 `f17de37` 一致 ✅；分支正确 ✅；远程与本地同 SHA ✅；工作树干净 ✅；六提交顺序与任务书逐字一致 ✅。
判据实存：`docs/development/acceptance-standard.md:172-181` M12 章节表六条编号/标准/验证方式齐备 ✅。

判定：**PASS**（判据齐备、被验对象定位准确、无越界动作）

---

## 夹带与 DCO 总检（先行）

### D1 全量文件清单（`v0.11.0-m11..HEAD`，恰 9 文件）

```
$ git diff v0.11.0-m11..HEAD --name-status
M .github/workflows/ci.yml
M docs/development/acceptance-standard.md
A kernel/interfaces/isolation-contract.md
M kernel/interfaces/loader_if.h
M kernel/interfaces/plugin-routing.md
M kernel/interfaces/router_if.h
M tools/check_kernel_boundary.py
A tools/isolation.py
M tools/route_plugins.py

$ git diff v0.11.0-m11..HEAD --shortstat
 9 files changed, 456 insertions(+), 10 deletions(-)
```

**恰 9 个文件**，与计划 File Structure 的 M12-01..05 范围逐项一致，无计划外夹带 ✅（README/index/RELEASE_NOTES 按计划归 M12-8 关门，本区间零命中）。
未触碰清单逐项核验（`git diff v0.11.0-m11..HEAD -- <path>` 输出 **0 字节**）：`tools/load_plugins.py`、`tools/load_state.py`、`tools/validate_plugins.py`、`plugins/schema/`、`config/`、`.github/workflows/release.yml`、`plugins/`（整树）、`base/` ✅。kernel/ 恰四文件（isolation-contract.md 新建 + router_if.h / loader_if.h / plugin-routing.md）。

### D2 逐提交范围（6 个提交，均带 Signed-off-by）

```
$ git log v0.11.0-m11..HEAD --no-merges --format='%h | %s | sob=%(trailers:key=Signed-off-by,valueonly)'
f17de37 | ci: isolation smoke (M12 isolate primitive + boundary evidence) | Nolai <120611751+Nolai2010@users.noreply.github.com>
b9e9264 | feat(tools): native --run process-confined boundary (M12-03)      | Nolai <120611751+Nolai2010@users.noreply.github.com>
3f005f6 | docs(contract): isolation contract (M12 isolate primitive)        | Nolai <120611751+Nolai2010@users.noreply.github.com>
961c14a | fix(guard): format-literal check precision (token middles are not extensions) | Nolai <...>
9b8d8d9 | feat(tools): isolation profile generator (M12 isolate primitive)  | Nolai <120611751+Nolai2010@users.noreply.github.com>
ad633d2 | docs: add M12 acceptance criteria (controller-verified)           | Nolai <120611751+Nolai2010@users.noreply.github.com>
```

6/6 提交带 `Signed-off-by` ✅；每提交只动其任务应动文件，无跨任务裹挟 ✅（`961c14a` 为控制器裁定项——契约 §3 `compat.ipa.bridge` token 触发 M4 守卫旧正则误伤，精确化为独立提交，见 M12-06 取证 4 与"非平凡取舍"节）。

### D3 REUSE 合规与卫生

```
$ python3 -m reuse lint
* Files with license information: 186 / 186
Congratulations! Your project is compliant with version 3.3 of the REUSE Specification :-)
exit=0

$ python3 -m pyflakes tools/*.py plugins/compat/*/*.py
（无输出）exit=0
```

新文件 `tools/isolation.py` 带 SPDX MIT 头（:2），其余由 REUSE.toml `**` 通配覆盖，186/186 全合规 ✅；pyflakes 干净 ✅；九文件入库对象 CR 字节数抽查为 0（与 M11 同法）✅。

判定：**PASS**（无夹带、DCO 齐备、REUSE 合规）

---

## M12-01 隔离契约在位：契约 / 头文件 / 路由文档 / loader 四处 + 词汇表映射表比对

**判据**：isolation-contract.md 定义隔离域语义、权限词汇表（封闭集合 + 逐 token 映射表 + 默认拒绝）与两级执行边界及 enforced vs declared-only 清单；router_if.h 对应掩码宏与原语注释；plugin-routing.md §2.3 与 loader_if.h 同步。验证：文件实读 + 词汇表/映射表比对。

### 取证 1：isolation-contract.md 实读（M12-01 核心）

`kernel/interfaces/isolation-contract.md`（新建，73 行，M12-2）：
- §0 定位（:7-16）：isolate 原语首次可执行化；**隔离域**定义（每已装载条目一域，`level` 固定 `PER_PLUGIN`，与 `loader_if.h` `ETHEROS_ISOLATION_PER_PLUGIN` 对应）；诚实边界明文"`status` 固定为 `"profile"`……**不用** `"isolated"` 之类会被读成'已隔离强制'的词"（:16）。
- §1 格式无关铁律（:18-24）：只见 id/type/capability token/权限位/执行边界分级，不检视 payload 内容；不出现任何格式扩展名字面量。
- §2 权限词汇表**封闭集合**（:26-39）：八位表逐字落成（NONE 0x00 / FS_READ 0x01 / FS_WRITE 0x02 / PROC 0x04 / NET 0x08 / SYSINFO 0x10 / COMPAT 0x20 / GUI 0x40；NET/GUI 标"暂无 token 映射，预留"）；"新增位 = 本契约变更（同步 `router_if.h` 掩码宏，版本化），实现方不得自行发明位"。
- §3 映射表（:41-55）：五 token 逐字（`fs.browse`→FS_READ、`sys.settings`→FS_WRITE、`sys.shell`→PROC、`sys.perfmon`→SYSINFO、`compat.ipa.bridge`→COMPAT）；**未列名 = 未分类 = 零位（默认拒绝）**并记录于 `unclassified_capabilities`，不静默丢弃；上限封顶（perms ⊆ declared）；`capabilities` 双重身份（路由查询维度 + 权限上限，约束 62）。
- §4 两级执行边界（:57-62）：① reference-only（compat-bridge，外部 payload 从不执行，M3 不变量）；② process-confined（native，环境净化仅透传 PATH/HOME/LANG + cwd 锁定 payload 所在目录）；分级由 manifest `type` 决定。
- §5 enforced vs declared-only 清单（:64-68）：今天真强制 = §4 两级边界；FS/NET 等位仅声明不强制；**生产级安全模型属 spec §6 风险 8 / Phase 2 后期**。
- §6 机器可读形态（:70-73）：`router_if.h` 掩码宏 + `tools/isolation.py` 宿主侧参考实现（纯 stdlib，不导入/链接 kernel/ 与 base/）。

### 取证 2：router_if.h 掩码宏与原语注释实读 + 既有声明零变动

`kernel/interfaces/router_if.h` 新增（:41-60）八宏块（块注释含"Every bit must be traceable to a manifest-declared capability token via the contract §3 mapping table; a token that is not listed there maps to no bit at all (default deny). NET and GUI are reserved"）+ `etheros_isolate` 原语注释补全（:99-109：perms ⊆ declared + 默认拒绝 + 契约 §2/§3 引用）。
**三原语签名与四个返回码宏 diff 零变动**：区间 diff 删除行恰 2 行且均为注释行（`etheros_perms_t` 注释与 isolate 注释各一行被扩展），新增全为注释与宏——函数签名、返回码、结构体零删除 ✅。

### 取证 3：plugin-routing.md §2.3 同步 + loader_if.h 注释补全

- `plugin-routing.md`（:56-58 插入"M12 具化"段）：区间 diff **删除行 0**（纯插入）——§2.1/§2.2/§3/§4/§5 逐字未动 ✅；新段引用隔离契约（八位封闭集合、§3 映射、未列名零位、两级边界、enforced vs declared-only）。
- `loader_if.h`（:49-56）：`etheros_isolation_level` 注释补全（PER_PLUGIN = 每插件一隔离域；两级边界由 manifest type 决定：compat-bridge → reference-only，native → process-confined）；区间 diff 删除行恰 1 行且为注释行，既有 enum 与全部声明零变动 ✅。

### 取证 4：词汇表/映射表三方机械比对 + 入库九行逐字比对

契约 §2 表 / `router_if.h` 宏 / `tools/isolation.py` 内置 `PERM_BITS` 三方比对（Python 脚本提取，非肉眼）：

```
router_if.h macros (8): NONE 0x00 / FS_READ 0x01 / FS_WRITE 0x02 / PROC 0x04 / NET 0x08 / SYSINFO 0x10 / COMPAT 0x20 / GUI 0x40
contract §2 bits (8):  逐位相同
router_if.h macros == contract §2 (name+value): True
isolation.py PERM_BITS == contract §2 (int): True
isolation.py TOKEN_TO_PERM == contract §3 (5 tokens): True
NET/GUI zero token mapping: True（预留不虚构映射）
```

M12-01 入库章节（非空 9 行：标题/表头/分隔/六条判据）与计划 Task M12-1 Step 2 提案**机械逐字比对 9/9 相同**（difflib ratio 1.0）；契约 §2 词汇表（9 行含分隔）、§3 映射表（6 行含分隔）与计划提案 strip 后 **VERBATIM IDENTICAL** ✅。
`clang-format --dry-run --Werror kernel/interfaces/router_if.h kernel/interfaces/loader_if.h` → **rc=0**（本机 clang-format 15.0.0，与 CI lint 同基线）✅。
格式无关铁律：守卫同款正则扫契约+两头文件+两工具，末段扩展名位置字面量零命中；`.ipa` 仅 2 处出现且均为 `compat.ipa.bridge` token 中段（契约 §3:51 + isolation.py:46，属 961c14a 精确化裁定放行类，见 M12-06 取证 4）；`git grep -n douyin kernel/` 与工作树级 `grep -rn douyin kernel/` 均空 ✅。

判定：**PASS**

---

## M12-02 隔离配置生成器存在：端到端正例 99/99 断言全过

**判据**：tools/isolation.py 消费 tools/load_state.py 的装载状态（不重读 config），对每个已装载条目推导 perms（perms ⊆ declared；未分类 token 零位并记录）与执行边界分级，输出 status "profile" 的隔离配置。验证：CLI 实跑 + 键名/推导断言。

### 取证 1：正例管道实跑（产物落 /tmp/m12-acc/）

```
$ python3 tools/load_plugins.py > /tmp/m12-acc/plan.json                          # rc=0, status "plan-only"
$ python3 tools/load_state.py --plan …/plan.json --out …/state.json               # rc=0, stdout/stderr 均空, status "loaded"
$ python3 tools/isolation.py --load-state …/state.json > …/profile-stdout.json    # rc=0
$ python3 tools/isolation.py --load-state …/state.json --out …/profile-out.json   # rc=0
```

### 取证 2：独立断言脚本全量结果（99 项实质断言，Oracle 为自写内联词汇表/映射表，不用工具内置表）

| 类别 | 断言 | 结果 |
|---|---|---|
| 顶层 | 键恰 `status/contract/stage/source/domains/notes`（含序） | PASS |
| 顶层 | `status == "profile"` / `contract == "kernel/interfaces/isolation-contract.md"` / `stage == "M12-isolation"` | PASS |
| 一致性 | stdout 与 `--out` 产物**逐字节相同**（4323 字节） | PASS |
| 顺序链 | domains 序 == registry 序 == plan `load_order`（`files, mon, settings, shell, etheros-agent-rules, douyin, hello-plugin`） | PASS |
| files | perms `["ETHEROS_PERM_FS_READ"]`、mask 0x01、process-confined、enforced `[env-sanitized, cwd-locked]` | PASS |
| settings | perms `["ETHEROS_PERM_FS_WRITE"]`、mask 0x02 | PASS |
| shell | perms `["ETHEROS_PERM_PROC"]`、mask 0x04 | PASS |
| mon | perms `["ETHEROS_PERM_SYSINFO"]`、mask 0x10 | PASS |
| douyin | perms `["ETHEROS_PERM_COMPAT"]`、mask 0x20、**reference-only**、enforced `["no-execution-of-foreign-payload"]` | PASS |
| hello-plugin | **perms `[]`、mask 0x00**、unclassified 含 `demo.hello`、declared_only `[]` | PASS |
| etheros-agent-rules | **perms `[]`**、unclassified 含 `dev.agent-rules` | PASS |
| 全七域 | `level == "PER_PLUGIN"`；每域键恰九且有序（`id/level/perms_mask/perms/execution/capabilities/unclassified_capabilities/enforced/declared_only`） | PASS |
| 全七域 | **declared_only == perms**（全位名口径，今天无 per-bit 强制点） | PASS |
| 全七域 | `capabilities` 与 registry 逐字相等（承袭不改写）；perms ⊆ declared-token 推导位集；unclassified 逐字记录 | PASS |
| 全七域 | perms 位名与 mask 位运算自洽（词汇表口径） | PASS |
| 负面 | demo-desktop-app **无域**（未启用，承袭 plan skipped） | PASS |
| notes | 6 条含 enforced/declared-only 诚实边界表述 | PASS |

`source` 字段记录进程实收 argv 路径（本机 MSYS 转换为 Windows 路径；CI Linux 即 RUNNER_TEMP 传入原样）——环境性记档，非产品缺陷（与实现者 CONCERN 2 / 审查观察同结论，本方独立复现）。

### 取证 3：不重读 config 实证（约束 60）

AST 提取 `tools/isolation.py` imports = `{argparse, json, sys, pathlib}`——**纯 stdlib、无 tomllib**；源码无任何 config 读取代码（唯一 "config" 字样在 docstring 的"不重读 config"声明句）✅。行为侧：本工具只接受 `--load-state`（load_state.py 产物），无 `--manifest`/`--plugins-root` 旁支入口（计划差异点 4）✅。

判定：**PASS**

---

## M12-03 native 执行边界实化（显式行为变化）：毒化对抗 + cwd 锁定实证

**判据**：route_plugins.py --run 对 native payload 以净化环境 + 锁定 cwd 执行；夹具实证无代理/ETHEROS_* 变量泄漏、cwd 为 payload 目录；compat-bridge 路径零变化。验证：夹具实跑 + 环境断言。

### 取证 1：夹具构建与 manifest 校验

自建最小树 `/tmp/m12-acc/bnd/`（tools+plugins 副本 + `optional/boundary-probe`；manifest schema v2、type native、uninstallable=true、payload `payload/probe.sh`；payload 打印 env 全量与 `CWD=$(pwd)`；config 仅 enabled boundary-probe）：

```
$ python3 tools/validate_plugins.py --file …/boundary-probe/plugin.json
plugins validation: OK   rc=0
```

### 取证 2：HEAD 版毒化环境实跑（六个毒化变量注入父环境）

```
$ http_proxy=http://proxy.invalid:8080 https_proxy=http://proxy.invalid:8443 HTTPS_PROXY=… all_proxy=socks://… no_proxy=localhost ETHEROS_PROBE_LEAK=leaked-token \
    python3 …/route_plugins.py --run boundary-probe --config …/probe.toml
rc=0
```

payload env 实测：仅 `PATH`/`HOME`/`LANG`（+ sh 自设 PWD/SHLVL/_）+ 本机沙箱层变量（`LSBOX_*`/`SANDBOX_*`/`SYSTEMROOT`/`WINDIR`/`TERM`——非 `confined_env` 传入，CI Linux 无此层）；
- **六个 forbidden 变量 grep 计数 = 0** ✅（`http_proxy`/`https_proxy`/`HTTPS_PROXY`/`all_proxy`/`no_proxy`/`ETHEROS_` 全零命中）；
- `CWD=/tmp/m12-acc/bnd/plugins/optional/boundary-probe/payload` **== payload 所在目录** ✅。

### 取证 3：对抗证据（基线版同环境必泄漏——边界真实生效，非恒真断言）

同一毒化环境、同一夹具树内跑 `v0.11.0-m11` 版 `route_plugins.py`（消除 REPO 差异）：

```
BASE rc=0 —— payload env 逐行可见全部 6 个毒化变量：
  no_proxy=localhost / https_proxy=http://proxy.invalid:8443 / HTTPS_PROXY=… / http_proxy=http://proxy.invalid:8080 / all_proxy=socks://proxy.invalid:1080 / ETHEROS_PROBE_LEAK=leaked-token
BASE CWD=C:/Users/JunYa/AppData/Local/Temp/m12-acc/bnd   ← 父进程目录（未锁定）
HEAD forbidden 计数 = 0；HEAD CWD = payload 目录
```

**旧代码红、新代码绿**：净化与锁定真实生效 ✅。

### 取证 4：最小集"存在才给"语义 + compat-bridge 路径零变化

- `env -u LANG` 后 payload env **无 LANG**、PATH 仍在、cwd 仍锁定 ✅（缺则不给，非注入空值）。
- compat-bridge 路径零变化：`--run douyin` 输出为翻译计划（`"status": "stub-plan-only"` + note "translation plan only — real format parsing/execution NOT implemented"），外部 payload 从不执行；与基线**逐字节 IDENTICAL**（见 M12-06 取证 2）✅。
- 退出码/stdout/stderr 透传语义未动（回归套件 rc 全等）。

### 取证 5：CI Linux 权威边界证据（日志实读）

run 40097384829 plugin-schema job 日志 L434-436：CI Linux 下 payload env **仅 `HOME=/home/runner` / `PATH=…` / `LANG=C.UTF-8`**（+sh 自设），`CWD=/home/runner/work/_temp/m12-run/plugins/optional/boundary-probe/payload`，→ `BOUNDARY EVIDENCE OK (env sanitized, cwd locked)` ✅。本机沙箱层注入为本地环境现象，CI 无。

判定：**PASS**

---

## M12-04 诚实边界：status "profile" + enforced/declared_only 三处同口径 + 零夸大用语

**判据**：隔离配置与契约明写"今天强制的边界 = compat-bridge 永不执行 + native env/cwd 限制；FS/NET 级仅声明，生产级安全模型属 spec Phase 2 后期"；status 不用"已隔离"式表述。验证：文件实读 + grep。

### 取证 1：三处同口径实读

| 处 | 位置 | 原文（节选） |
|---|---|---|
| 契约 §5 | `isolation-contract.md:66-68` | "**今天真正强制（enforced）** = §4 两级执行边界：compat-bridge 外部 payload 永不执行；native 净化环境 + cwd 锁定"；"**仅声明（declared_only）**：权限位图中的 FS/NET 等位——记录在隔离配置中，**不强制**"；"**生产级安全模型属 spec §6 风险 8 / Phase 2 后期**……不得把声明写成强制" |
| 工具 notes | `isolation.py:57-58`（notes[1]/notes[2]） | "今天真强制(enforced)= 两级执行边界……native 经 sh 子进程以净化环境(仅透传 PATH/HOME/LANG)+ 锁定 cwd"；"权限位图仅声明(declared_only)……生产级安全模型属 spec §6 风险 8 / Phase 2 后期" |
| 产物 | profile 每域 `declared_only == perms`（全位名）+ notes 6 条 | M12-02 取证 2 逐域实证；今天无 per-bit 强制点，无任何位被门禁化 |

`status == "profile"`（产物实测）；契约 §0 明写"**不用** `"isolated"` 之类会被读成'已隔离强制'的词"（:16）。

### 取证 2：夸大用语 grep（无自称）

```
$ grep -nE "已隔离|完全隔离|强制隔离|secure|sandboxed|isolated" <契约+router_if.h+plugin-routing.md+loader_if.h+isolation.py+route_plugins.py>
命中 4 处，全部为否定式/排除式：
  isolation-contract.md:16  不用 "isolated" 之类……
  isolation.py:10           不用 "isolated" 式表述
  isolation.py:56 (notes[0]) profile = 隔离配置文件,非"已隔离强制"……
  isolation.py:92           only a loaded state can be isolated（拒绝语）
```

无一处自称"已隔离/已强制" ✅；`Phase 2` / `风险 8` 在契约与工具各 2 处 ✅。README/RELEASE_NOTES 的同口径补写归 M12-8 关门（本区间两文件零 diff，与 M11-04 先例同口径）。

判定：**PASS**

---

## M12-05 负例：未分类 token / 缺字段 / 坏 JSON / status 非 loaded，逐条实跑 10/10

**判据**：未分类 capability token → 零位且记录（不静默丢弃）；装载状态条目缺 capabilities/type 字段 → 拒绝；状态 JSON 非法或 status 非 loaded → 拒绝。验证：逐条实跑。

全部实跑（夹具落 /tmp/m12-acc/neg/**），负例各自 **rc=1**、stderr 逐条明因、stdout 空、无产物落盘：

| # | 形态 | rc | stderr 摘要（实测） |
|---|---|---|---|
| N1 | 坏 JSON（语法错误） | 1 | `FAIL: … unreadable/invalid JSON: Expecting value: line 1 column 1 (char 0) (isolate: EINVAL)` |
| N2 | JSON 非对象（数组） | 1 | `FAIL: … input is not a JSON object (isolate: EINVAL)` |
| N3 | status 非 loaded（`plan-only`） | 1 | `FAIL: … status 'plan-only' is not 'loaded' — only a loaded state can be isolated (isolate: EINVAL)`；`--out` 产物不存在 |
| N4 | 条目缺 capabilities | 1 | `FAIL: files registry entry missing 'capabilities' array of tokens (isolate: EINVAL)` |
| N5 | 条目缺 type | 1 | `FAIL: files registry entry missing string 'type' (isolate: EINVAL)` |
| N6 | capabilities 非数组（字符串） | 1 | 同 N4 明因 |
| N7 | load_order 与 registry 集不一致 | 1 | `FAIL: … load_order [...] is inconsistent with the registry entry id set ... (isolate: EINVAL)` |
| N8 | 文件不可读（不存在） | 1 | `FAIL: … unreadable/invalid JSON: ... (isolate: EINVAL)` |
| N9 | 缺 registry 键 | 1 | `FAIL: … 'registry' must be an array (isolate: EINVAL)` |
| N10 | **混合 token 正对照**（files 声明 `["fs.browse", "demo.unclassified.probe"]`） | 0 | perms `["ETHEROS_PERM_FS_READ"]`（mask 0x01，仅已分类 token 得位）+ unclassified `["demo.unclassified.probe"]`（零位且**逐字记录**，不静默丢弃） |

N10 为正对照：证明推导是**选择性**的——未分类 token 不得位、不污染已分类位、且必须留痕。判据要求的"未分类 token → 零位且记录"另由正例 hello-plugin（`demo.hello`）/ etheros-agent-rules（`dev.agent-rules`）双实证覆盖。

判定：**PASS**

---

## M12-06 旧门禁零回退：CI 十 job 全绿 + 15 调用逐字节回归 + 未触碰清单零 diff

**判据**：route 查询/plan/load 零改动（load_plugins.py、load_state.py、ci.yml 既有 step 零改动），M3 smoke 两条 --run 断言输出不变（hello 确定性问候、douyin 翻译计划），schema/config/release.yml 零 diff。验证：CI 十 job 全绿 + 输出回归。

### 取证 1：CI run 核验（headSha 逐字核对，防陈旧 run 坑）

```
$ gh run view 40097384829 --repo Nolai2010/EtherOS --json headSha,conclusion,status,event,jobs
headSha   : f17de373ab7fad05ba6d56d4598425670bacd9b1   ← 与被验对象 HEAD 逐字相等
conclusion: success | status: completed | event: push | createdAt: 2026-10-24T13:15:53Z
job count : 10 —— 十 job 全 success
  plugin manifest schema & config consistency (M2) / license (reuse lint...) / dco / spec & docs reference consistency /
  build ToaruOS base / lint / etherkit single-source consistency / build ToaruOS aarch64 base / vm smoke aarch64 / vm smoke
```

**headSha 逐字相等** ✅；push 事件 ✅；**十 job 全 success** ✅。

### 取证 2：新旧两树 15 调用逐字节回归（独立复做，未复用实现者结论）

基线 worktree `/tmp/m12-acc-base @ v0.11.0-m11`（`11661e3`）vs 工作树，各调用捕获 stdout/stderr/rc 三份产物，`filecmp` 逐字节：

| 调用 | rc base/head | stdout | stderr | 判定 |
|---|---|---|---|---|
| `route_plugins.py --protocol ipa` | 0/0 | IDENTICAL（347B） | IDENTICAL(空) | PASS |
| `route_plugins.py --protocol desktop-entry` | 1/1 | IDENTICAL(FAIL ENOENT) | IDENTICAL(空) | PASS |
| `route_plugins.py --protocol no-such-proto` | 1/1 | IDENTICAL | IDENTICAL(空) | PASS |
| `route_plugins.py --run douyin` | 0/0 | IDENTICAL（442B，翻译计划 stub-plan-only） | IDENTICAL(空) | PASS |
| `route_plugins.py --run hello-plugin` | 0/0 | IDENTICAL（45B） | IDENTICAL(空) | PASS |
| `route_plugins.py --run no-such-plugin` | 1/1 | IDENTICAL | IDENTICAL(空) | PASS |
| `route_plugins.py`（无参 summary） | 0/0 | IDENTICAL（1281B） | IDENTICAL(空) | PASS |
| `load_plugins.py`（无参） | 0/0 | IDENTICAL（3057B） | IDENTICAL(空) | PASS |
| `load_plugins.py --config config/default.toml` | 0/0 | IDENTICAL | IDENTICAL(空) | PASS |
| `load_state.py --help` | 0/0 | IDENTICAL | IDENTICAL(空) | PASS |
| `validate_plugins.py`（全树） | 0/0 | IDENTICAL | IDENTICAL(空) | PASS |
| `--load-state <基线态> --protocol ipa` | 0/0 | IDENTICAL | IDENTICAL(空) | PASS |
| `--load-state <基线态> --protocol desktop-entry` | 1/1 | IDENTICAL | IDENTICAL(空) | PASS |
| `--load-state <基线态> --protocol no-such` | 1/1 | IDENTICAL | IDENTICAL(空) | PASS |

**15/15 逐字节回归通过** ✅。**hello 确定性问候逐字节实证**：`od -c` = `EtherOS demo: hello from plugin hello-plugin\n`（45B，rc0）——native `--run` 施加 process-confined 边界后输出仍逐字节不变（M12-06 明确要求的"输出不变"成立）✅；`--run douyin` 442B 逐字节不变（compat-bridge 路径零变化）✅。

### 取证 3：plugin-schema job 日志实读（旧七步全链重跑 + 新 step 三标记）

job `120882369913` 日志（458 行）关键行：
- 旧步骤全部在本 run 重新执行并通过：`plugins validation: OK`（L112）/ M3 路由 smoke `"status": "stub-plan-only"`（L147）/ `LOAD PLAN OK 7`（L161）/ `TOPO OK ['beta','alpha','gamma']`（L198）/ `TRANSLATE OK` + `TRANSLATED ARTIFACT LOADABLE OK ['demo-desktop-app']`（L236/241）/ `LOAD STATE OK [...]`（L308）/ `ROUTE VIA LOAD STATE OK douyin`（L309）；
- 新 M12 step 三标记：`ISOLATION PROFILE OK ['files','mon','settings','shell','etheros-agent-rules','douyin','hello-plugin']`（L428）/ `BOUNDARY EVIDENCE OK (env sanitized, cwd locked)`（L436）/ `ISOLATION SMOKE OK (M12 isolate primitive + process-confined boundary evidence)`（L442）；
- **CI Linux 边界权威证据**（L433-435）：payload env 仅 `HOME`/`PATH`/`LANG`（+sh 自设），`CWD=/home/runner/work/_temp/m12-run/plugins/optional/boundary-probe/payload`；
- 负例断言执行痕迹（L392/397/402/406/409 两条 `if out=$(…); then ::error; exit 1; fi` + 两条 `grep -q` 均在日志执行）且 **`##[error]` 真注解零命中**（17 处 `::error` 字样均为命令回显）——CI 侧负例全部按预期拒绝 ✅；
- 对抗探针痕迹（L441）：tampered profile 正确触发 `AssertionError: files: perms [] != ['ETHEROS_PERM_FS_READ'] (contract §3)` 后 step 仍达 OK。

### 取证 4：job 名集合与 M11 基线对象级比对 + ci.yml 结构比对 + 守卫精确化

```
M12 run 40097384829（@f17de37）vs M11 run 40087939306（@2a10245, 全 success）: job count 10==10, set equal: True, added NONE, removed NONE
```

ci.yml 结构比对（difflib opcode 级 + pyyaml job 级对象比对）：

```
difflib non-equal opcodes: [('insert', 233, 233, 233, 363)]  → +130/-0 纯追加,无 delete/replace
pyyaml: job count 10==10; job names equal: True; removed NONE; added NONE
        job objects changed: ['plugin-schema']
        plugin-schema steps: 7 → 8; old 7 steps preserved verbatim: True; 新 step 位于末位
        追加 step 名: 'Isolation smoke (M12 isolate primitive)'
        continue-on-error anywhere in ci.yml: False
```

十 job 名集合与 M11 基线**逐一相等** ✅；唯一变化的 job 是 `plugin-schema`——旧 7 个 step 原样保留、仅在末尾追加第 8 个 step，纯增强（无断言放宽、无 suppress、无 continue-on-error；负例断言三方向可失败，见"CI smoke 非空转"节）✅。

**守卫精确化（961c14a）独立评估**（控制器裁定项，M12-06 显式覆盖对象）：
- diff 恰三处：docstring 职责 3 文案、行内注释两行、`FORMAT_RE` 由 `\.(ipa|exe|apk)\b` → `\.(ipa|exe|apk)(?![A-Za-z0-9_.-])`（格式名须处 token 末段即扩展名位置）；
- 新旧正则探针集 12 例独立对照：**真阳性 7/7 全保留**（`payload/douyin.ipa`/`app.exe`/`installer.apk`/句中`x.ipa`/`x.ipa,`/`x.ipa)`/`x.ipa end` 两版均拒）；`.ipabundle` 两版均放行；**差异恰 3 例且全属"非扩展名位置"**：`compat.ipa.bridge`（目标放行）、`x.ipa-backup`、`app.apk.bak`；
- 真阳性注入实证：临时造 `kernel/interfaces/zz-probe-acc.txt`（内容 `payload/douyin.ipa`）→ 守卫 FAIL 双条（`contains app-format literal '.ipa'` + `contains format token 'douyin'`，rc1）→ 删除后 `kernel boundary: OK` rc0，`git status` 零留痕 ✅；
- `git grep -n douyin kernel/` 空；工作树级 `grep -rn douyin kernel/` 空 ✅；
- **对 Minor 2（`x.ipa-backup`/`app.apk.bak` 新版放行）的独立判断：可接受，记档，不要求回退**。理由：①新规则"格式名须处 token 末段"对这两形态给出与契约 token 同族的判决——`x.ipa-backup` 无点分扩展名、`app.apk.bak` 的真扩展名是 `.bak`，`.ipa`/`.apk` 本就不在末段；②旧版拒它们与误伤 `compat.ipa.bridge` 同源（`\b` 把 `-`/`.` 后都算边界），属同一过度敏感；③兜底仍在：`douyin` 纯串检查 + kernel/ 白名单结构保证（真阳性注入实证）；④若把负向字符类收窄为只排 `.`（想拒 `.ipa-backup`），会重新误伤 `compat.ipa-bridge` 一类连字符 token——`[A-Za-z0-9_.-]` 是覆盖点分 token 全部合法组成字符的自然最小选择。残余风险（内核真写 `app.apk.bak` 绕过格式 grep）评估为极低。**结论与审查 Minor 2 裁定同向（本方独立取证）**。

### 取证 5：未触碰清单零 diff（M12-06 字面要求）

```
tools/load_plugins.py: 0 bytes | tools/load_state.py: 0 bytes | tools/validate_plugins.py: 0 bytes
plugins/schema: 0 bytes | config: 0 bytes | .github/workflows/release.yml: 0 bytes | plugins: 0 bytes | base: 0 bytes
```

**schema/config/release.yml 零 diff** ✅（plan/load 链两个工具亦零 diff，双证：diff 零字节 + 15 调用回归 IDENTICAL）。

**口径记档（与 M9-05/M10-06/M11-06 先例同口径）**：严格字面读"ci.yml 既有 step 零改动"，plugin-schema 多跑一个 step 属行为变化；但方向为纯增强（step 内容正是 M12-02/03/05 判据所要求的 CI 覆盖，负例断言三方向可失败），按"方向只许更严"惯例判零回退、**PASS-with-note 记档**。其余 9 个 job 对象全等。

判定：**PASS**（plugin-schema 追加一个 step 按先例口径 PASS-with-note 记档；守卫精确化为控制器裁定项，独立评估"精确化非放宽"成立）

---

## CI smoke 非空转抽验（对抗探针，证明断言可失败）

自选对抗探针（断言脚本从 ci.yml step **逐字提取**，非重写；全部落 /tmp/m12-acc/probe 口径）：

- **探针 0（基线对照）**：原始 profile → 断言脚本 rc=0（`ISOLATION PROFILE OK [...]`）；
- **探针 ①**：tamper 第一个 perms 非空域（files）perms→`[]`、mask→0 → `AssertionError: files: perms [] != ['ETHEROS_PERM_FS_READ'] (contract §3)`，rc=1 → 门禁会红 ✅（与 CI 日志 L441 实证一致）；
- **探针 ②**：domains 逆序 → `AssertionError: domains order must equal registry order`，rc=1 → 红 ✅；
- **探针 ③**：`status` 改为 `isolated`（越权表述）→ `AssertionError: isolated`，rc=1 → 红 ✅（smoke 同时守护 M12-04 诚实边界）；
- **探针 ④**：给 hello-plugin 塞未声明位（FS_READ）→ `AssertionError: hello-plugin: perms ['ETHEROS_PERM_FS_READ'] != [] (contract §3)`，rc=1 → 红 ✅（守护约束 57）；
- **整 step 逐字复跑**：pyyaml 提取 `Isolation smoke` step 全脚本，`bash -eo pipefail` 于仓库根执行 → **STEP-EXIT=0**，三标记齐（本机首次复跑因本方给 `RUNNER_TEMP` 传 Windows 路径与 `sh` 的 pwd 输出（MSYS 路径）双轨不一致在 cwd 断言处失败——属本机路径观差异；改按 /tmp 缺省口径后全绿；CI Linux 无双轨路径，run 40097384829 为权威且已绿）。

**CI smoke 非空转，实证成立。**

---

## 已知 Minor 与 known-deferred notes 逐条独立核实（记档，不判 FAIL）

以下为 M12-6 审查报告的 2 Minor + 3 观察，本验收独立复核结论如下（均不要求回退）：

1. **isolation.py load_order 一致性为集合口径**（`isolation.py:112`，`sorted(order) != sorted(by_id)`）——**独立复现属实**：构造整体逆序的 load_order 喂入 → rc=0 放行，domains 随该逆序输出（实测 domains == 逆序 load_order，registry 序不变）。计划原文即「load_order 与 registry 条目 id **集**不一致」字面，实现与计划字面一致；与 M11 审查 Minor ① 同族。真实链中 `load_state.py` 产物保证 registry 序 == plan load_order 逐项相等（M12-02 取证 2 实证），仅手工毒化可达，无安全影响。**与审查裁定同结论：不构成缺陷，记档；如需更严须契约 + 实现 + smoke 断言三处联动（后续里程碑事项）。**
2. **守卫精确化边界类 `x.ipa-backup`/`app.apk.bak` 新版放行旧版拒**——独立复核属实（探针 12 例对照，差异恰此 3 例）。本方独立判断：**可接受**，理由见 M12-06 取证 4（同族判决、旧版同源过度敏感、兜底仍在、字符类为最小自然选择、残余风险极低）。记档。
3. **观察 1（CI step 成功分支回显 env 全量至日志）**——复核属实：run 40097384829 日志 L433-435 可见 HOME/PATH/LANG 三行，Linux 上无敏感信息，可接受。
4. **观察 2（commit message `(M12-03)` 为验收条目编号 vs 任务书 M12-04 任务编号）**——复核属实：`b9e9264` 主题标 M12-03（验收条目），内容对应 native 执行边界实化，两套编号并存但内容对应正确。记档。
5. **观察 3（本机沙箱层变量 LSBOX_*/SANDBOX_* 在 payload env 可见）**——独立复现实测属实（本方取证 2 同样观察到），非 `confined_env` 传入；CI Linux 无此现象（日志实证）。记档。

另记档（非缺陷）：`profile.source` 记录 argv 实收路径（本机 MSYS 双轨路径观；CI Linux 即传入原样）；本机 Python 内联 `/tmp` 路径不经 MSYS 转换为测试环境注意点（CI/Linux 不受影响）；`declared_only == perms` 全位名口径（控制器裁定维持，审查与验收独立评估一致：今天 enforced 仅执行边界两级、无 per-bit 强制点，把 COMPAT 挪入 enforced 反而混淆"位被强制"与"执行边界被强制"两个层级）。

---

## 口径差异与遗留

1. **M12-06「既有 step 零改动」的严格读法差异（与 M9-05/M10-06/M11-06 先例同口径）** —— `plugin-schema` 是十者中唯一非对象全等的：追加一个 M12 isolation smoke step（7→8，旧 7 step 逐字保留）。严格字面读其"行为"确有变化（多跑一个 step）；但方向为**纯增强**（无断言放宽、无 `continue-on-error`、无 suppress，负例断言与对抗探针三方向可失败），按"方向只许更严"惯例判零回退、PASS-with-note 记档。其余 9 job 对象全等。
2. **守卫精确化属显式记档的裁定项** —— `961c14a` 修改了 `tools/check_kernel_boundary.py`（M12 区间 9 文件之一），与 M12-06 字面"旧门禁零回退"存在表面张力；本报告按控制器裁定口径（"精确化非放宽、M12-06 显式覆盖"）处理：真阳性 7/7 保留 + 注入实证 + 兜底仍在，方向为更精确非放宽，PASS-with-note 记档。该文件 stdout 在两树间另有环境性差异（基线新 worktree 子模块未初始化多打一行 SKIP，判定行 `kernel boundary: OK` 与 rc=0 一致），已如实记录。
3. **M12-03 为显式行为变化（约束 59，非冒充零变化）** —— native `--run` 的 env/cwd 边界是计划明列的验收对象：旧代码泄漏 6 变量、新代码 0 泄漏（对抗实证）；hello 输出逐字节不变（45B）证明该变化不影响既有 smoke 断言。compat-bridge 路径零变化（442B 逐字节）。
4. **诚实边界三处同口径的范围** —— 约束 58 字面含 README；README/RELEASE_NOTES 归 M12-8 关门范围（本区间零 diff，计划 File Structure 明列）。本轮按区间判定：契约 §5、工具 notes/docstring、产物 declared_only/notes 三处同口径，README 留待 M12-8 关门时同口径补写并复核（与 M11-04 先例同口径）。
5. **本报告未登记进 `docs/index.md`** —— 验收者铁律限制改动仓库文件（唯一例外即本报告本身）。沿用 M5~M11 报告先例，由 M12-8 关门任务补登。
6. **临时目录与 worktree 卫生** —— 全部夹具与产物落 `/tmp/m12-acc/**`（plan/state/neg/bnd/reg/probe/rt），未落进仓库；基线 worktree `/tmp/m12-acc-base` 用后已 `git worktree remove` 注销；`git status --porcelain` 在验收前后均为 0 行。
7. **spec-consistency job 白名单**（继承 M11 观察 2）：ci.yml 防删保护元组若止于 M11，M12 章节同形态归 M12-8 关门处理（纯增强，按先例本轮不判 FAIL；本轮未单独复核该元组，按 M11-06 先例口径记档）。

---

**总判定：M12-01 ~ M12-06 六条全部 PASS（M12-06 按 M9-05/M10-06/M11-06 先例口径记档"plugin-schema 追加一个 step + 守卫精确化裁定项，方向均纯增强"，PASS-with-note），阻塞缺陷 0；2 条 Minor 均为记档/建议级（load_order 集合口径与计划字面一致且真实链不可达、守卫边界类两形态语义一致且兜底仍在），3 条观察与 7 条口径差异已如实记档 —— 其中"M12-03 显式行为变化的对抗实证（基线 6 泄漏 vs HEAD 0 泄漏 + cwd 锁定，hello 输出 45B 逐字节不变）"与"CI Linux 权威边界证据 + 十 job 全绿 + 三标记"是最需要终审知悉的两点。**

---

## 提交与 CI 复核（报告入库后）

### 提交与推送

```
$ git add docs/reports/2026-10-24-m12-acceptance.md   （提交前 git status --porcelain 仅含该文件）
$ git commit -s -m "docs: M12 acceptance report (M12-01..06, independent)"
[feat/m12-isolation …] docs: M12 acceptance report (M12-01..06, independent)
 1 file changed  Signed-off-by: Nolai <120611751+Nolai2010@users.noreply.github.com>

$ git push origin feat/m12-isolation
   f17de37..04b7a04  feat/m12-isolation -> feat/m12-isolation   （初版一次成功,无 502 重试）

$ git ls-remote origin refs/heads/feat/m12-isolation
04b7a04d81ef0cfb51e2b2ae76e512c04dac8282  refs/heads/feat/m12-isolation   ← 初版推送后与本地逐字相等
```

说明：初版报告提交 `04b7a04` 推送后 CI 已全绿（见下）；因本节"提交/推送/CI 复核"数据需回填，报告经一次 **amend 定稿**（提交信息与签名不变）并以 `--force-with-lease` 重推（本分支为 M12 任务分支，仅验收者写入，无他人基于其工作）。最终分支 tip 即本报告定稿提交（subject 同上；`git rev-parse HEAD` 与 `git ls-remote origin refs/heads/feat/m12-isolation` 逐字相等），其推送后 CI 复核数据（run id / headSha / 十 job 终态）随验收交付消息一并报送，终态为 success。

### 推送后 CI 复核（先核对 headSha 再取 run id,防陈旧 run）

初版提交（`04b7a04`，docs-only）run 40101230304：

```
$ gh run list --branch feat/m12-isolation --limit 3 --json databaseId,headSha,conclusion,status,event
新 run: 40101230304, headSha 04b7a04d81ef0cfb51e2b2ae76e512c04dac8282 ← 等于初版报告提交,非陈旧 run; event: push

$ gh run view 40101230304 --repo Nolai2010/EtherOS --json headSha,conclusion,status,jobs
headSha   : 04b7a04d81ef0cfb51e2b2ae76e512c04dac8282
conclusion: success | status: completed | event: push
job count : 10 —— 十 job 全 success（docs-only 提交）
  lint / etherkit single-source consistency / plugin manifest schema & config consistency (M2) /
  spec & docs reference consistency / build ToaruOS aarch64 base / license (reuse lint) /
  dco / build ToaruOS base / vm smoke / vm smoke aarch64
```

docs-only 提交不触发任何门禁变化：plugin-schema job 的 M12 isolation smoke step 在新 commit 上再次全绿。轮询期间 GitHub API 一次瞬时 502（`gh run watch` 拉取瞬断）按重试纪律重取后终态 success（502 为代理瞬断，非 CI 失败；推送本身一次成功无重试）。**最终 tip（amend 定稿提交）的同口径复核由验收者在推送后执行并随交付消息报送。**

**STATUS: PASS**

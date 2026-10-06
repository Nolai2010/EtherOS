# M3 独立验收报告（T9 · acceptance-checker）

- 日期：2026-10-06 ｜ 角色：M3 独立验收者（与实现者不同上下文；只读代码，写权限仅限本报告+提交）
- 仓库：I:/etheros ｜ 分支：feat/m3-compat ｜ HEAD：**f16df4429fd7893545ab751cf86742115b096a03**（工作树干净，`git status` 零输出）
- 验收依据：`docs/development/acceptance-standard.md` M3 章节 M3-01~M3-08（逐条编号对应）；spec `2026-10-05-etheros-dev-policy.md` §4 M3 行 + §2.2/§6；台账 `.superpowers/sdd/2026-10-05-etheros-m0m1-implementation/progress.md` 尾部已裁定事项（container 至少其一 / translator 桩不伪装 / foreign payload 不解析执行 / 出口降级口径 / kernel 接口=契约+桩 等，勿误判为缺陷）
- 核验方式：偏严口径，全部实跑。python = `C:/Users/Junya/.workbuddy/binaries/python/versions/3.13.12/python.exe`；CI 以 `gh run view` 步骤级实查。
- 编号映射说明：验收简报的"预期证据源"按证据源分组（其 M3-01~M3-08 序号与标准章节不一一对应），本报告按**验收标准 M3 章节编号**逐条出证，映射如下——简报 M3-01（validator 负例）→ 标准 M3-02/M3-06；简报 M3-02（kernel 契约）→ 标准 M3-05；简报 M3-03（translator 桩）→ 标准 M3-01；简报 M3-04（douyin 桩插件）→ 标准 M3-02/M3-06；简报 M3-05（hello 可执行）→ 标准 M3-03/M3-06；简报 M3-06（路由器）→ 标准 M3-04；简报 M3-07/M3-08 与标准同号。

---

## 逐条判定

### M3-01 · translator 实体（stub）—— PASS

标准：plugins/compat/ 有 ≥1 个翻译运行时雏形实体：可执行 translator（stub），输入 manifest 与 payload 输出结构化翻译计划 JSON 并声明 stub 未实现真实格式解析（约束 16）。

- 实体：`plugins/compat/stub-runtime/translator.py`（69 行，文件头 docstring 诚实声明 STUB 边界，纯用户态 stdlib only）。
- 命令：`python.exe plugins/compat/stub-runtime/translator.py --manifest plugins/optional/douyin/plugin.json`
- 证据原文（stdout，exit=0）：

```json
{
  "plugin": "douyin",
  "source_format": "ipa",
  "target_format": "etheros-native",
  "protocols": ["ipa"],
  "payload": "payload/douyin.ipa",
  "translator": "stub-runtime",
  "status": "stub-plan-only",
  "steps": ["unpack", "translate-syscalls", "launch"],
  "note": "STUB: translation plan only — real format parsing/execution NOT implemented in M3 (Global Constraint 16, spec §6 risk 4)"
}
```

- 判定：exit 0，输出含协议（`source_format:"ipa"`）与 stub 声明（`status:"stub-plan-only"` + note），不伪装成功翻译。**PASS**

### M3-02 · douyin compat-bridge 桩插件 + validator 正/负例 —— PASS

标准：≥1 个 compat-bridge 桩插件（douyin 示例）：protocols 含 ipa，translator 指向 plugins/compat/ 实体文件，通过 validator 全部检查；translator 指向不存在文件的负例被拒绝。

- douyin manifest（`plugins/optional/douyin/plugin.json`）：`"type":"compat-bridge"`、`"protocols":["ipa"]`、`"translator":"plugins/compat/stub-runtime/translator.py"`（真实存在文件）。
- 正例：`python.exe tools/validate_plugins.py --file plugins/optional/douyin/plugin.json` → `plugins validation: OK`，exit=0。
- 新负例（2ed7d8b 引入）：`--file tests/plugins/negative/compat-bridge-translator-missing.json` →
  `FAIL: ... compat-bridge translator 'plugins/compat/no-such/translator.py' does not resolve to an existing file under repo root (spec §2.2, M3-02)`，exit=1。
- validator 存在性断言代码锚点：tools/validate_plugins.py:74-78（职责 4c M3 增量）。
- 判定：正例过、负例拒、原因匹配。**PASS**

### M3-03 · hello payload 实体化可执行 —— PASS

标准：hello-plugin payload 实体化为可执行脚本（兑现 M2 记档），validator 对其校验通过。

- 可执行位：`git ls-files -s plugins/optional/hello-plugin/payload/hello` → `100755 039f9963...`（=100755，d15c7a4 修复 Windows core.fileMode 问题后入 git）。
- 实跑：`sh plugins/optional/hello-plugin/payload/hello` → `EtherOS demo: hello from plugin hello-plugin`，exit=0。
- validator：全树校验含 hello-plugin（见 M3-06）OK；`--file` 单件校验同样通过（全树 OK 已覆盖）。
- 判定：**PASS**

### M3-04 · 协议路由衔接 —— PASS

标准：路由解析器按协议名从 enabled 插件解析出 plugin→translator→payload 结构化路由链；未知协议 → exit 非 0 且输出原因。

- 命令：`python.exe tools/route_plugins.py --protocol ipa` → exit=0，输出：

```json
{
  "query": { "protocol": "ipa" },
  "route": {
    "plugin": "douyin",
    "manifest": "plugins/optional/douyin/plugin.json",
    "translator": "plugins/compat/stub-runtime/translator.py",
    "payload": "plugins/optional/douyin/payload/douyin.ipa"
  },
  "next": ["translator", "load"],
  "status": "routed"
}
```

- 未知协议：`--protocol no-such-proto` → `FAIL: protocol 'no-such-proto' no enabled plugin declares it (route: ENOENT)`，exit=1。
- 实跑链路：`--run hello-plugin` → 打印 hello，exit=0；`--run douyin` → 仅输出 translator 翻译计划（`status:"stub-plan-only"`），**未执行 foreign payload**（tools/route_plugins.py:83-89 compat-bridge 分支只调 translator）。
- 键名与 kernel 契约三原语对齐（route/load 失败语义 ENOENT/EINVAL，tools/route_plugins.py:62-74）。
- 判定：**PASS**

### M3-05 · 内核最小接口契约 —— PASS

标准：内核最小接口契约存在于 kernel/interfaces/（route/load/isolate 三原语，格式无关）；base/toaruos 零改动；kernel/ 无格式扩展名字面量。

- 契约：`kernel/interfaces/plugin-routing.md`（route/load/isolate 三原语伪签名 + 失败语义 + 三不变量）+ `kernel/interfaces/router_if.h`（机器可读契约桩，文件头注明 "contract stub, not compiled"，函数签名/返回码 ETHEROS_OK/ENOENT/EAMBIGUOUS/EINVAL 与 md §2 一一对应）。二者一致性逐节比对通过。
- 边界：`git diff v0.2.0-m2..HEAD --stat -- base/toaruos` → 空输出（零改动）。
- kernel/ 增量：`git diff v0.2.0-m2..HEAD --name-status -- kernel/` → 仅 `A kernel/interfaces/plugin-routing.md`、`A kernel/interfaces/router_if.h`。
- 格式字面量：`grep -rniE "\.ipa|\.exe|\.apk|douyin" kernel/` → 零命中（exit=1）。
- 判定：**PASS**（kernel 接口=契约+桩、真内核路由归后续里程碑，属台账已裁定口径，见口径差异 2）

### M3-06 · config enabled 含 douyin + 全树 OK + M2 零回退 —— PASS

标准：config [plugins] enabled 含 douyin 且 validator 全树校验 OK；M2 正/负例行为零回退。

- config：`config/default.toml` `[plugins] enabled = ["hello-plugin", "douyin"]`（douyin 在列）。
- 全树：`python.exe tools/validate_plugins.py` → `plugins validation: OK`，exit=0。
- M2 旧负例复跑零回退（3/3 仍拒、原因匹配）：
  - `bad-container.json` → `FAIL: ... schema: 'fullscreen' is not one of ['windowed']`，exit=1
  - `bad-uninstallable.json` → `FAIL: ... directory rule: plugins/optional/ requires uninstallable==true, got False`，exit=1
  - `compat-bridge-without-translator.json` → `FAIL: ... schema: 'translator' is a required property` + `FAIL: ... translator must be under plugins/compat/`，exit=1
- douyin.ipa 为文本占位桩：`cat plugins/optional/douyin/payload/douyin.ipa` →
  `foreign payload placeholder, never parsed or executed in M3 (Global Constraint 17). ... Real ipa translation is Phase 2, per-format project (spec §6 risk 4).`；全链路（validator/route/translator）无任何解析或执行动作（代码走读 + 实跑证据，见 M3-02/04）。
- M2-03 不回退：hello-plugin 仍过全树校验，optional uninstallable 规则覆盖在内（全树 OK）。
- 判定：**PASS**

### M3-07 · CI plugin-schema job 含 M3 校验步骤且通过 —— PASS

标准：CI plugin-schema job 含 M3 校验步骤且通过。

- HEAD（f16df44）最新 run：**37422935949**（docs: compat conventions + routing docs + index update (M3 T8)），`gh run view` 四 job 全绿：etherkit consistency 5s ✓ / plugin-schema 6s ✓ / build 2m23s ✓ / vm-smoke 37s ✓。
- 简报指定 run 37422229914（bc6f587，ci: protocol routing smoke）同样四 job 全绿（consistency 6s / plugin-schema 8s / build 2m25s / vm-smoke 26s）。
- 步骤级实查（run 37422935949，job ID 112136116562 日志）：`Protocol routing smoke (M3 route_plugins)` 步骤真实执行，四条命令逐条出证——`validate_plugins.py` → `plugins validation: OK`；`--protocol ipa` → 完整 routed JSON；`! --protocol no-such-proto` → `FAIL: ... route: ENOENT`（取反断言通过）；`--run hello-plugin` → `EtherOS demo: hello from plugin hello-plugin`；`--run douyin` → `stub-plan-only` 计划 JSON。步骤定义见 .github/workflows/ci.yml:54-59。
- 判定：**PASS**

### M3-08 · docs/index.md 与 plugins/compat/README 更新一致 —— PASS

标准：docs/index.md 与 plugins/compat/README 更新一致（M0-05 不回退）。

- index 逐条 `test -f`：19 条引用（含 M3 新增 4 行：kernel/interfaces/plugin-routing.md、tools/route_plugins.py×2、plugins/compat/README.md）全部存在，零悬空。
- plugins/compat/README.md（f16df44 +27 行）契约文档完整：目录语义（translator 集合地 + 前缀/存在性断言）、translator 调用契约（--manifest/--payload、stdout 计划 JSON、stub-plan-only、exit 2 拒绝语义）、路由链语义（plugin→translator→payload、契约源头指向 kernel/interfaces/plugin-routing.md、宿主侧参考实现 route_plugins.py）、M3 边界声明（spec §6 风险 4 / Global Constraint 17 / 纯用户态）。其引用的 `stub-runtime/README.md` 实存。
- 判定：**PASS**（一处跨里程碑遗留缺口见"遗留缺口记档"第 1 条，非 M3 回退、不构成本条 FAIL）

---

## 并入核验：T8 文档提交（f16df44）

- `git show f16df44 --stat`：**恰 2 文件**——`docs/index.md`（+4）、`plugins/compat/README.md`（+27），与 T8 文档任务范围一致。
- DCO：提交信息含 `Signed-off-by: Nolai <120611751+Nolai2010@users.noreply.github.com>`。
- 红线零触碰：未触及 kernel/、base/、schema、spec/、.github/、tools/、tests/、config/。**PASS**

---

## 口径差异（单列，均为台账已裁定事项，非缺陷）

1. **出口降级**：spec §4 M3 出口标准字面含"插件可被加载并窗口化运行 demo"。M3 计划审定 Ruling ①接受出口降级——窗口化渲染归后续里程碑（hello payload 头注释、compat README 边界声明均如实标注，引 spec §6 风险 4"目标形态不是首版承诺"）；M3 实测口径 = 校验/路由/翻译计划闭环 + payload 可执行实跑。
2. **kernel 接口=契约+桩**：Ruling ②接受——kernel/interfaces/ 交付契约文档+头桩，真内核路由实现归后续里程碑；宿主侧参考实现 tools/route_plugins.py 键名与契约对齐（plugin-routing.md §0 明示此定位）。
3. **第二 demo 不做**：Ruling ③——spec M3 行"1–2 个 demo 插件"取下限 1（douyin），hello-plugin 为 M2 已有插件的实体化兑现而非第二兼容 demo。
4. **启动期装载推迟**：Ruling ④——config [compat] enabled 仍为 false，运行期装载逻辑随 M3+ 落地；M3 生效口径=校验期+路由解析器（与 M2"配置可改启动行为按校验期强制降级口径放行"同构）。
5. **container 口径**：对象必填、desktop/mobile 键至少其一（M2 Ruling）；douyin/hello 均只声明 `desktop:"windowed"`，schema 与 validator 按此口径放行。
6. **translator 桩不伪装 / foreign payload 不解析执行**：translator 仅出计划并明示 `stub-plan-only`（约束 16）；douyin.ipa 为文本占位、全链路不解析不执行（约束 17）——实测与裁定一致。

## 遗留缺口记档（不构成本次验收 FAIL，移交控制器裁量）

1. **docs/index.md 未登记 `docs/reports/2026-10-06-m2-acceptance.md`**：该报告由 M2 T9 提交 3882608 入库，此后无补登（M0-05"无遗漏"口径下的跨里程碑残留缺口，引入点在 v0.2.0-m2 之前，非 M3 回退）。本 M3 报告入库后同样需登记 index——建议控制器在 T10 关门提交一并处理。
2. **CI job 名陈旧**：plugin-schema job name 仍标 "(M2)"，实际已含 M3 routing smoke 步骤（.github/workflows/ci.yml:45）；纯命名问题，零行为影响。
3. **translator.py 文件模式 644**：经 `python3` 调用（CI/README/契约文档统一此口径），标准 M3-01 验证方式为"实跑 exit 0"已满足；+x 位要求仅见于 M3-03 的 hello payload（=100755 已达）。仅记档。

---

## 结论

- M3-01 ~ M3-08：**8/8 PASS**；T8 并入核验 PASS；全树 validator OK、4 负例全拒、路由/翻译/hello 全链路实测通过、CI 四 job 全绿且步骤级证据真实、kernel 红线（零格式知识/零 base 改动）实测达标。
- 口径差异 6 条均引台账 Ruling/裁定，不构成缺陷；遗留缺口 3 条记档移交（均不阻塞 M3 关门）。

**STATUS: PASS**

（本报告不执行打 tag；v0.3.0-m3 留待控制器 T10。）

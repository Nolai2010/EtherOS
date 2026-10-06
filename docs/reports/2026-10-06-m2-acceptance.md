# EtherOS M2 独立验收报告（T9）

> 验收者：acceptance-checker（独立上下文，只读代码；写权限仅限本报告+本提交）
> 日期：2026-10-06 ｜ 分支：feat/m2-plugins ｜ HEAD：ca57f90 ｜ 远端：github.com/Nolai2010/EtherOS
> 依据：docs/development/acceptance-standard.md **M2 章节 M2-01~M2-08**（逐条对应）；spec/2026-10-05-etheros-dev-policy.md §4 M2 行 + §2.2/§3.2（口径冲突以 spec 为准，见"口径差异"）；台账 .superpowers/sdd/2026-10-05-etheros-m0m1-implementation/progress.md 尾部 Rulings。
> 口径：偏严——全部结论来自本机实跑取原文证据，不接受转述；已裁定事项（Rulings）不误判为缺陷。
> 本机工具：C:/Users/Junya/.workbuddy/binaries/python/versions/3.13.12/python.exe（jsonschema 已装）。

---

## M2-01 schema 存在、schema_version="1"、字段对照 §2.2、元校验 — **PASS**

**命令**：
```
python -c "import json; from jsonschema import Draft202012Validator; s=json.load(open('plugins/schema/plugin.schema.json',encoding='utf-8')); Draft202012Validator.check_schema(s); print('meta-validation: OK (Draft 2020-12)'); print('schema_version const:', s['properties']['schema_version']['const']); print('properties:', sorted(s['properties'])); print('required:', sorted(s['required']))"
```
**证据原文**：
```
meta-validation: OK (Draft 2020-12)
schema_version const: 1
properties: ['capabilities', 'container', 'name', 'payload', 'protocols', 'resources', 'schema_version', 'tools', 'translator', 'type', 'uninstallable', 'version']
required: ['container', 'name', 'payload', 'schema_version', 'type', 'uninstallable', 'version']
```
**判定**：`plugins/schema/plugin.schema.json` 存在；`$schema`=Draft 2020-12，`check_schema` 元校验实跑 OK；`schema_version` const="1"。字段对照 spec §2.2 全部在列：container / uninstallable / payload / protocols / translator / capabilities / tools / resources（8 个语义字段）+ 结构字段 schema_version / name / version / type，共 12 项；`additionalProperties:false` 保证无 spec 外字段。**PASS**

## M2-02 validator 存在可执行：全树 exit 0；三负例 exit 非 0 且原因匹配 — **PASS**

**命令**：`python tools/validate_plugins.py`（全树）；`python tools/validate_plugins.py --file tests/plugins/negative/<n>.json` ×3
**证据原文**：
```
$ python tools/validate_plugins.py
plugins validation: OK        (EXIT=0)

$ --file tests/plugins/negative/bad-container.json
FAIL: tests/plugins/negative/bad-container.json schema: 'fullscreen' is not one of ['windowed']   (EXIT=1)

$ --file tests/plugins/negative/bad-uninstallable.json
FAIL: tests/plugins/negative/bad-uninstallable.json directory rule: plugins/optional/ requires uninstallable==true, got False   (EXIT=1)

$ --file tests/plugins/negative/compat-bridge-without-translator.json
FAIL: ... schema: 'translator' is a required property
FAIL: ... compat-bridge translator must be under plugins/compat/ (spec §2.2), got None   (EXIT=1)
```
**判定**：validator `tools/validate_plugins.py` 存在且可执行；正例全树 exit 0；三负例均 exit 1 且失败原因与注入缺陷一一对应（container 枚举 / optional 目录规则 / compat-bridge 缺 translator）。**PASS**

## M2-03 ≥1 个 optional 示例插件通过 validator（含 uninstallable 目录规则）— **PASS**

**命令**：`python tools/validate_plugins.py --file plugins/optional/hello-plugin/plugin.json`
**证据原文**：
```
plugins validation: OK        (EXIT=0)
```
manifest 内容对照 schema：`plugins/optional/hello-plugin/plugin.json` 含 schema_version="1"、name="hello-plugin"、version="0.1.0"、type="native"、uninstallable=true、payload="payload/hello"（payload/hello 实体存在，validator 职责 4b 断言通过）、container.desktop="windowed"、capabilities/resources 数组——全部字段形态符合 schema v1；optional 目录 ⇒ uninstallable=true 目录规则由 bad-uninstallable 负例反向断言（见 M2-02）。**PASS**

## M2-04 配置生效：enabled 非法 id → validator 失败 — **PASS**

**命令**：写临时 config `/tmp/m2-inject.toml`（`[plugins] enabled = ["nonexistent-plugin"]`）→ `--config /tmp/m2-inject.toml`；再用默认 `config/default.toml` 复跑。
**证据原文**：
```
FAIL: C:\Users\JunYa\AppData\Local\Temp\m2-inject.toml [plugins] enabled id 'nonexistent-plugin' matches 0 manifests, must hit exactly one (职责 5)   (EXIT=1)

(还原默认 config 后)
plugins validation: OK        (EXIT=0)
```
**判定**：`config/default.toml [plugins] enabled=["hello-plugin"]` 驱动校验期启用一致性；注入不存在 id 即 FAIL exit 1，还原后 OK。口径：M2 为**校验期强制**（运行期装载属 M3），系台账 M2 计划 Ruling② 已放行口径，详见"口径差异"第 2 条。**PASS**

## M2-05 dev 插件通过 validator 且 uninstallable=false 规则被断言覆盖 — **PASS**

**命令**：`--file plugins/dev/etheros-agent-rules/plugin.json`；就地注入 `uninstallable:true` → 全树+单文件复跑 → 从备份还原复跑。
**证据原文**：
```
$ --file plugins/dev/etheros-agent-rules/plugin.json        (原样)
plugins validation: OK        (EXIT=0)      # manifest uninstallable=false

$ (注入 uninstallable:true 后)
FAIL: plugins/dev/etheros-agent-rules/plugin.json directory rule: plugins/dev/ requires uninstallable==false, got True   (EXIT_FILE=1)
FAIL: I:\etheros\plugins\dev\etheros-agent-rules\plugin.json directory rule: plugins/dev/ requires uninstallable==false, got True   (EXIT_TREE=1)

$ (还原后 git diff 无残留)
plugins validation: OK        (RESTORED_EXIT=0)
```
**判定**：`plugins/dev/` 有 1 个 dev 插件 manifest 通过 validator 且 uninstallable=false；dev 目录规则经就地注入实跑被断言覆盖（单文件与全树两种模式均拒绝），还原后工作区干净。**PASS**
（附注：builtin 目录当前无插件实体，builtin⇒false 规则仅有 validator 代码路径、无实体插件覆盖；M2-05 字面仅要求 dev 规则，不构成缺口，记为观察项。）

## M2-06 kernel/ 本里程碑零改动 — **PASS**

**命令**：`git diff v0.1.0-m1..HEAD -- kernel/ | wc -l` 及 `--stat`
**证据原文**：
```
0
KERNEL_DIFF_DONE
```
**判定**：diff 输出 0 行，kernel/ 相对 v0.1.0-m1 零改动。**PASS**

## M2-07 CI 新增插件校验 job 且通过（四 job 全绿）— **PASS**

**命令**：`gh run list -R Nolai2010/EtherOS --branch feat/m2-plugins --limit 2`；`gh run view 37399253779 -R Nolai2010/EtherOS`
**证据原文**：
```
completed  success  docs: minor fixes carried over from M2 final review (minor)  ci  feat/m2-plugins  push  37399253779  3m1s
completed  success  ci: add plugin-schema job (M2 manifest & config validation)   ci  feat/m2-plugins  push  37398129726  3m5s

run 37399253779 (HEAD ca57f90) JOBS:
✓ build ToaruOS base (upstream builder image) in 2m28s
✓ plugin manifest schema & config consistency (M2) in 5s
✓ etherkit single-source consistency in 6s
✓ vm smoke (QEMU headless boot evidence) in 28s
```
**判定**：最新 run（覆盖 HEAD ca57f90）四 job 全绿，其中 plugin-schema job 为 M2 新增且通过（annotations 仅为 runner 平台通告，非失败）。**PASS**

## M2-08 docs/index.md 与新增文档一致（M0-05 不回退）— **PASS**

**命令**：对 index 表 16 行逐条 `test -f`（以 docs/ 为基准的相对路径）；`find docs -type f` 全量清单反向比对。
**证据原文**：16/16 全部 `OK`（含 T8 新增引用：`../plugins/schema/README.md`、`../tools/validate_plugins.py`、reports/ 下 4 份）；docs/ 下 15 个文件（除 index.md 自身）全部被登记，无悬空、无遗漏。
**判定**：index 与实际文件一一对应，M0-05 不回退。**PASS**

---

## T8 并入核验（文档任务：0c350d1 + ca57f90）

**范围核验**（`git show <sha> --stat`）：
- 0c350d1：`docs/index.md`(+5)、`plugins/schema/README.md`(+54/-3) —— 仅计划内文档文件。
- ca57f90：`BUILD.md`(+8/-7)、`config/default.toml`(+4/-2)、`docs/development/acceptance-standard.md`(+20/-0)、`docs/tool-recognition-matrix.md`(+3/-3)。
- **零触碰清单核验**：kernel/、base/、Makefile、.etherkit/、spec/、.github/、tools/、tests/、plugins/schema/plugin.schema.json 在两笔提交中均无触碰。✓
- config/default.toml 变更逐行核对：全部为 `#` 注释行（头注释陈旧更新，系终审 MINOR 移交 T8 顺带项，台账在案），数据零变更。✓

**DCO**：两笔提交均含 `Signed-off-by: Nolai <120611751+Nolai2010@users.noreply.github.com>`。✓

**BUILD.md §4 与 CI 实际一致性**：对照 `.github/workflows/ci.yml` build job（L54-80）逐项核对——`submodules: recursive`、`docker pull toaruos/build-tools:1.99.x`、`docker run -v <workspace>/base/toaruos:/root/misaka -w /root/misaka -e LANG=C.UTF-8 ... util/build-in-docker.sh`、artifact 收集 `*.iso`/`misaka-kernel`/`*.igz`（etheros-boot-artifacts）、timeout 90min——BUILD.md §4 描述与 CI 实际一致，且如实记录裸 runner 路径废弃原因。✓

**acceptance-standard M1 归档纯追加**：`git show ca57f90 -- docs/development/acceptance-standard.md` 删除行（排除 diff 头 `---`）为空，stat +20/-0——M0/M2 章节未被改动，纯追加。✓

---

## 结论

**M2-01~M2-08 共 8 条：8 PASS / 0 FAIL。T8 并入核验 4 项：全部通过。**

**STATUS: PASS**

## 口径差异（单列，供终审裁量；均不构成 FAIL）

1. **container 两键口径**：spec §2.2 仅述 manifest 含 `container`（desktop:"windowed" / mobile:"fullscreen|split"），未明言两键是否齐备。实现取"对象必填、desktop/mobile **至少其一**"（minProperties:1），依据台账 Ruling（实现者 CONCERN② 裁定：跨形态适配语义允许插件只面向 desktop，强制两键属过度约束）；schema 内注释已标注该 Ruling。本验收按裁定口径核验，不判缺陷。
2. **"配置可改启动行为"降级口径**：spec §4 M2 行出口标准含"配置可改启动行为"；M2 实现为**校验期强制**（validator 保证 config [plugins] 与插件树一致），运行期按 enabled 装载归 M3。依据台账 M2 计划 Ruling②（spec §6 风险 4 + YAGNI 放行），config/default.toml 头注释亦如实声明该口径。
3. **--file 默认 optional 约定**：单文件模式目录类别按路径推断，推断不到按 optional 处理——台账已声明为 M2 负例循环自洽约定，非缺陷。
4. **stage="M2-plugins"**：config [system] stage 值与 M0-skeleton 同构，台账已裁定合理。
5. **builtin 目录规则无实体覆盖**（观察项，见 M2-05 附注）：builtin⇒uninstallable=false 仅有 validator 代码路径，M2 无 builtin 插件实体；M4 内建归位后自然获得实体覆盖。

> 本报告不打 tag（v0.2.0-m2 由控制器在 T10 处理）。无 FAIL 缺口。

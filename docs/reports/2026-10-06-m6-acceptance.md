# M6 独立验收报告 —— 发布通道（tag → 自动构建 → GitHub Release，三形态产物）

- **验收者**：general-purpose-1（独立上下文，与 M6 实现者 / Spec 审查者均不同；不替实现背书）
- **被验对象**：分支 `feat/m6-release`，HEAD `2747354`（提交主题 `feat: release channel (tag -> ISO/kernel/ramdisk; OVA deferred)`）
- **仓库**：`I:/etheros`（远端 `github.com/Nolai2010/EtherOS`）
- **执行日期**：2026-10-11（本机时区；文件名沿用 M6 计划日期 10-06，与 M0~M5 验收报告同系列）
- **依据**：`docs/development/acceptance-standard.md` M6 章节（M6-01~M6-06）+ 验收简报 `.superpowers/sdd/2026-10-05-etheros-m0m1-implementation/briefs/m6-t4-acceptance-brief.md`（含控制器已裁定的顺序调整与六条已声明 Minor）
- **口径**：偏严，全部实跑；只记录实测输出，不接受口头声明，不复用实现者/审查者结论作为判据（其声明的 Minor 逐条独立复现，见 §口径差异）
- **工作树**：验收前 `git status --short` 为空；验收过程中未落任何临时文件进仓库；本报告为本次唯一新增
- **未触碰任何仓库文件**：除本报告外零改动，因而不修任何问题——只记录，交由控制器裁定
- **`gh` 一律 `--repo Nolai2010/EtherOS`**（`gh` 不接受 `-C`）；Python `python3`；本机 Windows，构建类证据取 CI
- **补记（本次修订）**：原 M6-02 / M6-03 两条 PENDING 现已实跑完成，本文件就这两条补出终判并回填结论表（见 §M6-02 / §M6-03 / §结论）。补记为**追加修订**，不改写原轮已判定的 M6-01 / 04 / 05 / 06 四条结论，仅按"已有真实产物与 vm-smoke 绿证据"这一新事实重写原遗留 9。补记阶段同样零仓库文件改动（本报告仍为唯一改动对象）

---

## 0. 判据存在性核验与被验对象定位

```
$ git -C I:/etheros log --oneline -1
2747354 feat: release channel (tag -> ISO/kernel/ramdisk; OVA deferred)
$ git -C I:/etheros branch --show-current
feat/m6-release
$ git -C I:/etheros status --short
（空，0 字节）
```

HEAD 与简报所述 `2747354` 一致 ✅；分支正确；工作树干净。

判据实存（`sed -n '/## M6/,/^## M7/p' docs/development/acceptance-standard.md`）：M6-01 ~ M6-06 六条编号与验证方式齐备，无缺项。

```
$ git tag --points-at HEAD
（空）
$ git ls-remote --tags origin | tail -3
08e3feac36cff442be1345fe415b3264cec862b6	refs/tags/v0.4.0-m4^{}
28553bf1f7277f978ea573c3b3070fa779695944	refs/tags/v0.5.0-m5
03951673c1d76450e8750870caaffd975c423044	refs/tags/v0.5.0-m5^{}
$ git ls-remote origin refs/heads/main | head -2
03951673c1d76450e8750870caaffd975c423044	refs/heads/main
$ gh --repo Nolai2010/EtherOS release view v0.6.0-m6
release not found
```

未打 tag、未动 main（main 仍在 `0395167`）、`v0.6.0-m6` Release 尚未创建 ✅ —— 与"M6-02/03 尚未执行"的裁定一致。

判定：**PASS**（判据齐备、被验对象定位准确、无越界动作）

---

## M6-01 release.yml 双触发 + 与 ci.yml 同配方

### 结构取证（YAML 解析，非肉眼）

```
$ python3 -c "import yaml; d=yaml.safe_load(open('.github/workflows/release.yml')); print(d[True] if True in d else d.get('on')); ..."
top keys: ['name', True, 'permissions', 'jobs']
on: {'push': {'tags': ['v*']}, 'workflow_dispatch': {'inputs': {'dry_run': {'description': 'Build & upload artifacts only, skip GitHub Release creation', 'type': 'boolean', 'default': True}}}}
permissions: {'contents': 'write'}
jobs: ['build-release', 'publish-release']
  build-release   | if=None                          | needs=None          | timeout=90
  publish-release | if=github.event_name == 'push'   | needs=build-release | timeout=None
```

要素逐项：`on.push.tags == ['v*']` ✅；`workflow_dispatch` 带 `dry_run` boolean 输入（default true）✅ 双触发成立；`permissions.contents: write` ✅（Release 创建所需）；两 job ✅；`publish-release` 的 `if: github.event_name == 'push'` ✅（非 tag push 不发布）；`needs: build-release` ✅ 串行保序；幂等分支 `gh release view` → `upload --clobber` / 否则 `create` ✅（release.yml:63-70）。

### 配方同构：逐字节比对（本条核心，本人独立执行）

```
$ grep -n "docker pull" .github/workflows/ci.yml .github/workflows/release.yml
.github/workflows/ci.yml:190:          docker pull toaruos/build-tools:1.99.x
.github/workflows/release.yml:28:          docker pull toaruos/build-tools:1.99.x

$ grep -n "docker run" .github/workflows/ci.yml .github/workflows/release.yml
.github/workflows/ci.yml:191:          docker run -v ${{ github.workspace }}/base/toaruos:/root/misaka -w /root/misaka -e LANG=C.UTF-8 -t toaruos/build-tools:1.99.x util/build-in-docker.sh
.github/workflows/release.yml:29:          docker run -v ${{ github.workspace }}/base/toaruos:/root/misaka -w /root/misaka -e LANG=C.UTF-8 -t toaruos/build-tools:1.99.x util/build-in-docker.sh

$ grep -h "docker pull\|docker run" ci.yml > /tmp/a.txt ; grep -h "docker pull\|docker run" release.yml > /tmp/b.txt
$ diff /tmp/a.txt /tmp/b.txt
（无输出）
DIFF: EMPTY (identical)

$ md5sum /tmp/a.txt /tmp/b.txt
c910271a026670633a0d1909e962c4b1 */tmp/a.txt
c910271a026670633a0d1909e962c4b1 */tmp/b.txt
```

两行 `docker pull` / `docker run` 抽取后 **diff 空、md5 完全相同**（`c910271a026670633a0d1909e962c4b1`）。逐要素核对：镜像 `toaruos/build-tools:1.99.x` 同 ✅；挂载 `-v ${{ github.workspace }}/base/toaruos:/root/misaka` 同 ✅；工作目录 `-w /root/misaka` 同 ✅；`-e LANG=C.UTF-8` 同 ✅；`-t` 同 ✅；入口 `util/build-in-docker.sh` 同 ✅。

### 注释互指：仅单向成立（本人新发现，非已声明 Minor）

```
$ grep -n "ci.yml" .github/workflows/release.yml
2:# Build recipe MUST stay in sync with ci.yml:build (same builder image + util/build-in-docker.sh).
19:    name: build release artifacts (same recipe as ci.yml:build)
26:      - name: Build base OS (upstream builder image — keep in sync with ci.yml:build)

$ grep -n "release.yml\|release channel\|M6" .github/workflows/ci.yml
（零命中）
```

release.yml → ci.yml 方向 3 处指引 ✅；**ci.yml → release.yml 方向零命中** ❌。标准字面写的是"注释互指"，实为单向指引。

判定：**PASS-with-note** —— 双触发、`permissions`、两 job、`if`、`needs`、幂等分支六项结构要素齐备，配方两行经 md5 全等实证同构（非"看起来一样"）。note：注释互指仅单向成立，"互指"半句字面未达成；因验收者铁律禁止改动仓库文件（且零回退要求 ci.yml diff 必须为空），本轮**不修、只记档**，列为遗留 7 交控制器裁定。

---

## M6-02 干跑演练（workflow_dispatch dry_run=true）

> **补记终判（原为 PENDING）**：原 PENDING 的成因是环境约束（`gh workflow run` 要求 workflow 已存在于默认分支，在 `feat/m6-release` 上 dispatch 实测报 `HTTP 404: workflow release.yml not found on the default branch`）——非实现缺陷。现 `feat/m6-release` 已 `git merge --no-ff` 进 main（合并提交 `b3c2fdd`），干跑已实跑完毕，据实出具终判如下。

### 前提：merge 后 main 的基线

```
$ git -C I:/etheros branch --show-current
main
$ git -C I:/etheros log --oneline -1
b3c2fdd Merge feat/m6-release: M6 release channel + Phase 1 closeout
```

main CI run `38076005107`（event=push, headBranch=main, conclusion=success）八 job 结论：

```
dco (Signed-off-by on every commit, merges exempt) | success
build ToaruOS base (upstream builder image) | success
spec & docs reference consistency (anti context-drift) | success
lint (EtherOS-owned code only; base/ structurally excluded) | success
etherkit single-source consistency | success
license (reuse lint, submodules excluded per spec 5 / risk 2) | success
plugin manifest schema & config consistency (M2) | success
vm smoke (QEMU headless boot evidence) | success
```

基线干净（八 job 全 success，含 vm smoke）✅ —— 后续的干跑 / 真实发布都建立在这条 merge 后的 main 之上。

### 实跑取证

```
$ gh --repo Nolai2010/EtherOS run view 38076253475 --json status,conclusion,headBranch,event,displayTitle
{"conclusion":"success","displayTitle":"release","event":"workflow_dispatch","headBranch":"main","status":"completed"}

$ gh --repo Nolai2010/EtherOS run view 38076253475 --json jobs --jq '.jobs[]|"\(.name) | \(.conclusion)"'
build release artifacts (same recipe as ci.yml:build) | success
publish-release | skipped
```

触发方式 `workflow_dispatch` ✅、基准分支 `main` ✅、run 总结论 success ✅；两 job 结论与"干跑"预期**完全吻合**：`build release artifacts` **success**、`publish-release` **skipped** ✅❗

`build release artifacts`（job id `114283697628`）的 collect 步骤原始日志摘录：

```
Run mkdir -p artifacts
  mkdir -p artifacts
  find base/toaruos -maxdepth 2 -type f \( -name "*.iso" -o -name "misaka-kernel" -o -name "*.igz" \) -exec cp {} artifacts/ \; || true
  ls -la artifacts/
  test -f artifacts/image.iso
total 14308
-rw-r--r--  1 runner runner 7593984 Oct 10 18:35 image.iso
-rwxr-xr-x  1 runner runner  274384 Oct 10 18:35 misaka-kernel
-rw-r--r--  1 runner runner 6771662 Oct 10 18:35 ramdisk.igz
```

`test -f artifacts/image.iso` 硬断言在该步骤内且步骤 conclusion=success → **断言通过** ✅；三形态产物齐备（`image.iso` / `misaka-kernel` / `ramdisk.igz`）✅，其中 `image.iso` 与 `misaka-kernel` 由上游配方（`util/build-in-docker.sh`，与 ci.yml 同配方，见 M6-01 md5 全等）产出。

```
$ gh api repos/Nolai2010/EtherOS/actions/runs/38076253475/artifacts --jq '.artifacts[]|"\(.name) | \(.size_in_bytes) bytes"'
etheros-release-artifacts | 13671702 bytes
```

artifact 名 `etheros-release-artifacts`、大小 **13671702 bytes** ✅（与 upload 步骤日志 `Final size is 13671702 bytes. Artifact ID is 11678845622`、`With the provided path, there will be 3 files uploaded` 互证 —— 三件齐备，非"看起来齐"）。

### 关键负向断言：干跑未创建任何 Release

```
$ gh --repo Nolai2010/EtherOS release list --limit 20
EtherOS v0.6.0-m6	Pre-release	v0.6.0-m6	2026-10-10T18:40:02Z
```

全仓库 Release 列表**仅 1 条**，即 `v0.6.0-m6`，`publishedAt` = `2026-10-10T18:40:02Z`。干跑 run `38076253475` 完成于 `2026-10-10T18:35:56Z`，早于该 Release 五分钟；且该 Release 另有其主（见 M6-03，run `38076522422` 的 publish job 创建）。→ **干跑未创建任何 Release** ✅❗ 这正是"干跑"的语义核心：`publish-release` 被 `if: github.event_name == 'push'` 挡下，只构建不发布。

判定：**PASS** —— 干跑 gate 的三项（① build job success ② publish job skipped ③ 三形态产物齐备且 artifact 上传成功）+ 一项负向断言（Release 列表未新增）全部由 `gh` 实跑输出坐实，无一项依赖推理或他人声明。原 PENDING 所依赖的环境约束已解除，且解除后行为与预测一致。

## M6-03 真实发布（v0.6.0-m6 tag push）

> **补记终判（原为 PENDING）**：同上，依赖 merge 进 main。原轮已确认"尚未执行"三处证据齐备（`git tag --points-at HEAD` 空、`ls-remote --tags` 最新为 `v0.5.0-m5`、`gh release view` → `release not found`，无偷偷预建嫌疑）。现 tag 已推送、release.yml 已实跑，据实出具终判如下。

### tag 与 commit 的对应关系（先确认不是"挂错对象"）

```
$ git ls-remote --tags origin | grep -i m6
b3da4b57a6070291614e781afe1a96ab1333be0c	refs/tags/v0.6.0-m6
b3c2fddd6ef01c46d70c7db03c9390fbf74f643a	refs/tags/v0.6.0-m6^{}

$ git -C I:/etheros rev-parse v0.6.0-m6
b3da4b57a6070291614e781afe1a96ab1333be0c
```

tag 为**附注 tag**（有 `^{}` 剥离行），对象 `b3da4b5` 剥离后 → **b3c2fdd**，即 main 上的合并提交 `b3c2fdd` ✅。本地 `rev-parse` 与远端一致 → 无本地/远端分叉。Release 侧：

```
$ gh --repo Nolai2010/EtherOS release view v0.6.0-m6 --json tagName,targetCommitish,createdAt,publishedAt
{"createdAt":"2026-10-10T18:37:20Z","publishedAt":"2026-10-10T18:40:02Z","tagName":"v0.6.0-m6","targetCommitish":"main"}
```

tagName 与 tag 名逐字一致 ✅；targetCommitish = `main` ✅（Release 锚定默认分支，非游离对象）。**Release 与 tag 对应无误**。

### 实跑取证

```
$ gh --repo Nolai2010/EtherOS run view 38076522422 --json status,conclusion,headBranch,event,displayTitle
{"conclusion":"success","displayTitle":"Merge feat/m6-release: M6 release channel + Phase 1 closeout","event":"push","headBranch":"v0.6.0-m6","status":"completed"}

$ gh --repo Nolai2010/EtherOS run view 38076522422 --json jobs --jq '.jobs[]|"\(.name) | \(.conclusion)"'
build release artifacts (same recipe as ci.yml:build) | success
publish-release | success
```

event=push、headBranch=`v0.6.0-m6` → 确系 **tag push** 触发（与干跑的 `workflow_dispatch` 形成对照）✅；两 job **均 success**，`publish-release` 本次不再 skipped ✅❗ —— 这正是 M6-02 与 M6-03 的分水岭：同一份 workflow，只因 `github.event_name` 从 `workflow_dispatch` 变为 `push`，发布闸门由闭转开。

`publish-release`（job id `114285023495`）步骤逐条：

```
Set up job                                                                    | success
Run actions/checkout@v4                                                       | success
Download release artifacts                                                    | success
Create GitHub Release (-mN tags marked prerelease; v1.0.0 later per user decision) | success
```

`Download release artifacts` → `Create GitHub Release` 的顺序证实：发布的资产**来自本次 build job 产物**（download 自 `etheros-release-artifacts`），而非另起炉灶 ✅。

### 门槛逐项核验

```
$ gh --repo Nolai2010/EtherOS release view v0.6.0-m6 --json tagName,name,isPrerelease,isDraft,assets
{
  "assets": [
    {"name":"image.iso",     "size":7593984, "state":"uploaded", "contentType":"application/vnd.efi.iso"},
    {"name":"misaka-kernel", "size":274384,  "state":"uploaded", "contentType":"application/octet-stream"},
    {"name":"ramdisk.igz",   "size":6772626, "state":"uploaded", "contentType":"application/octet-stream"}
  ],
  "isDraft":false, "isPrerelease":true, "name":"EtherOS v0.6.0-m6", "tagName":"v0.6.0-m6"
}
```

| 门槛 | 实测 | 结论 |
|---|---|---|
| 资产 ≥3 件 | 3 件（`image.iso` / `misaka-kernel` / `ramdisk.igz`） | ✅ |
| 资产类型覆盖 ISO + kernel + ramdisk | 三者齐备，`image.iso` 的 contentType 为 `application/vnd.efi.iso` | ✅ |
| `isPrerelease == true` | `true` | ✅ |
| 非草稿（`isDraft` 不冒充） | `false` | ✅ |
| Release 与 tag 对应 | tagName `v0.6.0-m6` == tag 名，targetCommitish `main` | ✅ |

`isPrerelease: true` 与 M6-04 落档的"`-mN` 一律 prerelease"策略一致 ✅（release.yml:67 `--prerelease` 生效的实证，非仅 YAML 静态检查）。发布说明取自 `RELEASE_NOTES.md`（release.yml:69 `--notes-file RELEASE_NOTES.md`），本轮未对 notes 内容做逐字回读，此项沿用 M6-04 的文档侧实证。

### 发现：ramdisk 产物跨 run 非字节可复现（本人新发现，非已声明 Minor）

对比干跑（run `38076253475`，artifact `13671702`）与真实发布（Release assets）的同名产物：

| 产物 | 干跑（18:35） | 真实发布（18:40） | 差值 |
|---|---|---|---|
| `image.iso` | 7593984 | 7593984 | 0 ✅ |
| `misaka-kernel` | 274384 | 274384 | 0 ✅ |
| `ramdisk.igz` | 6771662 | 6772626 | **+964** ❗ |

`image.iso` 与 `misaka-kernel` 两次构建**字节数完全一致**；`ramdisk.igz` 相差 **964 字节**。两次构建间隔约 5 分钟、同一 commit（`b3c2fdd`）、同一配方（`util/build-in-docker.sh`，镜像 `toaruos/build-tools:1.99.x`）→ 差值只能来自配方内部的**非确定性输入**（ramdisk 打包嵌入了时间戳 / 文件 mtime 之类的易变元数据，属上游 initrd 打包的固有行为，非 release.yml 的缺陷）。

后果评估：产物**可用**（M6-06 的可启动性链路不受影响 —— ISO 与 kernel 两次全等，且 vm-smoke 在同配方产物上实绿），但"同一 tag 重跑会产出不同字节的 ramdisk"，意味着 Release 资产**不可按字节复现校验**（外部用户无法用一个公布的和校验码去验手里的 `ramdisk.igz`）。不阻塞 M6 关门，挂 Phase 2 待办。

判定：**PASS-with-note** —— 门槛四项（≥3 资产 / 类型覆盖 / prerelease / Release-tag 对应）全部由 `gh release view` 实跑输出坐实，且 publish job 的 download→create 顺序证实资产来源为本次构建产物。note 即上述 `ramdisk.igz` 跨 run 964 字节漂移（不可字节复现），与"未对已发布资产做独立启动验证"（见 §M6-06 与遗留 9）—— 两条均为如实记录，不判 FAIL（不阻塞 M6-03 的发布通道 gate），亦不粉饰为"已完整验证"。

---

## M6-04 语义化版本策略落档（v0.x.0-mN 惯例 / -mN 一律 prerelease / v1.0.0 留用户决策）

### RELEASE_NOTES.md 三段实读 + grep

① 段（版本内容，第 3-23 行）✅；② 段 **版本策略(语义化版本惯例)**（第 25-31 行）✅；③ 段 **产物形态与降级记档**（第 33-41 行）✅。三段齐备。

```
$ grep -n "v0.x.0-mN\|prerelease\|v1.0.0" RELEASE_NOTES.md
27:- 本仓库延续 **`v0.x.0-mN`** 版本惯例:次版本号 `x` 对应里程碑序号,`-mN` 为该里程碑的收官标记
29:- **`-mN` 后缀在 semver 中即预发布形态**,因此凡 `-mN` 标签创建的 GitHub Release **一律标记 prerelease**
30:  (`--prerelease`),不冒充正式版。
31:- **`v1.0.0` 不在本版本切换**:是否切 `v1.0.0` 留待 Phase 1 收官后由用户决策,本版本不做预判、不提前占用。
```

三条逐项：`v0.x.0-mN` 惯例明写 ✅；`-mN` 一律 `--prerelease` 明写且给出 semver 理由 ✅；`v1.0.0` 写的是"**不在本版本切换**""**留待 Phase 1 收官后由用户决策**""**不做预判、不提前占用**"——措辞为"留决策"而非既成事实 ✅（与控制器三条口径一致：不切 v1.0.0）。

### release.yml 侧落地

```
$ grep -n "prerelease\|--notes-file\|--title" .github/workflows/release.yml
58:      - name: Create GitHub Release (-mN tags marked prerelease; v1.0.0 later per user decision)
67:              --prerelease \
68:              --title "EtherOS $TAG" \
69:              --notes-file RELEASE_NOTES.md
```

`gh release create` 带 `--prerelease` ✅，发布说明以 `--notes-file RELEASE_NOTES.md` 消费（与 M6-03"RELEASE_NOTES.md 为发布说明"要求对齐）✅。

判定：**PASS** —— 文档三段与 workflow 实现双向对齐，`v1.0.0` 措辞经逐字核对确为"留用户决策"。

---

## M6-05 OVA 降级记档（差异点 8 / Phase 2，不冒充已支持）

```
$ grep -n -i "OVA\|vmdk\|ovf\|Phase 2\|差异点 8" RELEASE_NOTES.md
39:**OVA 尚未支持(降级至 Phase 2,差异点 8)**:本次发布 **不提供 OVA / VMDK / OVF 虚拟机镜像**,
40:不做 vmdk/ovf 打包(YAGNI)。如需虚拟机镜像,请直接使用 `image.iso` 自行安装或转换。
41:此项在验收标准 `docs/development/acceptance-standard.md` M6-05 条与验收报告中均如实记档,**不以任何形式声称 OVA 已支持**。
```

逐项核对：白纸黑字"**OVA 尚未支持**" ✅；明确标注"降级至 Phase 2,差异点 8"（与 spec 差异点编号对齐）✅；"不做 vmdk/ovf 打包" ✅；显式声明"**不以任何形式声称 OVA 已支持**" ✅；给出替代路径（用 `image.iso` 自装/自转）✅。

反向检查（是否别处有冒充）：`release.yml` 的 collect 步骤仅收集 `*.iso` / `misaka-kernel` / `*.igz` 三类（release.yml:34），**无 vmdk/ovf 产物** ✅；且步骤名自带"（ISO + kernel + ramdisk; OVA deferred to Phase 2, 差异点 8）"（release.yml:31），workflow 侧同样如实 ✅。

判定：**PASS** —— 文档与 workflow 双侧均以否定式措辞明写"尚未支持"，无任何位置暗示 OVA 已交付。

---

## M6-06 Release 含可启动产物（image.iso 与 vm-smoke 消费产物同源同配方）

### 链路一：配方同构（承接 M6-01 实证）

`ci.yml:190-191` 与 `release.yml:28-29` 的 `docker pull` / `docker run` 两行 md5 全等（`c910271a026670633a0d1909e962c4b1`，见 M6-01）→ 两处构建产出的 `image.iso` **同配方** ✅。收集逻辑亦同构（两处均为 `find base/toaruos -maxdepth 2 -type f \( -name "*.iso" -o -name "misaka-kernel" -o -name "*.igz" \)`）。

### 链路二：ci.yml 内 build → vm-smoke 消费闭环

```
ci.yml:199-204   Upload boot artifacts   → name: etheros-boot-artifacts
ci.yml:220-224   Download boot artifacts → name: etheros-boot-artifacts   （vm-smoke job, needs: build）
ci.yml:232       ISO=$(find artifacts -name "*.iso" | head -1)
ci.yml:284       if grep -aq "login:" serial-com2.log   → 断言内核+用户态均已跑起
```

artifact 名两端一致（`etheros-boot-artifacts`）✅；vm-smoke 以 `needs: build` 串行消费 build 产物 ✅；断言目标即 build 产出的 ISO ✅。

### 链路三：vm-smoke 绿证据（本次 HEAD 上的实跑）

```
$ gh --repo Nolai2010/EtherOS run list --branch feat/m6-release --limit 5
completed	success	feat: release channel (tag -> ISO/kernel/ramdisk; OVA deferred)	ci	feat/m6-release	push	38073922725	2m50s	2026-10-10T17:58:51Z

$ gh --repo Nolai2010/EtherOS run view 38073922725 --json jobs --jq '.jobs[]|"\(.name) | \(.conclusion)"'
etherkit single-source consistency | success
license (reuse lint, submodules excluded per spec 5 / risk 2) | success
build ToaruOS base (upstream builder image) | success
lint (EtherOS-owned code only; base/ structurally excluded) | success
dco (Signed-off-by on every commit, merges exempt) | success
plugin manifest schema & config consistency (M2) | success
spec & docs reference consistency (anti context-drift) | success
vm smoke (QEMU headless boot evidence) | success
```

run `38073922725` 的触发提交即被验 HEAD `2747354`（run 标题与提交主题逐字一致），八 job 全 success，其中 **vm smoke 绿** ✅ —— 即在**本条被验的同一 commit** 上，同配方产出的 ISO 经 QEMU headless 实启动并捕获到 `login:`。

### RELEASE_NOTES 侧的自述一致性

```
RELEASE_NOTES.md:21  | `image.iso` | 可启动光盘镜像(BIOS + EFI 双引导);与 ci.yml `vm-smoke` job 消费的 ISO 同源同配方 |
RELEASE_NOTES.md:36-37  可启动性由 ci.yml `vm-smoke` job 背书:该 job 以 QEMU headless 启动同一配方产出的 ISO,
                        捕获 serial 上的 `login:` 作为内核与用户态均已真正跑起来的证据。
```

文档自述与实证一致，无夸大 ✅。

判定：**PASS-with-note** —— 三条链路齐备：配方 md5 全等 + artifact 名闭环 + 本 HEAD 上 vm-smoke 实绿。note（口径声明，不掩饰）：**"可启动性链路背书"系签收自 ci.yml vm-smoke 的既有绿证据**，而非本轮对 release.yml 产物单独做的启动验证——原轮撰写时 release.yml 的 `etheros-release-artifacts` 尚未产出（待 merge 后 M6-02/03），故其可启动性只能由"配方全等"这一同构关系传递背书，属推理链的第二环，白纸黑字记明。

> **补记对该 note 的更新（不修改上段结论，仅修正其失效前提）**：上段"产物尚未产出"的前提**现已失效** —— M6-02 / M6-03 实跑后，release.yml 产物已真实产出并上传（干跑 artifact `13671702` bytes；Release `v0.6.0-m6` 三件资产）。但 note 的**实质结论依然成立**：vm smoke 启动的是 ci.yml build job 自产的 `etheros-boot-artifacts`，**不是** Release 里那一份 `image.iso`；二者同配方、同 commit、字节数全等（7593984），却非同一 artifact 对象，CI 中不存在"下载 Release 资产再启动"的步骤。故本条**仍为传递背书、仍非独立启动验证**，只是传递起点已由静态配方比对升级为同 commit 上的另一次实跑绿证据。完整重写见 §口径差异与遗留 9。

---

## 附：零回退与生成物纪律（简报指定顺带项）

### 零回退：M6 未动 ci.yml

```
$ git diff v0.5.0-m5..HEAD -- .github/workflows/ci.yml | wc -c
0
```

diff 字节数 **0** → M6 对 ci.yml 零改动 ✅（与 M6-01 复用同配方、M5 八 job 零回退一致）。

### 全量改动清单（确认无夹带）

```
$ git diff v0.5.0-m5..HEAD --stat
 .github/workflows/release.yml           | 70 +++++++++++++++++++++++++++++++++
 RELEASE_NOTES.md                        | 45 +++++++++++++++++++++
 docs/development/acceptance-standard.md | 11 ++++++
 docs/index.md                           |  1 +
 4 files changed, 127 insertions(+)
```

四个文件全部为 M6 直接产物：`release.yml`（发布通道本体）、`RELEASE_NOTES.md`（发布说明）、`acceptance-standard.md`（+11 为 M6 判据章节本身，控制器提交 `bc953c5`）、`docs/index.md`（+1 为 RELEASE_NOTES 登记行）。**纯插入、零删除、无夹带** ✅

### 生成物纪律

```
$ bash .etherkit/generate.sh
[EtherOS] 项目同步: .etherkit/ -> 各工具原生配置
  + AGENTS.md / CLAUDE.md / GEMINI.md ... （共 71 个文件/目录）
[EtherOS] 完成: 共生成 71 个文件/目录

$ git status --short | wc -c
0
```

重跑生成脚本后 `git status --short` 为 **0 字节** → 生成物零漂移 ✅（71 个生成物全部与 `.etherkit/` 源同步且已提交）。

### spec-consistency 本地复跑（index 新登记不悬空）

```
$ git diff v0.5.0-m5..HEAD -- docs/index.md
+| `../RELEASE_NOTES.md` | 发布说明（M6）：v0.6.0-m6 Phase 1 收官内容、v0.x.0-mN 版本惯例与 v1.0.0 留用户决策、三形态产物与 OVA 降级 Phase 2 记档；release.yml 以 `--notes-file` 消费 |

$ （复跑 ci.yml:142-174 内联脚本的 (a) 段）
  [命中] ../RELEASE_NOTES.md -> exists: True
RELEASE_NOTES 登记悬空? False
FAILS: none
spec-consistency (a): OK
```

新增的 `../RELEASE_NOTES.md` 登记走仓库根基准可解析，**不悬空** ✅（与 CI run 38073922725 的 spec-consistency job success 互证）。

### 禁用口号守卫

本报告涉及该守卫处均带"禁用"字样（守卫规则本身豁免此类警示性提及）；`RELEASE_NOTES.md` 页脚为「融汇万端(Connect the Unconnectable.)」，未触碰守卫拦截项，CI slogan guard job（etherkit-consistency）绿 ✅。

---

## 结论

| 编号 | 判定 | 终判依据（run id / 命令） |
|---|---|---|
| M6-01 release.yml 双触发 + 与 ci.yml 同配方 | **PASS-with-note** | YAML 解析 + 配方两行 md5 全等 `c910271a…`（原轮判定，未改写） |
| M6-02 干跑演练（dry_run=true） | **PASS**（原 PENDING，本次补记） | run `38076253475`：build **success** / publish **skipped**；artifact `13671702` bytes；`release list` 未新增 |
| M6-03 真实发布（v0.6.0-m6） | **PASS-with-note**（原 PENDING，本次补记） | run `38076522422`：build **success** / publish **success**；`release view`：3 assets、`isPrerelease=true`、tagName 对应 |
| M6-04 语义化版本策略落档 | **PASS** | RELEASE_NOTES 三段 + `release.yml:67` `--prerelease`（原轮判定，未改写） |
| M6-05 OVA 降级记档（差异点 8 / Phase 2） | **PASS** | 文档与 collect 步骤双重否定式措辞（原轮判定，未改写） |
| M6-06 Release 含可启动产物（同源同配方链路） | **PASS-with-note** | 配方 md5 全等 + artifact 名闭环 + vm smoke 绿（原轮判定，未改写；背书性质见遗留 9 已重写） |
| 零回退（ci.yml diff 空）+ 生成物纪律 + spec-consistency | **PASS**（附项） | `git diff … ci.yml \| wc -c` = 0（原轮判定，未改写） |

**总计：M6-01 ~ M6-06 六条全部 PASS，其中 3 条 PASS-with-note（M6-01 / 03 / 06）；PENDING 归零。阻塞缺陷数 0。**

补记承诺已履行：原 PENDING 的 M6-02 / M6-03 两条现已基于 `gh run view` / `gh release view` / `gh release list` 实跑输出出具终判并回填本表；遗留 9 已按"已有真实产物与 vm-smoke 绿证据"这一新事实重写。

---

## 口径差异与遗留

1. **顺序调整（控制器已裁定，原轮据此执行）—— 现已闭环**：`gh workflow run` 要求 workflow 已存在于默认分支，实测在 `feat/m6-release` 上 dispatch 报 `HTTP 404: workflow release.yml not found on the default branch`；当时默认分支 `main` 为 `0395167`（不含 release.yml）。故 M6-02 / M6-03 只能待 merge 后执行，原轮写 **PENDING**——既不因"没跑过"判 FAIL（那是环境约束非实现缺陷），也不判 PASS（无 run 证据）。顺序：原轮验收 → merge → 干跑 → 打 tag 真实发布 → 补记终判。
   **闭环状态（补记）**：上述四步已按序执行完毕 —— merge 合并提交 `b3c2fdd`（main CI run `38076005107` 八 job 全绿）→ 干跑 run `38076253475`（build success / publish skipped）→ tag `v0.6.0-m6`（附注 tag，剥离后即 `b3c2fdd`）→ 真实发布 run `38076522422`（两 job 均 success）→ 本文件补记终判。**原 404 约束已解除且解除后行为与预测一致**，本条不再构成遗留，保留原文仅为存证。

2. **已声明 Minor ① `dry_run` 是死输入** —— 本人独立复现属实：
   ```
   $ grep -n "dry_run\|inputs\." .github/workflows/release.yml
   9:      dry_run:
   45:    # dry_run（workflow_dispatch 默认）或干跑演练时不创建 Release；只有真实 tag push 触发发布。
   ```
   全文唯一引用是 `:45` 的注释，无 `inputs.dry_run`；`publish-release` 的 `if` 只看 `github.event_name`。行为安全（偏保守，`dry_run=false` 也不建 Release），但输入名与语义脱节。规格层面合规（简报逐字指定），记档不判 FAIL。

3. **已声明 Minor ② 幂等分支只 `--clobber`、不刷新 notes/title** —— 独立复现属实（release.yml:63-64）：Release 已存在时仅重传资产，若 `RELEASE_NOTES.md` 事后修改，重跑不更新发布说明。Phase 1 可接受，建议挂残余风险账。

4. **已声明 Minor ③ `publish-release` 缺 `timeout-minutes`** —— 独立复现属实：YAML 解析显示 `build-release` timeout=90，`publish-release` timeout=None（走 6h 默认上限）。`gh` 挂起时有风险，不阻塞。

5. **已声明 Minor ④ `--prerelease` 无条件** —— 独立复现属实（release.yml:67）：将来真打 `v1.0.0` 也会被标 prerelease。按简报/控制器口径属有意为之，但需在 v1.0.0 决策时同步改，Phase 2 待办挂账。

6. **已声明 Minor ⑤ 口号页脚空格差异** —— 独立复现属实：
   ```
   RELEASE_NOTES.md:45    融汇万端(Connect the Unconnectable.)        ← 无空格
   .etherkit/AGENTS.md:9  主口号：**融汇万端 (Connect the Unconnectable.)**  ← 有空格
   ```
   纯观感漂移，不触发任何门禁（slogan guard 只拦禁用口号裸用），可忽略。

7. **已声明 Minor ⑥ RELEASE_NOTES.md 未写发布日期** —— 独立复现属实（`grep -nE "20[0-9]{2}-[0-9]{2}-[0-9]{2}" RELEASE_NOTES.md` 零命中）。赞成不编日期，非缺陷。

8. **【本人新发现，非已声明】注释互指仅单向**：见 M6-01。release.yml 有 3 处指向 ci.yml，ci.yml 对 release.yml **零命中**。标准字面"注释互指"的反向半句未达成。因验收者铁律禁止改动仓库文件（且零回退要求 ci.yml diff 必须为空、本轮实证为 0 字节），**不修只记档**。建议关门任务在 ci.yml build job 注释区补一行反向指引（例如"配方与 .github/workflows/release.yml:build-release 同构，改此须同步"），补后重跑零回退与 CI 即可闭合。

9. **M6-06 的背书性质声明（已按新事实重写，不掩饰也不夸大到"已独立启动验证"）**：原轮写的是 release.yml 产物"尚未产出、可启动性系推理链第二环"。补记后事实变化如下，**逐条据实重写**：
   - **已成立的部分**：release.yml 产物现已真实产出（干跑 artifact `13671702` bytes，run `38076253475`），且真实发布已上传三件资产（run `38076522422` / Release `v0.6.0-m6`）。"产物是否存在"这一环已从推理变为事实 ✅。同配方关系亦已从静态 md5 比对升级为**两次实跑均成功产出三形态产物**的实证 ✅。
   - **仍未成立的部分（不粉饰）**：**已上传的那三件资产本身，未经独立启动验证**。证据链是：vm smoke job 在 run `38076005107`（main，同 commit `b3c2fdd`）上实绿，它启动的是 **ci.yml build job 自己产出的** ISO（`etheros-boot-artifacts`），不是 Release 里那一份 `image.iso`。二者**同配方、同 commit、且实测字节数全等（7593984）**，但**不是同一个 artifact 对象**，CI 流程中不存在"下载 Release 资产再启动"这一步。
   - **因此准确定性**：M6-06 的"可启动"结论仍是**同源同配方传递背书**，只是传递的起点从"静态配方比对"变成了"同 commit 上同配方的另一次实跑绿证据"。它**比原轮更强**（不再是纯静态推理），但**依然不是**"release 产物已独立启动验证"——后者需要对 `gh release download v0.6.0-m6` 下来的那一份 `image.iso` 单独跑一次 QEMU，本轮未做，故不宣称。
   - **闭合建议（Phase 2 待办）**：取 Release 资产实跑一次 QEMU（`gh release download v0.6.0-m6 -p image.iso` 后走 ci.yml:220-284 的 vm-smoke 同款脚本），即可将本条由"传递背书"闭合为"直接证据"。叠加遗留 10 与 §M6-03 的 ramdisk 漂移后，一次闭合动作可同时坐实资产可用性与不可复现性两项。

10. **本报告未登记进 `docs/index.md`**（补记后待办项更新）：验收者铁律限制改动仓库文件（唯一例外即本报告本身）。沿用 M5 报告先例，由关门任务（控制器代笔 plumbing）补登一行。**原建议文本写的是"（4 PASS / 2 PENDING…）"，补记后应改为**：
   ```
   | docs/reports/2026-10-06-m6-acceptance.md | M6 独立验收报告（6 PASS，其中 M6-01/03/06 为 PASS-with-note；含 OVA 降级 Phase 2 记档、v1.0.0 留决策记档，以及 ramdisk 跨 run 非字节可复现记档） |
   ```
   经本机校验：该引用在 spec-consistency 双基准检查下按 docs/ 相对基准可解析，登记后不会造成悬空 FAIL。

11. **验收过程零副作用声明（原轮 + 补记）**：
   - **原轮**（HEAD `2747354`，分支 `feat/m6-release`）：写操作仅 `bash .etherkit/generate.sh`（实测零漂移，`git status --short` 为 0 字节）；临时比对文件落在 `/tmp`，未落进仓库；未推 tag、未动 main（`main` 仍 `0395167`）、未 dispatch 任何 workflow、未创建任何 Release。
   - **补记轮**（HEAD `b3c2fdd`，分支 `main`）：**仅执行只读取证**（`gh run view` / `gh release view` / `gh release list` / `gh api …/artifacts` / `git log` / `git ls-remote`），**零写操作**；未推 tag、未创建 Release、未 dispatch 任何 workflow。补记期间发生的 merge（控制器执行）、tag 推送（控制器执行）、Release 创建（release.yml 自动执行）**均非本验收者所为**，本人对这些动作的取证是事后只读核验。
   - 两轮合计：本验收者对仓库的改动**始终只有本报告一个文件**。

---

**STATUS: PASS（补记后：M6-01 ~ M6-06 六条全部 PASS，其中 M6-01 / 03 / 06 为 PASS-with-note；PENDING 归零，阻塞缺陷数 0）**

# M0 独立验收报告(对抗式验收)

- 日期:2026-10-06
- 仓库:I:/etheros,分支 feat/m0-m1(HEAD 5893948,工作树干净)
- 验收者:独立 acceptance-checker(与实现者不同上下文,全部判定基于本机实跑,不接受报告转述)
- 验收标准:docs/development/acceptance-standard.md M0 章节(外部合格线,未改写)

## 逐条核验

| 编号 | 实跑命令(摘要) | 证据关键行 | 判定 |
|---|---|---|---|
| M0-01 | for 循环 test -d 19 个目录 | spec、docs(+development/experience-library)、kernel、arch/{x86_64,aarch64,riscv64}、plugins/{schema,compat,builtin,optional,dev}、config、packages、sdk、themes、.etherkit、.github/workflows 全部 `OK`,0 个 MISS | 通过 |
| M0-02 | `bash .etherkit/generate.sh`(前后记录 `git status --short`) | EXIT=0;「共生成 71 个文件/目录」;抽查 AGENTS.md、CLAUDE.md、GEMINI.md、.cursor/rules/01~04.mdc、.clinerules/(4)、.trae/rules/(4)、.github/copilot-instructions.md 全部存在;.codex/agents/ 恰 5 个 toml(builder/reviewer/test-author/visual-reviewer/acceptance-checker) | 通过 |
| M0-03 | generate.sh 连跑第二次,`git status --short` | `IDEMPOTENT: git status empty`,EXIT=0 | 通过 |
| M0-04 | `gh run list -R Nolai2010/EtherOS --branch feat/m0-m1 --limit 3` + `gh run view 37337647254` | 最近一次 run `completed success`,job「etherkit single-source consistency」✓ | 通过(附注:本地 HEAD 5893948 领先远端 origin/feat/m0-m1=e990775 共 2 个提交未推送,CI 覆盖至 e990775;本地实跑 generate.sh 两次均零 diff,已复现一致性) |
| M0-05 | 按索引逐条 test -f + 反向 ls | 正向:`experience-library/active-rules.md` **MISS**(索引注明"待首条",但标准要求无悬空);反向:`docs/tool-recognition-matrix.md` 已被 git 追踪却**未入索引**(遗漏) | 未达 |
| M0-06 | `diff spec/2026-10-05-etheros-dev-policy.md D:/Agents/Workfile/docs/superpowers/specs/2026-10-05-etheros-dev-policy.md` | 输出 `IDENTICAL`(逐字节一致) | 通过 |
| M0-07 | 读 CORE_MANIFEST.toml 对照 spec §2.2 | capabilities=[schedule, protocol-route, load-isolate] 对应 §2.2 ①调度②协议/能力解释并路由③加载/隔离;forbidden_in_kernel=[fs-format, app-format, device-protocol, ui, driver] 覆盖 §2.2「不含任何文件系统格式、应用格式、设备协议逻辑」且"驱动也是插件"一致 | 通过 |
| M0-08 | cat .gitignore | 构建产物(build/ dist/ *.o *.a)、镜像产物(*.iso *.img *.vhd *.vhdx *.ova *.qcow2)、reports/ 三类条目齐备 | 通过 |
| M0-09 | grep README + CI 同款 grep 管道 | README.md:3 `融汇万端 (Connect the Unconnectable.)`;CI 同款管道(含 --exclude-dir 与豁免词)结果 `RAW_HITS=NONE`;spec 内 2 处提及均在 CI 豁免目录且为警示/架构表述 | 通过 |
| M0-10 | `git log --format="%h %(trailers:key=Signed-off-by)" main..HEAD` + `git ls-remote origin HEAD` | main..HEAD 共 7 个提交,Signed-off-by 逐条非空(Nolai <120611751+Nolai2010@users.noreply.github.com>);ls-remote 返回 HEAD 引用,REMOTE_OK | 通过 |
| M0-11 | ls + cat REUSE.toml | LICENSES/MIT.txt、REUSE.toml 均存在;REUSE.toml 含两个 [[annotations]],path=["**"]→SPDX MIT,path=["LICENSE","NOTICE","LICENSES/**"]→CC0-1.0 | 通过 |
| M0-12 | 下载 ezwinports GNU Make 4.4.1(SHA256=fb66a02b…与 winget 清单一致)后于仓库根 `make` | EXIT=0;「skeleton check: OK」;末行经字节还原为「[EtherOS] M0 空构建:结构校验通过,无编译目标(M1 接入 ToaruOS 底座)」= Makefile 第 9 行。终端乱码系 ezwinports make.exe 在 Windows 按 ANSI 中转 recipe 输出的环境局限(ASCII 行正常、仅中文受影响),Makefile 源字节为正确 UTF-8,非仓库缺陷 | 通过 |
| M0-13 | `git ls-files .etherkit \| cut -d/ -f2 \| sort \| uniq -c` + 文件大小抽查 | skills=1, agents-md=2, rules=4, prompts=1, frameworks=1,五类各 ≥1;抽查 9 个文件 841–1940 字节全部非空且被 git 追踪。观察:另有 subagents/=5(标准未列举的第六类,不影响判定,记档) | 通过 |

## 结论

**M0:12/13 通过,1 项未达(M0-05)。M0 暂不可关闭,待 M0-05 修复后复核该单项即可。**

## 缺口清单

1. **M0-05-悬空**:docs/index.md 第 14 行列出 `experience-library/active-rules.md`,该文件不存在(即便注明"待首条",也不满足"无悬空")。
2. **M0-05-遗漏**:`docs/tool-recognition-matrix.md`(commit 5893948 引入)未登记进 docs/index.md。

## 验收者附注

- 本报告由独立验收者出具;修复属控制者职责,验收者未改动 M0-05 相关文件。
- M0-12 的 make 验证环境:本机原无 make,验收者下载 ezwinports make 4.4.1 至系统临时目录(SHA256 校验通过),未向仓库引入任何文件。
- M0-04 附注:若要求 CI 覆盖最新提交,控制者推送 5893948 后 CI 会自动补验(其内容即本次本地已复现的 generate.sh 零 diff)。

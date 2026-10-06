# BUILD.md — 构建说明

> 状态:M1(Task 10)。事实依据:`docs/reports/2026-10-06-toaruos-survey.md`(T8 调研)、底座 `base/toaruos` @ `e77143fd14391d880c3ee11c1524252cdcbfd225`。

## 1. 结论

**本地 Windows 不可构建。** T8 调研结论:底座构建依赖交叉编译工具链(`x86_64-pc-toaru-gcc`,需在 Linux 上由 gcc/binutils-gdb 子模块自举)以及 xorriso、genext2fs、mtools、gnu-efi 等 Linux 工具,均无原生 Windows 路径;官方构建路径是 Docker(`toaruos/build-tools:1.99.x`)或 Linux(来源:T8 报告 §3、§风险 1)。

**构建路径 = CI(Linux runner)**,由 T13 落地;`make build` 即 CI build job 的调用入口(先 `check` 再转发 `$(MAKE) -C base/toaruos`)。

## 2. 依赖清单(Linux 环境)

照 T8 报告 §3(来源:上游 `util/docker/Dockerfile` apt 列表 + `build/x86_64.mk`):

- `build-essential`
- `python3`
- `xorriso`(ISO9660 打包)
- `genext2fs`、`mtools`、`dosfstools`(EFI FAT 镜像)
- `gnu-efi`(EFI 引导)
- `git`
- `automake`、`autoconf`、`wget`
- `libgmp-dev`、`libmpfr-dev`、`libmpc-dev`(交叉 GCC 自举)
- `flex`、`bison`、`texinfo`

**无 nasm 依赖**(T8:全仓 Makefile/Dockerfile grep `nasm` 无命中;汇编由交叉 as/GCC 处理)。

交叉工具链(`x86_64-pc-toaru-gcc`/binutils)由底座自带脚本 `util/build-toolchain.sh` 从 `util/gcc`、`util/binutils-gdb` 子模块构建,无需预装;官方 Docker 镜像 `toaruos/build-tools:1.99.x` 已预置。

## 3. 本机尝试记录(2026-10-06,Windows 11 Git Bash)

命令:`make build`。**预期失败,输出原文如下,未做任何修饰:**

```
bash tools/check-skeleton.sh
skeleton check: OK
C:/Users/JunYa/AppData/Local/Microsoft/WinGet/Links/make.exe -C base/toaruos
make[1]: Entering directory 'I:/etheros/base/toaruos'
mkdir -p base/dev
process_begin: CreateProcess(NULL, mkdir -p base/dev, ...) failed.
make (e=2): 系统找不到指定的文件。
make[1]: *** No rule to make target 'base/bin/about-dialog', needed by 'ramdisk.tar'.  Stop.
make[1]: Leaving directory 'I:/etheros/base/toaruos'
make: *** [Makefile:9: build] Error 2
```

失败原因与 T8 结论一致:底座 Makefile 依赖 Unix 工具(`mkdir -p` 等)与 Linux 工具链,Windows 的 WinGet make(Win32 进程模型)无法执行。**请勿在本机试图绕过。**

## 4. CI 构建说明(预期,T13 落地)

CI build job 流程预期:

1. checkout 时启用 `submodules: recursive`(底座含 gcc/binutils-gdb 等大子模块,注意体积与超时);
2. Linux runner 上直接执行 `make build`(入口即本仓 Makefile 的 `build` 目标:先 `check` 再转发底座);
3. 构建成功后,将底座产出的 iso 作为 workflow artifact 上传。

细节(触发条件、缓存、超时、工具链自举时长)由 T13 落地。

## 5. 构建产物路径预期

底座在 `base/toaruos` 内产出(T8 报告 §3):

- `image.iso`(ISO9660 可启动镜像,BIOS+EFI 双引导)——artifact 目标;
- 中间产物:`misaka-kernel`(内核)、`ramdisk.igz`(压缩 ramdisk)。

以上为 T8 调研读上游 Makefile/CI 所得的预期;实际路径以 CI 首次成功构建的输出为准,**T13 落地后回填本节**。

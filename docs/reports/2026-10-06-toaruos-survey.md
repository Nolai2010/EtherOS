# ToaruOS 底座调研报告(2026-10-06)

> 任务:Task 8(M1 前置)。需求源:task-8-brief.md。调研对象为只读克隆,未做任何修改。
> 克隆命令:`git clone --depth 50 https://github.com/klange/toaruos /tmp/toaruos-survey`(与官方站点指向一致,未发生 404/改名,未启用备选检索)。

## 结论

**满足 M1 底座条件,锁定 SHA `e77143fd14391d880c3ee11c1524252cdcbfd225`(master,2026-10-05)。**

| 条件 | 结论 | 依据 |
|---|---|---|
| 可构建 x86_64 | 满足 | CI workflow `.github/workflows/x86_64.yml` 产出 `image.iso`;构建依赖全部为一方代码+标准 Linux 工具链 |
| 可构建 aarch64 | 满足 | `build/aarch64.mk`、`kernel/arch/aarch64/`(含 RPi400 支持)、CI `aarch64.yml` 均在 |
| 自带 GUI | 满足 | Yutani 合成器 `apps/yutani.c`("The ToaruOS Window Compositor",见文件头)+ 装饰器/面板/登录会话(`apps/live-session.c`、`panel.c`、`glogin.c`),GUI 栈全为一方代码 |
| 许可与 MIT 共存 | 满足 | 一方代码为 UIUC/NCSA 开源许可(BSD 类宽松许可);子模块 bim(ISC 类)、kuroko(MIT)均兼容;可再许可/捆绑于 MIT 项目,须保留版权与许可全文 |

## 逐项事实

### 1. 默认分支 / HEAD / 最近提交

- 默认分支:`master`(`git branch --show-current` 输出)
- HEAD SHA:**`e77143fd14391d880c3ee11c1524252cdcbfd225`**
- 最近提交日期:`Mon Oct 5 22:49:02 2026 +0900`

核验输出:

```
$ git -C /tmp/toaruos-survey rev-parse HEAD && git -C /tmp/toaruos-survey log -1 --format=%cd
e77143fd14391d880c3ee11c1524252cdcbfd225
Mon Oct 5 22:49:02 2026 +0900
```

### 2. 许可(逐字引用,非凭记忆)

根 `LICENSE`(仓库内唯一顶层许可文件,34 行)**全文归属:UIUC/NCSA(University of Illinois/NCSA Open Source License)**。前 5 行逐字摘录:

```

University of Illinois/NCSA Open Source License

Copyright (c) 2011-2026 K Lange, et al. (hereafter [fullname]). All rights reserved.

Developed by: ToaruOS (hereafter [project])
```

`README.md` §License 确认:"All first-party parts of ToaruOS are made available under the terms of the University of Illinois / NCSA License, which is a BSD-style permissive license",且明确允许 "redistribute code under the NCSA license, as well as make modifications to the code and sublicense it under other terms (such as the GPL, or a proprietary license)",条件是保留版权声明与许可全文。

第三方目录与许可文件分布(子模块未随主仓检出,以下许可文件读自各自上游浅克隆,SHA 与主仓锁定一致):

| 组件 | 位置 | 许可文件 | 前 5 行摘录 | 归属 |
|---|---|---|---|---|
| 主仓(内核/libc/lib/apps/boot 全部一方代码) | / | `LICENSE` | 见上 | UIUC/NCSA |
| bim(编辑器) | 子模块 `bim`,锁定 `8ece591f` | 上游 `LICENSE` | `Copyright (C) 2012-2021 K. Lange` / `Permission to use, copy, modify, and/or distribute this software for any` / `purpose with or without fee is hereby granted, provided that the above` / `copyright notice and this permission notice appear in all copies.` | ISC 类 |
| kuroko(解释器) | 子模块 `kuroko`,锁定 `50e45b4a` | 上游 `LICENSE` | `Copyright (c) 2020-2024 K. Lange <klange@toaruos.org>` / `Copyright (c) 2015 Robert Nystrom` / `Permission is hereby granted, free of charge, to any person obtaining a copy` / `of this software and associated documentation files (the "Software"), to` | MIT(含 Nystrom 部分版权) |
| 工具链源 | 子模块 `util/binutils-gdb`(LGPL/GPL)、`util/gcc`(GPL) | 各自上游 COPYING | 仅构建期使用,产物(工具链二进制)不随镜像分发到运行时边界 | 构建工具,非捆绑组件 |
| DejaVu 字体 | `base/usr/share/fonts/truetype/dejavu/`(8 个 .ttf) | 仓库内**无**独立许可文件 | — | 三方字体,DejaVu 许可(BITSTREAM_VERA 类),需在 M1 许可清单中补 NOTICE |

注:`find -iname '*license*' -o -iname '*copying*'` 在主仓内(排除 .git)仅命中根 `LICENSE` 一个文件——主仓没有第三方源码目录;三方组件全部经由 git 子模块与字体资源引入。

### 3. 构建系统与依赖清单

构建入口:根 `Makefile`(经 `util/activate.sh` + `build/${ARCH}.mk`),官方推荐 Docker/CI 构建(`README.md` §Building、`util/build-in-docker.sh`)。

**x86_64 完整依赖清单**(来源:`util/docker/Dockerfile` 第 4 行 apt 列表 + `build/x86_64.mk`):

- 编译器:交叉 GCC/binutils,目标三元组 `x86_64-pc-toaru`(由 `util/build-toolchain.sh` 自 gcc/binutils-gdb 子模块构建,需 `libgmp-dev libmpfr-dev libmpc-dev flex bison texinfo`);Docker 镜像 `toaruos/build-tools:1.99.x` 已预置
- **无 nasm 依赖**(全仓 Makefile/Dockerfile grep 'nasm' 无命中;汇编用交叉 as/GCC 处理,BIOS 引导用 `-m32` GCC)
- 汇编器/链接器:交叉 binutils(as/ld,`-melf_i386` 用于 BIOS/MBR 部分)
- 语言运行时:Python3(镜像内)、Kuroko(子模块,构建 `auto-dep.krk`/`createramdisk.krk` 等构建期工具)
- 打包工具:`xorriso`(ISO9660)、`genext2fs`、`mtools`、`dosfstools`(EFI FAT 镜像)
- 其他:`gnu-efi`(EFI 引导,链接 `-lefi -lgnuefi`)、`git`、`automake autoconf wget`
- Docker 内构建脚本:`util/build-in-docker.sh`(内部执行 `make base/lib/libc.so && make -j4`)

**产物**:`image.iso`(ISO9660 可启动镜像,含 BIOS+EFI 双引导)以及中间产物 `misaka-kernel`(内核)+ `ramdisk.igz`(压缩 ramdisk 归档)。另有 `make test` 可直接以 `-kernel/-initrd` 方式启动。

### 4. aarch64 支持证据

- `build/aarch64.mk` 存在,目标三元组 `aarch64-unknown-toaru`,产物含 `misaka-kernel ramdisk.igz bootstub kernel8.img`(RPi400 树莓派直接启动镜像)
- `kernel/arch/aarch64/` 目录完整:entry.S/gic.c/pl011.c/mmu.c/virtio.c/smp.c 等,另有 `rpi400/` 子目录与 `rpi_miniuart.c`
- CI:`.github/workflows/aarch64.yml` 存在
- `README.md`:"complete, independent operating system for x86-64 PCs and ARMv8 VM environments"、"In early 2022, the OS was further ported to aarch64."

### 5. GUI 栈

- **Yutani 窗口合成器**:`apps/yutani.c`,文件头自述 "Yutani - The ToaruOS Window Compositor ... canvas-based window compositor and manager"(共享内存 canvas + 包式 socket 协议)
- 会话入口:`apps/live-session.c`(Live CD 图形会话,`yutani_init()` 启动)、`apps/login.c`/`glogin.c`(登录)、`apps/panel.c`(任务栏)
- 配套:`lib/` 一方 GUI 库(toaru 图形/控件/装饰器)、`base/usr/share/ttk` 素材、`base/usr/share/fonts/truetype/dejavu` 字体
- 结论:"自带 GUI" 属实,GUI 显示栈全为一方代码,无 X11/Wayland 依赖

### 6. 仓库规模

- 文件数(不含 .git):**1160**;`du -sh` 总体积:**15M**(含 .git;工作树本体约 4.5M)
- 主要目录:kernel 1.1M / apps 1.9M / libc 676K / lib 672K
- 子模块(另计):kuroko、bim、util/binutils-gdb、util/gcc(后两者仅构建期,体积大但非运行时内容)

### 7. 活跃度(最近 5 条 commit)

```
e77143f 2026-10-05 ls: add -H, -L, -P
643bcd8 2026-10-05 ls: show classifiers in long mode
1d5a8d2 2026-10-05 tar: don't print warning when we expectedly hit end of archive
ad7ba54 2026-10-05 procfs: put exe collection behind its own flag
bbae8c8 2026-10-05 kuroko: sync upstream
```

深度 50 的浅克隆内 50 条提交全部落在 2026-10-05 前后,项目处于活跃维护状态(始于 2011 年,持续 15 年)。

## spec 影响

1. **许可预写确认,无需修正**:spec §6 风险 2 与 §2.1 预写"上游 UIUC/NCSA 类许可"与实测一致(根 LICENSE 即 UIUC/NCSA 全文)。spec 中 "上游 UIUC/NCSA 存于 LICENSES/ + NOTICE + 文件级 SPDX" 方案可直接执行,无需修订。
2. **补充事实**(spec 未提及,建议 M1 许可清算时纳入):除上游主许可外,还有 (a) kuroko 子模块为 MIT 且含第二版权人(Robert Nystrom);(b) bim 子模块为 ISC 类;(c) DejaVu 字体在仓库内无许可文件,需按 DejaVu 许可补 NOTICE;(d) `util/gcc`、`util/binutils-gdb` 为 GPL 构建 子模块,建议 M1 明确"仅构建期使用、不随镜像分发"的边界声明,避免 GPL 清算误伤。
3. **架构覆盖与 spec §2 一致**:x86-64 + aarch64 均有 Makefile 目标与 CI,无需改动 spec 架构决策。
4. **无与 spec §2/§6 冲突的其他发现**;Misaka 为混合模块化内核一事 spec §6 风险 1 已预写,事实相符。

## 风险与未知

1. **本机 Windows 构建可行性:Git Bash 直接构建不可行**。依赖交叉编译器(x86_64-pc-toaru-gcc 需在 Windows 上自行构建,含 GMP/MPFR/MPC)、xorriso、genext2fs、mtools、gnu-efi 等,均无原生 Windows 路径;官方构建路径是 Docker(`toaruos/build-tools:1.99.x`)或 Linux。**建议 M1 用 Linux/CI 环境(Docker 或 GitHub Actions,上游 workflow 可直接复用)做 `make` 验证**,本机只做代码级工作。
2. **子模块未随主仓克隆检出**:`git submodule update --init` 需网络可达 kuroko-lang、toaruos/bim 及 gcc/binutils-gdb(后两者体积大);M1 拉基线时须记录子模块 SHA(bim `8ece591f`、kuroko `50e45b4a`、binutils-gdb `facad00e`、gcc `66860610`)。
3. **DejaVu 字体许可文件缺失**是许可清单的已知缺口,需 M1 主动补 NOTICE(风险 2 中已列)。
4. **未实跑构建**:本次为只读调研,未执行 `make`(简报未要求);M1 底座基线任务须以 CI/Linux 环境实跑构建作为验收。
5. `/tmp/toaruos-survey` 按简报要求保留,供 Task 9 复用校验。

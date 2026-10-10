#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""EtherOS M4 内核边界守卫(纯工具层,Global Constraint 11 同款纪律:不导入/链接任何 kernel/
与 base/toaruos 代码,只做结构与 git 层检查)。spec §3.2 + 计划约束 18/19/21。
职责:
1. vendored 指针一致: `git ls-tree HEAD base/toaruos`(mode 160000)的 SHA == CORE_MANIFEST
   [vendored_base].pinned——不依赖 submodule 初始化(CI checkout 非 recursive 亦可跑);
   若 submodule 已初始化,额外断言 `git -C base/toaruos rev-parse HEAD` 一致且
   `git diff --submodule=log base/toaruos` 为空(本地漂移);未初始化则打印 SKIP,不作失败。
2. kernel/ 白名单: 工作树扫描(含未跟踪文件,严于 git ls-files,可被 touch 注入反例命中);
   允许集合 = kernel/README.md + kernel/interfaces/*(内核零实现代码的结构保证)。
3. 格式字面量零命中: kernel/ 递归扫 `\\.(ipa|exe|apk)\\b` 与 `douyin`(M3 先例口径)。
4. manifest↔契约对齐: [kernel].capabilities == {schedule, protocol-route, load-isolate}
   且 forbidden_in_kernel 非空(M0-07 不回退的机器可查形态)。
CLI: --manifest <path> 覆盖 CORE_MANIFEST 路径(负测用)。任何失败逐条 `FAIL: <项> <原因>` + exit 1;全过 `kernel boundary: OK` + exit 0(风格对齐 tools/validate_plugins.py)。"""
import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VENDORED = "base/toaruos"
KERNEL = REPO / "kernel"
ALLOWED_KERNEL = ("kernel/README.md",)  # kernel/interfaces/* 整目录放行(计划 Task M4-4 职责 2)
REQUIRED_CAPS = {"schedule", "protocol-route", "load-isolate"}  # kernel/interfaces 三原语契约
FORMAT_RE, FORMAT_TOKEN = re.compile(r"\.(ipa|exe|apk)\b"), "douyin"  # 约束 15 + M3 先例口径
FAILURES: list[str] = []


def fail(item, reason):
    FAILURES.append(f"FAIL: {item} {reason}")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def check_vendored(manifest):
    """职责 1: vendored 指针一致(约束 18);pinned 读自 manifest(可 --manifest 覆盖供负测)。"""
    pinned = manifest.get("vendored_base", {}).get("pinned")
    if not isinstance(pinned, str) or not pinned:
        fail("vendored pointer", "[vendored_base].pinned missing in manifest")
        return
    tree = git("ls-tree", "HEAD", VENDORED)
    if tree.returncode:
        fail("vendored pointer", f"git ls-tree HEAD {VENDORED} failed: {tree.stderr.strip()}")
        return
    entries = [ln.split() for ln in tree.stdout.splitlines() if ln.strip()]
    pointer = next((e[2] for e in entries if e[0] == "160000"), None)
    if pointer is None:
        fail("vendored pointer", f"{VENDORED} is not a gitlink (mode 160000) at HEAD — submodule removed or renamed")
    elif pointer != pinned:
        fail("vendored pointer", f"gitlink SHA {pointer} != CORE_MANIFEST pinned {pinned}")
    if (REPO / VENDORED / ".git").exists():  # submodule 已初始化 → 本地漂移检查(约束 18)
        if git("-C", VENDORED, "rev-parse", "HEAD").stdout.strip() != pinned:
            fail("vendored pointer", f"initialized submodule HEAD drifted from pinned {pinned}")
        if git("diff", "--submodule=log", VENDORED).stdout.strip():
            fail("vendored pointer", "git diff --submodule=log not empty (local drift)")
    else:
        print("SKIP: submodule not initialized — local drift checks skipped (CI checkout non-recursive is OK)")


def check_kernel_whitelist():
    """职责 2: kernel/ 文件白名单(工作树扫描,含未跟踪文件;严于 git ls-files)。"""
    for f in sorted(p for p in KERNEL.rglob("*") if p.is_file()):
        rel = f.relative_to(REPO).as_posix()
        if rel in ALLOWED_KERNEL or rel.startswith("kernel/interfaces/"):
            continue
        fail("kernel whitelist", f"unexpected file under kernel/: {rel} (kernel must stay README + interfaces/* only)")


def check_format_literals():
    """职责 3: kernel/ 格式字面量零命中(约束 15;自实现扫描,不依赖外部 grep)。"""
    for f in sorted(p for p in KERNEL.rglob("*") if p.is_file()):
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            fail("format literal", f"{f.relative_to(REPO).as_posix()} unreadable: {exc}")
            continue
        for m in FORMAT_RE.finditer(text):
            fail("format literal", f"{f.relative_to(REPO).as_posix()} contains app-format literal '{m.group(0)}' (Constraint 15)")
        if FORMAT_TOKEN in text:
            fail("format literal", f"{f.relative_to(REPO).as_posix()} contains format token '{FORMAT_TOKEN}' (M3 precedent)")


def check_manifest_alignment(manifest):
    """职责 4: manifest↔契约对齐(M0-07 不回退;capabilities 与 kernel/interfaces 三原语一致)。"""
    caps = manifest.get("kernel", {}).get("capabilities")
    if not isinstance(caps, list) or set(caps) != REQUIRED_CAPS:
        fail("capabilities", f"must equal {sorted(REQUIRED_CAPS)} (kernel/interfaces three primitives, M0-07), got {caps!r}")
    forbidden = manifest.get("kernel", {}).get("forbidden_in_kernel")
    if not isinstance(forbidden, list) or not forbidden:
        fail("forbidden_in_kernel", "must be a non-empty list (M0-07 no-regression)")


def main():
    ap = argparse.ArgumentParser(description="EtherOS kernel boundary guard (M4: vendored pin + kernel whitelist + format literals + manifest alignment)")
    ap.add_argument("--manifest", default=str(REPO / "CORE_MANIFEST.toml"), help="override CORE_MANIFEST path (negative testing)")
    args = ap.parse_args()
    try:
        with open(args.manifest, "rb") as fh:
            manifest = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        fail("manifest", f"{args.manifest} unreadable/invalid TOML: {exc}")
        manifest = {}
    check_vendored(manifest)
    check_kernel_whitelist()
    check_format_literals()
    check_manifest_alignment(manifest)
    if FAILURES:
        print("\n".join(FAILURES))
        return 1
    print("kernel boundary: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

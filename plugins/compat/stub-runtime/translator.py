#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""EtherOS M3 兼容翻译运行时雏形(STUB, Global Constraint 16)。

STUB 边界(诚实声明,不伪装成功翻译):本工具只输出结构化「翻译计划」JSON,
不解析 exe/ipa/apk 等任何真实格式内容,不执行任何 payload,不做指令集/
系统调用/GUI 翻译。真翻译属 Phase 2 逐格式立项(spec §6 风险 4"目标形态
不是首版承诺")。纯用户态 stdlib only,不导入/链接任何 kernel/ 代码
(约束 11;spec §6 风险 1:任何格式兼容都通过用户态兼容层实现)。

CLI: translator.py --manifest <plugin.json 路径> [--payload <路径>]
  --payload 缺省时取 manifest 的 payload 字段(相对 manifest 所在目录解析)。
  exit 0 = 输出翻译计划;exit 2 = 非翻译对象/输入不可用(不输出计划)。
"""
import argparse
import json
import sys
from pathlib import Path


def refuse(reason):
    # 拒绝即明说:不出计划、exit 2,绝不伪装成功(约束 16)
    print(f"translator: {reason}", file=sys.stderr)
    return 2


def main():
    ap = argparse.ArgumentParser(description="EtherOS compat stub translator (plan-only, M3)")
    ap.add_argument("--manifest", required=True, help="plugin manifest JSON path")
    ap.add_argument("--payload", help="payload path override (default: manifest payload field)")
    args = ap.parse_args()

    mpath = Path(args.manifest)
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return refuse(f"manifest unreadable: {exc}")
    if not isinstance(manifest, dict):
        return refuse("manifest is not a JSON object")
    if manifest.get("type") != "compat-bridge":
        return refuse(f"plugin {manifest.get('name')!r} is type {manifest.get('type')!r}, not compat-bridge — nothing to translate")

    payload = args.payload or manifest.get("payload", "")
    if not payload:
        return refuse("no payload path given (--payload) and manifest has no payload field")
    ppath = (mpath.parent / payload).resolve()
    if not ppath.is_file():
        return refuse(f"payload '{payload}' does not resolve to an existing file")

    # 翻译计划:steps 仅为 Phase 2 真翻译的阶段示意,本 stub 不执行其中任何一步
    plan = {
        "plugin": manifest.get("name"),
        "source_format": (manifest.get("protocols") or [None])[0],
        "target_format": "etheros-native",
        "protocols": manifest.get("protocols", []),
        "payload": payload,
        "translator": "stub-runtime",
        "status": "stub-plan-only",
        "steps": ["unpack", "translate-syscalls", "launch"],
        "note": "STUB: translation plan only — real format parsing/execution NOT implemented in M3 (Global Constraint 16, spec §6 risk 4)",
    }
    json.dump(plan, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

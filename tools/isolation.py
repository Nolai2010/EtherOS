#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""EtherOS M12 隔离配置生成器(纯工具层,约束 11:不导入/链接任何 kernel/ 与 base/toaruos 代码)。
kernel/interfaces/isolation-contract.md 的宿主侧参考实现:消费 tools/load_state.py 的装载状态
(M11,status "loaded",约束 60),按 load_order 序为每个已装载条目建立隔离域——权限位图由 manifest
已声明 capabilities 经契约 §3 映射表逐 token 推导(perms ⊆ declared,约束 57;未列名 token =
未分类 = 零位,默认拒绝并记录于 unclassified_capabilities,约束 56),执行边界按 manifest type
分两级(契约 §4:compat-bridge → reference-only,外部 payload 永不执行;native → process-confined,
净化环境仅透传 PATH/HOME/LANG + cwd 锁定 payload 所在目录),输出 status "profile" 的隔离配置
(契约 §6;不用 "isolated" 式表述)。诚实边界(约束 58):今天真强制(enforced)= 两级执行边界;
权限位图仅声明(declared_only),FS/NET 级强制与生产级安全模型属 spec §6 风险 8 / Phase 2 后期。
格式无关(约束 61):只见 id/type/capability token/权限位/执行边界分级,不检视 payload 内容。
CLI: --load-state <file>(必需,load_state.py 的产物)、--out <file>(可选,落盘;缺省只打 stdout)。
负例(逐条 FAIL + stderr + 非 0 退出 + 不输出配置):输入不可读/非 JSON 对象 / status 非 "loaded" /
缺 registry 或缺 load_order / registry 条目缺 type 或缺 capabilities(非数组)/ load_order 与
registry 条目 id 集不一致 / 权限位追溯不到已声明 token(内部不一致即拒,约束 57)。"""
import argparse
import json
import sys
from pathlib import Path

CONTRACT = "kernel/interfaces/isolation-contract.md"
STAGE = "M12-isolation"
LEVEL = "PER_PLUGIN"  # 每插件一隔离域(契约 §0;loader_if.h ETHEROS_ISOLATION_PER_PLUGIN)
COMPAT_BRIDGE = "compat-bridge"  # manifest type token → reference-only(契约 §4)
FAILURES: list[str] = []

# 权限位封闭集合(契约 §2,与 router_if.h ETHEROS_PERM_* 掩码宏逐字对齐;NET/GUI 预留暂无映射)
PERM_BITS = {
    "ETHEROS_PERM_NONE": 0x00,
    "ETHEROS_PERM_FS_READ": 0x01,
    "ETHEROS_PERM_FS_WRITE": 0x02,
    "ETHEROS_PERM_PROC": 0x04,
    "ETHEROS_PERM_NET": 0x08,
    "ETHEROS_PERM_SYSINFO": 0x10,
    "ETHEROS_PERM_COMPAT": 0x20,
    "ETHEROS_PERM_GUI": 0x40,
}

# capability token → 权限位映射表(契约 §3,逐 token 明列;未列名 = 未分类 = 零位,约束 56)
TOKEN_TO_PERM = {
    "fs.browse": "ETHEROS_PERM_FS_READ",
    "sys.settings": "ETHEROS_PERM_FS_WRITE",
    "sys.shell": "ETHEROS_PERM_PROC",
    "sys.perfmon": "ETHEROS_PERM_SYSINFO",
    "compat.ipa.bridge": "ETHEROS_PERM_COMPAT",
}

# 执行边界分级(契约 §4):manifest type token → (execution, enforced 清单);其余 type 即 native
BOUNDARIES = {
    COMPAT_BRIDGE: ("reference-only", ["no-execution-of-foreign-payload"]),
}
DEFAULT_BOUNDARY = ("process-confined", ["env-sanitized", "cwd-locked"])

NOTES = [
    "profile = 隔离配置文件,非“已隔离强制”;status 不用 “isolated” 式表述(契约 §0,约束 58)。",
    "今天真强制(enforced)= 两级执行边界(契约 §4):compat-bridge 外部 payload 永不执行;native 经 sh 子进程以净化环境(仅透传 PATH/HOME/LANG)+ 锁定 cwd(payload 所在目录)执行。",
    "权限位图仅声明(declared_only):FS/NET 等位记录在配置中但不强制,今天无 per-bit 强制点;生产级安全模型属 spec §6 风险 8 / Phase 2 后期(约束 58)。",
    "perms ⊆ declared(约束 57):每位必须可追溯到该条目 manifest 已声明的 capability token;未列名 token = 未分类 = 零位(默认拒绝,约束 56),原样记录于 unclassified_capabilities,不静默丢弃。",
    "单一事实源链(约束 60):本工具只消费 tools/load_state.py 的装载状态(status “loaded”),不重读 config、不自行扫树决定启用集;domains 序 == load_order。",
    "格式无关(约束 61):只见 id/type/capability token/权限位/执行边界分级,不检视 payload 内容;NET/GUI 位预留(暂无 token 映射,契约 §2)。",
]


def fail(where, reason):
    FAILURES.append(f"FAIL: {where} {reason}")


def check_mapping_table():
    """内部自检:映射表每个值必须是词汇表内的非 NONE 位且位值唯一(契约 §2/§3 漂移即拒)。"""
    seen = {}
    for token, name in sorted(TOKEN_TO_PERM.items()):
        if name not in PERM_BITS or name == "ETHEROS_PERM_NONE":
            fail(token, f"maps to unknown permission bit '{name}' (contract §2/§3 drift; isolate: EINVAL)"); return False
        if PERM_BITS[name] in seen:
            fail(token, f"maps to bit '{name}' already mapped from '{seen[PERM_BITS[name]]}' (contract §3 drift; isolate: EINVAL)"); return False
        seen[PERM_BITS[name]] = token
    return True


def load_state(state_path):
    """读装载状态并做契约级校验(不可读/非 JSON 对象 / status 非 "loaded" / registry·load_order
    形态 / 条目缺 type 或缺 capabilities(非数组)/ load_order 与 registry 条目 id 集不一致)。
    返回按 load_order 序排列的 registry 条目列表;校验失败记 FAIL 返回 None。"""
    try:
        state = json.loads(Path(state_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(state_path, f"unreadable/invalid JSON: {exc} (isolate: EINVAL)"); return None
    if not isinstance(state, dict):
        fail(state_path, "input is not a JSON object (isolate: EINVAL)"); return None
    if state.get("status") != "loaded":
        fail(state_path, f"status {state.get('status')!r} is not 'loaded' — only a loaded state can be isolated (isolate: EINVAL)"); return None
    registry = state.get("registry")
    order = state.get("load_order")
    if not isinstance(registry, list):
        fail(state_path, "'registry' must be an array (isolate: EINVAL)"); return None
    if not isinstance(order, list) or not all(isinstance(p, str) for p in order):
        fail(state_path, "'load_order' must be an array of plugin ids (isolate: EINVAL)"); return None
    by_id = {}
    for item in registry:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            fail(state_path, "every 'registry' entry must be an object with a string 'id' (isolate: EINVAL)"); return None
        pid = item["id"]
        if pid in by_id:
            fail(pid, "duplicate registry entry id (isolate: EINVAL)"); return None
        if not isinstance(item.get("type"), str):
            fail(pid, "registry entry missing string 'type' (isolate: EINVAL)"); return None
        caps = item.get("capabilities")
        if not isinstance(caps, list) or not all(isinstance(t, str) for t in caps):
            fail(pid, "registry entry missing 'capabilities' array of tokens (isolate: EINVAL)"); return None
        by_id[pid] = item
    if len(order) != len(by_id) or sorted(order) != sorted(by_id):
        fail(state_path, f"load_order {order} is inconsistent with the registry entry id set "
                         f"{sorted(by_id)} (isolate: EINVAL)"); return None
    return [by_id[pid] for pid in order]


def derive_domain(entry):
    """为一个已装载条目推导隔离域(契约 §3/§4):perms_mask = 已分类 token 对应位之或;断言式校验
    (约束 57):mask 中每位必须可追溯到某个已声明 token,否则内部不一致即拒;未分类 token 原样进
    unclassified_capabilities(零位,约束 56);execution/enforced 按 type 分级(契约 §4);
    declared_only = perms 全部位名(今天无 per-bit 强制点,位图仅声明,约束 58)。返回 domain
    dict(键序逐字对齐契约);失败记 FAIL 返回 None。"""
    pid, caps, ptype = entry["id"], entry["capabilities"], entry["type"]
    perms_mask = 0
    for token in caps:
        name = TOKEN_TO_PERM.get(token)
        if name is not None:
            perms_mask |= PERM_BITS[name]
    for bit in (b for b in PERM_BITS.values() if b and perms_mask & b):
        if not any(PERM_BITS[TOKEN_TO_PERM[t]] == bit for t in caps if t in TOKEN_TO_PERM):
            fail(pid, f"internal inconsistency: permission bit {bit:#04x} not traceable to any "
                      f"declared capability token (isolate: EINVAL)"); return None
    perms = [name for name, bit in sorted(PERM_BITS.items(), key=lambda kv: kv[1]) if bit and perms_mask & bit]
    execution, enforced = BOUNDARIES.get(ptype, DEFAULT_BOUNDARY)
    return {
        "id": pid,
        "level": LEVEL,
        "perms_mask": perms_mask,
        "perms": perms,
        "execution": execution,
        "capabilities": caps,
        "unclassified_capabilities": [t for t in caps if t not in TOKEN_TO_PERM],
        "enforced": enforced,
        "declared_only": list(perms),
    }


def main():
    ap = argparse.ArgumentParser(description="EtherOS isolation profile generator (M12, host-side reference of kernel/interfaces/isolation-contract.md)")
    ap.add_argument("--load-state", required=True, help="load state JSON produced by tools/load_state.py (status 'loaded')")
    ap.add_argument("--out", help="write the isolation profile to this file (default: stdout only)")
    args = ap.parse_args()
    if not check_mapping_table():
        print("\n".join(FAILURES), file=sys.stderr); return 1
    entries = load_state(args.load_state)
    if entries is None:
        print("\n".join(FAILURES), file=sys.stderr); return 1
    domains = []
    for entry in entries:
        domain = derive_domain(entry)
        if domain is None:
            print("\n".join(FAILURES), file=sys.stderr); return 1
        domains.append(domain)
    profile = {
        "status": "profile",
        "contract": CONTRACT,
        "stage": STAGE,
        "source": args.load_state,
        "domains": domains,
        "notes": NOTES,
    }
    text = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

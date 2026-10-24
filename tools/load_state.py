#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""EtherOS M11 用户态装载器(纯工具层,约束 11:不导入/链接任何 kernel/ 与 base/toaruos 代码)。
kernel/interfaces/loader-contract.md §7/§8 的宿主侧参考实现:消费 tools/load_plugins.py 的装载计划
(M7,status "plan-only"),按 plan load_order 逐项回读 manifest 补 protocols/translator 字段,物化
装载状态(registry + 激活路由表 routes + isolation 派生声明),输出 status "loaded" 的 §7 契约 JSON。
启用集与顺序的权威是 plan(约束 50):本工具不重读 config、不自行决定启用集,只物化 plan 已决之事;
plan 与插件树/manifest 漂移即拒(契约 §8)。loaded 只表示宿主侧注册表已物化 + 路由已激活,不表示
已启动/更不表示已运行;内核侧装载与镜像内启动期装载属后续里程碑(约束 29)。
CLI: --plan <plan.json>(必需,load_plugins.py 的产物)、--plugins-root <dir>(缺省仓库 plugins/)、
--out <file>(可选,落盘;缺省只打 stdout)。负例(契约 §8:逐条原因 + stderr + 非 0 退出 + 不输出
状态 JSON):输入非 JSON 对象 / status 非 "plan-only" / contract 非本契约 / plan 条目 id 树中不存在
(ENOENT)/ manifest 与 plan 条目 payload 引用不符 / payload 解析后不存在 / load_order 与条目 id 集
不一致 / 两个已装载条目声明同一协议 token(装载期 EAMBIGUOUS,约束 55)。格式无关(契约 §1/§7):只见
id/type/payload 引用/容器策略/能力 token/协议 token/translator 引用,不检视 payload 内容。"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTRACT = "kernel/interfaces/loader-contract.md"
STAGE = "M11-loader-load"
CATEGORIES = ("builtin", "dev", "optional")  # 与 load_plugins.py 同口径
FAILURES: list[str] = []


def fail(where, reason):
    FAILURES.append(f"FAIL: {where} {reason}")


def rel(path):  # 统一 POSIX 分隔符(与 tools/route_plugins.py rel() 同函数同口径);越出仓库根则退回绝对路径
    path = path.resolve()
    try: return path.relative_to(REPO).as_posix()
    except ValueError: return str(path)


def scan_plugins(root):
    """{name: (manifest_path, manifest, category)};扫描语义同 load_plugins.py(缺 plugin.json /
    JSON 非法 / 重名即记 FAIL)。仅用于 plan 条目 id 的树中存在性校验,不代表启用。"""
    found = {}
    for cat in CATEGORIES:
        base = root / cat
        for d in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
            jf = d / "plugin.json"
            if not jf.is_file():
                fail(jf, "plugin directory without plugin.json (cannot verify a load entry)"); continue
            try:
                m = json.loads(jf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                fail(jf, f"unreadable/invalid JSON: {exc}"); continue
            if not isinstance(m, dict) or not isinstance(m.get("name"), str):
                fail(jf, "manifest is not an object or missing string 'name'"); continue
            if m["name"] in found:
                fail(jf, f"duplicate plugin name '{m['name']}' (also in {found[m['name']][0]})"); continue
            found[m["name"]] = (jf, m, cat)
    return found


def load_plan(plan_path):
    """读 plan 并做 §8 契约级校验(非 JSON 对象 / status 非 "plan-only" / contract 非本契约 /
    enabled·load_order 形态 / load_order 与条目 id 集不一致)。返回 (plan, entries, order);
    校验失败记 FAIL 返回 None。"""
    try:
        plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(plan_path, f"unreadable/invalid JSON: {exc} (load: EINVAL)"); return None
    if not isinstance(plan, dict):
        fail(plan_path, "input is not a JSON object (load: EINVAL)"); return None
    if plan.get("status") != "plan-only":
        fail(plan_path, f"status {plan.get('status')!r} is not 'plan-only' — only a plan-only plan can be loaded (load: EINVAL)"); return None
    if plan.get("contract") != CONTRACT:
        fail(plan_path, f"contract {plan.get('contract')!r} is not this contract '{CONTRACT}' (load: EINVAL)"); return None
    entries = plan.get("enabled")
    order = plan.get("load_order")
    if not isinstance(entries, list) or not isinstance(order, list):
        fail(plan_path, "'enabled'/'load_order' must be arrays (load: EINVAL)"); return None
    for e in entries:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str):
            fail(plan_path, "every 'enabled' entry must be an object with a string 'id' (load: EINVAL)"); return None
    if not all(isinstance(p, str) for p in order):
        fail(plan_path, "'load_order' must be an array of plugin ids (load: EINVAL)"); return None
    entry_ids = [e["id"] for e in entries]
    if sorted(order) != sorted(entry_ids) or len(order) != len(entry_ids):
        fail(plan_path, f"load_order {order} is inconsistent with the enabled entry id set "
                        f"{sorted(entry_ids)} (load: EINVAL)"); return None
    return plan, entries, order


def build_registry(entries, order, found):
    """按 plan load_order 逐项回读 manifest:树中存在性(ENOENT)、payload 引用一致性、payload 悬空
    (§8);补 protocols/translator(manifest 原样)与派生 isolation(固定 PER_PLUGIN)。返回 registry
    列表;任一漂移记 FAIL 返回 None。"""
    by_id = {e["id"]: e for e in entries}
    registry = []
    for pid in order:
        entry = by_id[pid]
        if pid not in found:
            fail(pid, "plan entry id matches no manifest under plugins/{builtin,dev,optional} (load: ENOENT)"); return None
        jf, m, _cat = found[pid]
        manifest_payload = m.get("payload")
        if entry.get("payload") != manifest_payload:
            fail(pid, f"plan entry payload {entry.get('payload')!r} does not match manifest payload "
                      f"{manifest_payload!r} (load: EINVAL)"); return None
        if not isinstance(manifest_payload, str) or not manifest_payload:
            fail(jf, "manifest 'payload' missing or not a non-empty string (load: EINVAL)"); return None
        if not (jf.parent / manifest_payload).resolve().is_file():
            fail(pid, f"payload '{manifest_payload}' does not resolve to an existing file (load: EINVAL)"); return None
        protocols = m.get("protocols")
        if protocols is None:
            protocols = []
        elif not isinstance(protocols, list) or not all(isinstance(t, str) for t in protocols):
            fail(jf, "manifest 'protocols' must be an array of tokens (load: EINVAL)"); return None
        translator = m.get("translator")
        if translator is not None and not isinstance(translator, str):
            fail(jf, "manifest 'translator' must be a string when present (load: EINVAL)"); return None
        registry.append({"id": pid, "type": entry.get("type"), "category": entry.get("category"),
                         "payload": entry.get("payload"), "container": entry.get("container"),
                         "capabilities": entry.get("capabilities") or [],
                         "protocols": protocols, "translator": translator,
                         "manifest": rel(jf), "isolation": "PER_PLUGIN"})
    return registry


def build_routes(registry, found):
    """激活路由表(契约 §7):仅已装载且 type == compat-bridge 且 protocols 非空的条目;同 token 两个
    已装载条目即拒(装载期 EAMBIGUOUS,约束 55,不静默择一)。token → {plugin, manifest, translator,
    payload}(与 route 原语 §2.1 同口径)。"""
    routes = {}
    for item in registry:
        if item["type"] != "compat-bridge" or not item["protocols"]:
            continue
        jf, m, _cat = found[item["id"]]
        ppath = jf.parent / m.get("payload", "")
        for token in item["protocols"]:
            if token in routes:
                fail(f"protocol '{token}'", f"ambiguous: loaded plugins '{routes[token]['plugin']}' and "
                                            f"'{item['id']}' both declare it (load: EAMBIGUOUS, constraint 55)")
                return None
            routes[token] = {"plugin": item["id"], "manifest": item["manifest"],
                             "translator": item["translator"], "payload": rel(ppath)}
    return routes


def main():
    ap = argparse.ArgumentParser(description="EtherOS userland loader (M11, host-side reference of kernel/interfaces/loader-contract.md §7/§8)")
    ap.add_argument("--plan", required=True, help="load plan JSON produced by tools/load_plugins.py")
    ap.add_argument("--plugins-root", default=str(REPO / "plugins"), help="plugin tree root")
    ap.add_argument("--out", help="write the load state to this file (default: stdout only)")
    args = ap.parse_args()
    loaded = load_plan(args.plan)
    if loaded is None:
        print("\n".join(FAILURES), file=sys.stderr); return 1
    plan, entries, order = loaded
    found = scan_plugins(Path(args.plugins_root))
    if FAILURES:
        print("\n".join(FAILURES), file=sys.stderr); return 1
    registry = build_registry(entries, order, found)
    if registry is None:
        print("\n".join(FAILURES), file=sys.stderr); return 1
    routes = build_routes(registry, found)
    if routes is None:
        print("\n".join(FAILURES), file=sys.stderr); return 1
    state = {
        "status": "loaded",
        "contract": CONTRACT,
        "stage": STAGE,
        "plan_contract": plan["contract"],
        "registry": registry,
        "load_order": order,
        "routes": routes,
        "skipped": plan.get("skipped", []),
        "notes": [
            "loaded = 宿主侧已登记 + 路由已激活,非已启动/非已运行;内核侧装载与镜像内启动期装载属后续里程碑(约束 29)。",
            "isolation 为计划级声明(PER_PLUGIN,loader_if.h 既有 enum),非强制;隔离强制属后续安全模型里程碑(约束 52)。",
            "歧义提前:两个已装载条目声明同一协议 token 时装载期拒绝(ETHEROS_EAMBIGUOUS,约束 55),与 route 原语同口径、只是提前。",
            "启用集与装载顺序的权威是 plan(约束 50):registry 顺序与 plan load_order 逐项相等,skipped 原样承袭输入 plan。",
            "格式无关(契约 §1/§7):条目只携带 manifest 已声明的 id/type/payload 引用/容器策略/能力 token/协议 token/translator 引用,不检视 payload 内容。",
        ],
    }
    text = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

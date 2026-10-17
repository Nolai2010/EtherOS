#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""EtherOS M7 用户态装载计划生成器(纯工具层,Global Constraint 11:不导入/链接任何 kernel/ 与
base/toaruos 代码)。kernel/interfaces/loader-contract.md 的宿主侧参考实现:输出键名与契约 §2 逐字
对齐;格式无关(只见插件 id/类型/payload 引用/容器策略,不检视 payload 内容,契约 §1)。
本工具只生成装载计划,status 固定 "plan-only":未真正装载、未启动任何插件;启动期装载(镜像内
/etc/os/config.toml 覆盖 + 真实加载)属后续里程碑(约束 29)。约束 12:config [plugins] enabled
是启用唯一事实源(builtin/dev 隐式启用,optional 显式启用,与 validator/route_plugins 同语义)。
CLI: 缺省=读 config/default.toml + plugins/ 出计划;--config <toml>=覆盖配置(负例用);
--plugins-root <dir>=覆盖插件根。负例(逐条 FAIL + exit 1):enabled id 树中不存在(ENOENT)/
插件目录缺 plugin.json 或 JSON 非法(EINVAL)/manifest payload 解析后不存在(EINVAL,与 M2
validator 同语义)/依赖 id 未在本次装载的启用集里(ENOENT)/依赖成环(非 0 退出并列出环上成员,
约束 41)。schema v2 起 manifest 支持可选 dependencies 字段 → load_order = 依赖拓扑序(被依赖者
在前);无依赖时退化为目录序遍历序(builtin → dev → optional,各类内目录名字典序),并在 notes
记档(不自造字段,契约 §3)。"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTRACT = "kernel/interfaces/loader-contract.md"
STAGE = "M7-loader-plan"
CATEGORIES = ("builtin", "dev", "optional")  # 装载顺序即此序(契约 §3)
FAILURES: list[str] = []


def fail(where, reason):
    FAILURES.append(f"FAIL: {where} {reason}")


def scan_plugins(root):
    """{name: (manifest_path, manifest, category)};缺 plugin.json / JSON 非法 / 重名即记 FAIL。"""
    found = {}
    for cat in CATEGORIES:
        base = root / cat
        for d in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
            jf = d / "plugin.json"
            if not jf.is_file():
                fail(jf, "plugin directory without plugin.json (cannot plan a load entry)"); continue
            try:
                m = json.loads(jf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                fail(jf, f"unreadable/invalid JSON: {exc}"); continue
            if not isinstance(m, dict) or not isinstance(m.get("name"), str):
                fail(jf, "manifest is not an object or missing string 'name'"); continue
            if m["name"] in found:
                fail(jf, f"duplicate plugin name '{m['name']}' (also in {found[m['name']][0]})"); continue
            found[m["name"]] = (jf, m, cat)
    if not found:  # 零 manifest 守卫(同 validator 职责 2 口径),防静默空计划
        fail(root, "no plugin manifest under {builtin,dev,optional}/*/plugin.json (zero-manifest guard)")
    return found


def load_enabled(config_path):
    """[plugins] enabled 列表;段缺失/不可读/类型错即记 FAIL 返回 None(约束 12 防静默)。"""
    try:
        section = tomllib.loads(Path(config_path).read_text(encoding="utf-8")).get("plugins")
        if not isinstance(section, dict):
            raise LookupError("missing [plugins] section — config is the single source of plugin enablement (Global Constraint 12)")
        enabled = section.get("enabled", [])
        if not isinstance(enabled, list):
            raise TypeError("[plugins] enabled must be an array of plugin ids")
    except (OSError, tomllib.TOMLDecodeError, LookupError, TypeError) as exc:
        fail(config_path, str(exc)); return None
    return enabled


def find_cycle(deps, remaining):
    """在 remaining 节点上做 DFS 取一个环;返回 [n1, n2, ..., n1](首尾同节点明示闭环)。"""
    stack, on_stack, seen = [], set(), set()

    def dfs(node):
        stack.append(node); on_stack.add(node); seen.add(node)
        for dep in deps.get(node, ()):
            if dep not in remaining:
                continue
            if dep in on_stack:
                return stack[stack.index(dep):] + [dep]
            if dep not in seen:
                hit = dfs(dep)
                if hit:
                    return hit
        stack.pop(); on_stack.discard(node)
        return None

    for node in sorted(remaining):
        if node not in seen:
            hit = dfs(node)
            if hit:
                return hit
    return sorted(remaining)


def resolve_load_order(order, deps):
    """依赖拓扑序(Kahn):被依赖者在前;同批就绪者按入参 order(目录序)取,故无依赖时逐字退化
    为目录序。成环 → 记 FAIL 并列出环上成员,返回 None(约束 41:不得静默跳过、不得只 warn)。"""
    rank = {pid: i for i, pid in enumerate(order)}
    indeg = {pid: 0 for pid in order}
    dependents = {pid: [] for pid in order}
    for pid in order:
        for dep in deps.get(pid, ()):
            indeg[pid] += 1
            dependents[dep].append(pid)
    ready = [p for p in order if indeg[p] == 0]
    out = []
    while ready:
        pid = ready.pop(0)
        out.append(pid)
        for d in dependents[pid]:
            indeg[d] -= 1
            if indeg[d] == 0:
                ready.append(d)
        ready.sort(key=rank.get)  # 稳定排序:就绪集合始终按目录序消费
    if len(out) != len(order):
        cycle = find_cycle(deps, {p for p in order if indeg[p] > 0})
        fail("dependency cycle", f"detected among: {' → '.join(cycle)} (load: EINVAL, constraint 41)")
        return None
    return out


def check_dependencies(order, deps, found, config_path):
    """依赖 id 必须落在本次装载的启用集里。分层口径(约束 41):validator 管插件树里有没有这个 id
    (存在性 / 自依赖 / 重复),本装载器管这一次装载有没有启用它 —— 树里有但没启用同样拒绝。"""
    planned = set(order)
    for pid in order:
        for dep in deps.get(pid, ()):
            if dep in planned:
                continue
            if dep in found:
                fail(config_path, f"plugin '{pid}' depends on '{dep}', which exists in the plugin tree but is not enabled in this load "
                                  f"(optional plugins must be listed in [plugins] enabled — Global Constraint 12)")
            else:
                fail(pid, f"plugin '{pid}' depends on '{dep}', which matches no manifest under "
                          f"plugins/{{builtin,dev,optional}} (load: ENOENT)")


def build_plan(enabled, found, config_path):
    """(entries, skipped, order, deps);payload 悬空记 FAIL(契约 §5-3);optional 未启用进 skipped。"""
    entries, skipped, order, deps = [], [], [], {}
    for cat in CATEGORIES:
        group = sorted((v for v in found.values() if v[2] == cat), key=lambda v: v[0].parent.name)
        for jf, m, c in group:
            if c == "optional" and m["name"] not in enabled:
                skipped.append({"id": m["name"],
                                "reason": "optional plugin not listed in [plugins] enabled — config is the single source of enablement (Global Constraint 12)"})
                continue
            payload = m.get("payload")
            if not isinstance(payload, str) or not payload:
                fail(jf, "manifest 'payload' missing or not a non-empty string (load: EINVAL)"); continue
            if not (jf.parent / payload).resolve().is_file():
                fail(m["name"], f"payload '{payload}' does not resolve to an existing file (load: EINVAL)"); continue
            declared = m.get("dependencies", [])
            if not isinstance(declared, list) or not all(isinstance(d, str) for d in declared):
                fail(jf, "manifest 'dependencies' must be an array of plugin ids (load: EINVAL)"); continue
            deps[m["name"]] = declared
            entries.append({"id": m["name"], "type": m.get("type"), "category": c,
                            "payload": payload, "container": m.get("container"),
                            "capabilities": m.get("capabilities") or []})
            order.append(m["name"])
    for pid in enabled:  # 契约 §5-1: enabled id 必须命中树中 manifest(ENOENT 语义)
        if pid not in found:
            fail(config_path, f"[plugins] enabled id '{pid}' matches no manifest under plugins/{{builtin,dev,optional}} (load: ENOENT)")
    return entries, skipped, order, deps


def main():
    ap = argparse.ArgumentParser(description="EtherOS userland load-plan generator (M7, host-side reference of kernel/interfaces/loader-contract.md)")
    ap.add_argument("--config", default=str(REPO / "config" / "default.toml"), help="config TOML path")
    ap.add_argument("--plugins-root", default=str(REPO / "plugins"), help="plugin tree root")
    args = ap.parse_args()
    found = scan_plugins(Path(args.plugins_root))
    enabled = load_enabled(args.config)
    if FAILURES or enabled is None:
        print("\n".join(FAILURES)); return 1
    entries, skipped, order, deps = build_plan(enabled, found, args.config)
    if FAILURES:
        print("\n".join(FAILURES)); return 1
    check_dependencies(order, deps, found, args.config)
    resolved = None if FAILURES else resolve_load_order(order, deps)  # 依赖未启用时不再进图算法
    if FAILURES or resolved is None:
        print("\n".join(FAILURES)); return 1
    by_id = {e["id"]: e for e in entries}
    entries = [by_id[pid] for pid in resolved]  # enabled 顺序即装载顺序(契约 §2)
    order = resolved
    plan = {
        "status": "plan-only",
        "contract": CONTRACT,
        "stage": STAGE,
        "enabled": entries,
        "load_order": order,
        "skipped": skipped,
        "notes": [
            "plan-only:本工具只生成装载计划,未真正装载、未启动任何插件(约束 29)。",
            "启动期装载(镜像内 /etc/os/config.toml 覆盖 + 真实加载)属后续里程碑。",
            "schema v2 起 manifest 支持可选 dependencies 字段:load_order 为依赖拓扑序(被依赖者在前);无依赖时退化为目录序遍历序(builtin → dev → optional,各类内目录名字典序)。",
            "依赖 id 必须落在本次装载的启用集里(树里有但未启用同样拒绝);依赖成环由本装载器检测,检测到即拒绝出计划(非 0 退出并列出环上成员,约束 41)。",
            "格式无关:条目只携带 manifest 已声明的 id/type/payload 引用/容器策略/能力 token,不检视 payload 内容(契约 §1)。",
        ],
    }
    json.dump(plan, sys.stdout, ensure_ascii=False, indent=2); print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

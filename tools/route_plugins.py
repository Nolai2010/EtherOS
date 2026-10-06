#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""EtherOS M3 协议路由解析器(纯用户态,约束 11:不导入/链接任何 kernel/ 代码)。
kernel/interfaces/plugin-routing.md route 原语的宿主侧参考实现:输出键名与三原语对齐;只消费
manifest 已声明 protocols,零格式知识、不检视 payload 内容(契约 §1/§3)。
--protocol <p>:在 enabled 的 compat-bridge 中解析 plugin→translator→payload 路由链 JSON,
零命中(ENOENT)/多命中(EAMBIGUOUS)→ 逐条 FAIL + exit 1;--run <name>:native 经 sh 调 payload
(双保险不依赖可执行位),compat-bridge 仅调用户态 translator 出翻译计划、绝不执行 foreign
payload(约束 16/17);两参数缺省=打印 enabled 全集路由摘要 exit 0。约束 12:config [plugins]
enabled 是启用唯一事实源(builtin/dev 隐式启用,与 validator 同语义)。"""
import argparse, json, subprocess, sys, tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CATEGORIES = ("builtin", "optional", "dev")
FAILURES: list[str] = []


def fail(where, reason):
    FAILURES.append(f"FAIL: {where} {reason}")


def collect(config_path):
    """enabled 插件集 {name: (manifest_path, manifest)};扫描语义同 validator 职责 2(排除 README)。"""
    manifests = []
    for cat in CATEGORIES:
        base = REPO / "plugins" / cat
        for d in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
            for jf in sorted(d.glob("*.json")):
                if jf.name.upper().startswith("README"): continue  # 职责 2: 排除 README
                try: m = json.loads(jf.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    fail(jf, f"unreadable/invalid JSON: {exc}"); continue
                if isinstance(m, dict) and isinstance(m.get("name"), str): manifests.append((jf, m))
    try:  # 约束 12: [plugins] 段缺失/不可读即红,防静默
        section = tomllib.loads(Path(config_path).read_text(encoding="utf-8")).get("plugins")
        if not isinstance(section, dict): raise LookupError("missing [plugins] section — config is the single source of plugin enablement (Global Constraint 12)")
        enabled = section.get("enabled", [])
        if not isinstance(enabled, list): raise TypeError("[plugins] enabled must be an array of plugin ids")
    except (OSError, tomllib.TOMLDecodeError, LookupError, TypeError) as exc:
        fail(config_path, str(exc)); return None
    enabled_ids, plugins = set(enabled), {}
    for jf, m in manifests:
        if next((p for p in jf.parts if p in CATEGORIES), "optional") == "optional" and m["name"] not in enabled_ids:
            continue  # 约束 12: optional 未列入 enabled 即不路由(目录内无启用开关)
        if m["name"] in plugins: fail(jf, f"duplicate plugin name '{m['name']}'"); continue
        plugins[m["name"]] = (jf, m)
    for pid in enabled:  # 与 validator 职责 5 同口径: enabled id 必须命中真实 manifest
        if pid not in plugins: fail(config_path, f"[plugins] enabled id '{pid}' matches no manifest")
    return None if FAILURES else plugins


def rel(path):  # 统一 POSIX 分隔符(跨平台/CI 可比);越出仓库根则退回绝对路径
    path = path.resolve()
    try: return path.relative_to(REPO).as_posix()
    except ValueError: return str(path)


def cmd_protocol(plugins, protocol):
    # route(query) -> plugin_id(契约 §2.1): 只消费已声明 protocols,不做语义推断
    hits = [(jf, m) for jf, m in plugins.values() if m.get("type") == "compat-bridge" and protocol in (m.get("protocols") or [])]
    if len(hits) != 1:  # 零命中 ENOENT / 多命中 EAMBIGUOUS,不静默择一(契约 §2.1)
        fail(f"protocol '{protocol}'", "no enabled plugin declares it (route: ENOENT)" if not hits else
             f"ambiguous: {len(hits)} enabled plugins declare it (route: EAMBIGUOUS): " + ", ".join(sorted(m["name"] for _, m in hits)))
        return 1
    jf, m = hits[0]
    ppath = jf.parent / m.get("payload", "")
    if not ppath.resolve().is_file():  # load 失败语义(契约 §2.2): payload 引用悬空 → EINVAL
        fail(m["name"], f"payload '{m.get('payload')}' does not resolve to an existing file (load: EINVAL)")
        return 1
    json.dump({"query": {"protocol": protocol},
               "route": {"plugin": m["name"], "manifest": rel(jf), "translator": m.get("translator"), "payload": rel(ppath)},
               "next": ["translator", "load"], "status": "routed"}, sys.stdout, ensure_ascii=False, indent=2); print()
    return 0


def cmd_run(plugins, name):
    if name not in plugins:
        fail(name, "no such enabled plugin (Global Constraint 12)")
        return 1
    jf, m = plugins[name]
    deny = lambda reason: (fail(name, reason), 1)[1]
    if m.get("type") == "compat-bridge":  # 约束 17: foreign payload 只装载引用、永不执行(契约 §2.2 不变量)
        tpath = REPO / m["translator"] if m.get("translator") else None
        if not tpath or not tpath.is_file():
            return deny(f"translator {m.get('translator')!r} missing — cannot produce translation plan")
        if subprocess.run([sys.executable, str(tpath), "--manifest", str(jf)]).returncode:
            return deny("translator exited non-zero (plan not produced)")
        return 0
    ppath = (jf.parent / m.get("payload", "")).resolve()  # native: 经 sh 调 payload(双保险,不依赖可执行位)
    if not m.get("payload") or not ppath.is_file():
        return deny(f"payload {m.get('payload')!r} does not resolve to an existing file (load: EINVAL)")
    if subprocess.run(["sh", str(ppath)]).returncode:
        return deny("payload exited non-zero")
    return 0


def cmd_summary(plugins):
    routes = [{"plugin": n, "type": m.get("type"), "protocols": m.get("protocols", []),
               "payload": m.get("payload"), "translator": m.get("translator")} for n, (jf, m) in sorted(plugins.items())]
    json.dump({"status": "summary", "enabled": routes, "next": ["route", "load", "isolate"]}, sys.stdout, ensure_ascii=False, indent=2); print()
    return 0


def main():
    ap = argparse.ArgumentParser(description="EtherOS userland protocol route resolver (M3, host-side reference of kernel/interfaces/plugin-routing.md)")
    ap.add_argument("--protocol", help="resolve route chain for a protocol token")
    ap.add_argument("--run", metavar="PLUGIN", help="run native payload via sh; compat-bridge gets translator plan only")
    ap.add_argument("--config", default=str(REPO / "config" / "default.toml"), help="config TOML path")
    args = ap.parse_args()
    plugins = collect(Path(args.config))
    rc = 0 if plugins is None else cmd_protocol(plugins, args.protocol) if args.protocol else cmd_run(plugins, args.run) if args.run else cmd_summary(plugins)
    if FAILURES:
        print("\n".join(FAILURES))
        return 1
    return rc


if __name__ == "__main__":
    sys.exit(main())

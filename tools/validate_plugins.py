#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""EtherOS M2 插件 manifest 校验器(纯工具层,Global Constraint 11:不导入/链接任何 kernel/ 代码)。
职责 1-7 见计划 Task 3;spec 依据 spec/2026-10-05-etheros-dev-policy.md(注释标注段落)。
CLI(职责 7): 缺省=全树校验(含 config 一致性);--file <manifest>=单文件校验(负例循环用,跳过
config 一致性);--config <toml>=覆盖默认 config/default.toml。单文件模式目录规则:按路径中的
builtin/optional/dev 段推断类别,推断不到按 optional 处理(M2 负例循环约定,M2 示例均 optional,约束 14)。
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

REPO = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO / "plugins" / "schema" / "plugin.schema.json"
# spec §3.2 三类目录;compat/ 不扫描(M2 无翻译运行时实体,约束 13)
CATEGORIES = ("builtin", "optional", "dev")
FAILURES: list[str] = []


def fail(where, reason):
    FAILURES.append(f"FAIL: {where} {reason}")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        fail(path, f"unreadable/invalid JSON: {exc}")
        return None


def load_schema_validator():
    # 职责 1: schema 元校验,防 schema 自身损坏(M2-01;spec §2.4 契约版本化)
    schema = load_json(SCHEMA_PATH)
    if schema is None:
        return None
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        fail(SCHEMA_PATH, f"schema meta-validation failed: {exc.message}")
        return None
    return Draft202012Validator(schema)


def semantic_checks(path, manifest, schema_validator, names, file_mode):
    """职责 3(schema 结构校验)+ 职责 4(语义校验);目录类别按路径中类别段推断(spec §3.2)。"""
    for err in sorted(schema_validator.iter_errors(manifest), key=lambda e: e.json_path):
        fail(path, f"schema: {err.message}")  # 职责 3: 结构校验(schema v1,计划 Task 2)
    if not isinstance(manifest, dict):
        return
    name = manifest.get("name")
    if isinstance(name, str):  # 职责 4a: name 全树唯一(spec §3.2 插件目录即插件)
        if name in names:
            fail(path, f"duplicate plugin name '{name}' (also defined in {names[name]})")
        else:
            names[name] = str(path)
    payload = manifest.get("payload")
    # 职责 4b: payload 相对路径文件存在(spec §2.2 "同级二进制";计划职责 7: 允许 .. 跨目录引用,只断言解析后真实存在)
    if isinstance(payload, str) and payload and not (Path(path).parent / payload).resolve().is_file():
        fail(path, f"payload '{payload}' does not resolve to an existing file")
    # 职责 4c: compat-bridge ⇒ protocols 非空 + translator 前缀 plugins/compat/(spec §2.2;语义层兜底,schema 已表达)
    if manifest.get("type") == "compat-bridge":
        if not manifest.get("protocols"):
            fail(path, "compat-bridge requires non-empty protocols (spec §2.2)")
        if not str(manifest.get("translator", "")).startswith("plugins/compat/"):
            fail(path, f"compat-bridge translator must be under plugins/compat/ (spec §2.2), got {manifest.get('translator')!r}")
        elif isinstance(manifest.get("translator"), str):
            # 职责 4c M3 增量(M3-02): 前缀合法的 translator 解析后必须真实存在为文件
            # (spec §2.2 "translator 指向 plugins/compat/ 下的翻译运行时";M2 仅断言前缀,未断言存在性)
            tpath = REPO / manifest["translator"]
            if not tpath.is_file():
                fail(path, f"compat-bridge translator '{manifest['translator']}' does not resolve to an existing file under repo root (spec §2.2, M3-02)")
    cat = next((p for p in Path(path).parts if p in CATEGORIES), "optional" if file_mode else None)
    if cat is not None:  # 职责 4d: 目录规则(spec §2.2/§3.2): builtin/dev ⇒ uninstallable==false,optional ⇒ true
        want = cat == "optional"
        if manifest.get("uninstallable") is not want:
            fail(path, f"directory rule: plugins/{cat}/ requires uninstallable=={str(want).lower()}, got {manifest.get('uninstallable')!r}")


def validate_tree(config_path, schema_validator):
    names, manifests, count = {}, [], 0
    # 职责 2: 扫描 plugins/{builtin,optional,dev}/*/ 的 plugin.json 及 *.json 别名,排除 README(约束 14 命名约定);零 manifest ⇒ 报错防静默空过
    for cat in CATEGORIES:
        base = REPO / "plugins" / cat
        for plugin_dir in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
            for jf in sorted(plugin_dir.glob("*.json")):
                if jf.name.upper().startswith("README"):
                    continue  # 职责 2: 排除 README
                count += 1
                manifest = load_json(jf)
                if manifest is not None:
                    if schema_validator is not None:
                        semantic_checks(jf, manifest, schema_validator, names, file_mode=False)
                    manifests.append((jf, manifest))
    if count == 0:
        fail(REPO / "plugins", "no plugin manifest under plugins/{builtin,optional,dev}/*/ (zero-manifest guard, 职责 2)")
    # 职责 5: 配置一致性(Global Constraint 12: config [plugins] 是启用唯一事实源;段缺失报错防静默;builtin/dev 隐式启用)
    try:
        with open(config_path, "rb") as fh:
            cfg = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        fail(config_path, f"config unreadable: {exc}")
        cfg = {}
    section = cfg.get("plugins")
    if not isinstance(section, dict):
        fail(config_path, "missing [plugins] section — config is the single source of plugin enablement (Global Constraint 12)")
        section = {}
    enabled = section.get("enabled", [])
    if not isinstance(enabled, list):
        fail(config_path, "[plugins] enabled must be an array of plugin ids")
        enabled = []
    by_name = {}
    for path, manifest in manifests:
        if isinstance(manifest, dict) and isinstance(manifest.get("name"), str):
            by_name.setdefault(manifest["name"], []).append((path, manifest))
    for pid in enabled:
        hits = by_name.get(pid, [])
        if len(hits) != 1:  # 职责 5: enabled id 必须命中恰好一个 manifest
            fail(config_path, f"[plugins] enabled id '{pid}' matches {len(hits)} manifests, must hit exactly one (职责 5)")
        elif hits[0][1].get("uninstallable") is not True:
            fail(hits[0][0], f"enabled id '{pid}' must have uninstallable==true (职责 5)")


def main():
    ap = argparse.ArgumentParser(description="EtherOS plugin manifest validator (M2, schema v1)")
    ap.add_argument("--file", help="validate a single manifest file (skips config consistency)")
    ap.add_argument("--config", default=str(REPO / "config" / "default.toml"), help="config TOML path")
    args = ap.parse_args()  # 职责 7: --file/--config,两参数缺省 = 全树校验
    schema_validator = load_schema_validator()
    if args.file:  # 单文件模式: 职责 3+4 的文件内检查;不做目录扫描与 config 一致性(计划职责 7)
        manifest = load_json(args.file)
        if manifest is not None and schema_validator is not None:
            semantic_checks(args.file, manifest, schema_validator, {}, file_mode=True)
    else:
        validate_tree(Path(args.config), schema_validator)
    if FAILURES:
        print("\n".join(FAILURES))
        return 1  # 职责 6: 任何失败逐条打印 FAIL + exit 1
    print("plugins validation: OK")  # 职责 6: 全过打印 OK + exit 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""EtherOS M10 桌面条目翻译器 —— compat 层首个**真**翻译实现(约束 44/45/47/48)。

【诚实边界(本文件最重要的一节)】
这是**描述符级翻译**:把外部应用的 freedesktop `.desktop` 描述符文本翻译成 EtherOS
插件 manifest v2 + 一个包装 payload。它**不是二进制指令翻译**:
  - 不解析 exe/ipa/apk 等二进制容器;
  - 不做指令集解码、不做系统调用转换、不做沙箱内执行;
  - `Exec=` 字段只作**字符串原样转发**进包装 payload(约束 47),本工具从不执行它。
因此 `status: "translated"` 只表示"产物已真实写出",**不表示已装载、更不表示已运行**
(装载属启动期能力,仍属后续里程碑)。
`plugins/optional/douyin/`(protocols: ["ipa"])与 `plugins/compat/stub-runtime/`
继续是 stub:不因本里程碑出现真实现就改口径(差异点 2)。

【为什么是 .desktop】
freedesktop 桌面条目是真实存在的纯文本描述符格式(`[Desktop Entry]` / `Name=` /
`Exec=` / `Type=` …),可被真正解析;而二进制指令翻译属 spec §6 风险 8 明示的后期项。

CLI(沿用 M3 契约,与 plugins/compat/stub-runtime/translator.py 同形):
  translator.py --manifest <源声明 JSON> [--payload <.desktop 路径>]
                [--out <输出目录>] [--name <覆盖插件 id>]
  --payload 缺省时取 manifest 的 payload 字段(相对 manifest 所在目录解析)。
  --out 缺省为 <manifest 所在目录>/translated。
  exit 0 = 已真实写出 manifest + 包装 payload(打印结果 JSON);
  exit 2 = 拒绝(入口不可用/非 desktop-entry/缺关键字段/id 冲突等),给出原因、不产出。
stdlib only(与 M3 stub 同族);不导入/链接任何 kernel/ 代码(约束 11)。
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # plugins/compat/desktop-entry/translator.py → 仓库根
TRANSLATOR_REL = "plugins/compat/desktop-entry/translator.py"  # 产出 manifest 指回本 translator
SECTION = "Desktop Entry"
GROUP_RE = re.compile(r"^\[(.+)\]$")
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
CATEGORIES = ("builtin", "optional", "dev")  # 与 tools/validate_plugins.py 同的三类目录
SOURCE_FORMAT = "desktop-entry"
GENERATED_VERSION = "0.1.0"  # 合法 semver(schema v2 version pattern)


def refuse(reason):
    # 拒绝即明说:不产出、exit 2,绝不伪装成功(与 M3 stub 同口径)
    print(f"translator: {reason}", file=sys.stderr)
    return 2


def slugify(raw):
    """小写化 + 非字母数字转 '-' + 折叠连续 '-'(归一化算法第 1/2/4 步)。"""
    out = []
    for ch in raw.strip().lower():
        out.append(ch if ("a" <= ch <= "z" or "0" <= ch <= "9") else "-")
    return re.sub(r"-+", "-", "".join(out))


def normalize_name(raw):
    """Name → 插件 id 的归一化(差异点 4,规则在 README 逐条记档)。
    1) 小写化;2) 非字母数字字符转 '-';3) 折叠连续 '-';
    4) 去前导非字母(含 '-' 与数字,因 id 首字符必须是 [a-z]);5) 去尾 '-'。
    例:'Demo Desktop App' → 'demo-desktop-app';'3D Viewer' → 'd-viewer'。"""
    s = slugify(raw).strip("-")
    i = 0
    while i < len(s) and not ("a" <= s[i] <= "z"):
        i += 1
    return s[i:].rstrip("-")


def category_capabilities(raw):
    """Categories → capabilities:分号切分,逐 token 归一化后加 'desktop.category.' 前缀。
    与既有插件的点分 capability token(fs.browse / compat.ipa.bridge)同族。"""
    caps = []
    for tok in raw.split(";"):
        slug = slugify(tok).strip("-")
        if not slug:
            continue
        cap = f"desktop.category.{slug}"
        if cap not in caps:
            caps.append(cap)
    return caps


def parse_desktop_entry(text):
    """解析 [Desktop Entry] 段;返回 (fields, reason)。
    只取该段内的 `Key=Value`;段外内容一律不采信(防 [Desktop Action x] 等同名键污染)。
    本地化键(`Name[zh_CN]=`)显式忽略并在 README 记档;行续接(\\ 结尾)不受理。
    """
    fields = {}
    group = None
    seen_section = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = GROUP_RE.match(line)
        if m:
            group = m.group(1)
            if group == SECTION:
                seen_section = True
            continue
        if group != SECTION or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key or "[" in key:  # 本地化键忽略
            continue
        fields.setdefault(key, value.strip())
    if not seen_section:
        first = next((l.strip() for l in text.splitlines() if l.strip()), "")
        hint = " (looks like JSON, not a desktop entry)" if first.startswith("{") else ""
        return None, f"payload is not a freedesktop desktop entry: no [{SECTION}] section{hint}"
    return fields, None


def tree_plugin_ids():
    """全树已声明插件 id(只读 name,不校验、不报错);与 validator 的 tree_plugin_ids 同口径。"""
    ids = set()
    for cat in CATEGORIES:
        base = REPO / "plugins" / cat
        if not base.is_dir():
            continue
        for jf in sorted(base.glob("*/*.json")):
            if jf.name.upper().startswith("README"):
                continue
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(data, dict) and isinstance(data.get("name"), str):
                ids.add(data["name"])
    return ids


def load_source(mpath):
    """读源声明 JSON;返回 (manifest, reason)。"""
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"manifest unreadable: {exc}"
    if not isinstance(manifest, dict):
        return None, "manifest is not a JSON object"
    kind = manifest.get("type")
    if kind is not None and kind != "compat-bridge":
        return None, f"plugin {manifest.get('name')!r} is type {kind!r}, not compat-bridge — nothing to translate"
    protocols = manifest.get("protocols")
    if isinstance(protocols, list) and protocols and SOURCE_FORMAT not in protocols:
        return None, (f"translator handles {SOURCE_FORMAT!r} only, source declares "
                      f"protocols {protocols!r} — refuse to guess another format")
    return manifest, None


def read_payload(ppath):
    """读外部 .desktop 描述符;返回 (text, reason)。约束 47:只读纯文本,不解析/执行二进制。"""
    try:
        raw = ppath.read_bytes()
    except OSError as exc:
        return None, f"payload unreadable: {exc}"
    if not raw.strip():
        return None, f"payload '{ppath.name}' is empty (0 bytes / blank) — nothing to translate"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, f"payload '{ppath.name}' is not UTF-8 text — refuse to parse binary payloads (约束 47)"
    return text, None


def main():
    ap = argparse.ArgumentParser(description="EtherOS compat desktop-entry translator (M10, real descriptor-level translation)")
    ap.add_argument("--manifest", required=True, help="source declaration JSON path")
    ap.add_argument("--payload", help="payload path override (default: manifest payload field)")
    ap.add_argument("--out", help="output directory (default: <manifest dir>/translated)")
    ap.add_argument("--name", help="override the normalized plugin id (must match ^[a-z][a-z0-9-]*$)")
    args = ap.parse_args()

    mpath = Path(args.manifest)
    manifest, reason = load_source(mpath)
    if manifest is None:
        return refuse(reason)

    payload = args.payload or manifest.get("payload", "")
    if not payload:
        return refuse("no payload path given (--payload) and manifest has no payload field")
    ppath = (mpath.parent / payload).resolve() if not Path(payload).is_absolute() else Path(payload)
    if not ppath.is_file():
        return refuse(f"payload '{payload}' does not resolve to an existing file")

    text, reason = read_payload(ppath)
    if text is None:
        return refuse(reason)
    fields, reason = parse_desktop_entry(text)
    if fields is None:
        return refuse(reason)

    entry_type = fields.get("Type")
    if entry_type is None:
        return refuse("desktop entry has no Type= — cannot decide Application/Link/Directory")
    if entry_type != "Application":
        return refuse(f"desktop entry Type={entry_type!r} is not supported — only Type=Application maps to a compat-bridge plugin "
                      f"(Type=Link/Directory have no Exec payload to bridge)")
    original_name = fields.get("Name")
    if not original_name:
        return refuse("desktop entry has no Name= (or it is empty) — cannot derive a plugin id")
    if not fields.get("Exec"):
        return refuse("desktop entry has no Exec= (or it is empty) — nothing to forward into the wrapper payload")

    if args.name:
        pid = args.name
        if not ID_RE.match(pid):
            return refuse(f"--name {pid!r} does not match ^[a-z][a-z0-9-]*$")
    else:
        pid = normalize_name(original_name)
        if not pid:
            return refuse(f"Name={original_name!r} normalizes to an empty plugin id — cannot derive a valid id")
        if not ID_RE.match(pid):
            return refuse(f"Name={original_name!r} normalizes to {pid!r}, which violates ^[a-z][a-z0-9-]*$")

    source_name = manifest.get("name") if isinstance(manifest.get("name"), str) else None
    if pid != source_name and pid in tree_plugin_ids():
        return refuse(f"normalized plugin id '{pid}' (from Name={original_name!r}) collides with an existing plugin id in "
                      f"plugins/{{{','.join(CATEGORIES)}}} — refuse to overwrite another plugin (差异点 4)")

    payload_name = f"{pid}.payload"
    caps = category_capabilities(fields["Categories"]) if fields.get("Categories") else []
    out_manifest = {
        "schema_version": "2",
        "name": pid,
        "version": GENERATED_VERSION,
        "type": "compat-bridge",
        "uninstallable": True,  # optional 目录规则(validator 职责 4d)
        "payload": payload_name,
        "container": {"desktop": "windowed"},
        "protocols": [SOURCE_FORMAT],
        "translator": TRANSLATOR_REL,
    }
    if caps:
        out_manifest["capabilities"] = caps

    outdir = Path(args.out) if args.out else mpath.parent / "translated"
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "plugin.json").write_text(json.dumps(out_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (outdir / payload_name).write_text(wrapper_text(ppath, fields), encoding="utf-8")
    except OSError as exc:
        return refuse(f"cannot write translation artifacts to {outdir}: {exc}")

    result = {
        "plugin": pid,
        "source_format": SOURCE_FORMAT,
        "target_format": "etheros-native",
        "protocols": [SOURCE_FORMAT],
        "status": "translated",
        "kind": "descriptor-level",
        "source_payload": str(ppath),
        "manifest": str(outdir / "plugin.json"),
        "payload": str(outdir / payload_name),
        "steps": ["parse-desktop-entry", "normalize-name", "emit-manifest-v2", "emit-wrapper-payload"],
        "note": ("descriptor-level translation: .desktop descriptor text → EtherOS manifest v2 + wrapper payload. "
                 "NOT binary instruction translation — no instruction decoding, no syscall translation, no in-sandbox execution; "
                 "Exec= is forwarded verbatim as a string (约束 47). "
                 "status 'translated' means the artifacts were really written — NOT loaded, NOT run. "
                 "ipa/exe and plugins/optional/douyin/ remain stub (差异点 2)."),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


def wrapper_text(ppath, fields):
    """包装 payload 内容:记录源描述符与原样转发的 Exec 字符串(约束 47)。
    本文件是**数据**,translator 与任何 EtherOS 工具都不解析/执行它;它只证明翻译链路有产物。"""
    lines = [
        "# EtherOS M10 包装 payload —— 描述符级翻译产物,非二进制指令翻译产物",
        f"# generated by {TRANSLATOR_REL}; this file is data: nothing parses or executes it",
        "# Exec= is forwarded VERBATIM as a string: no instruction translation, no syscall mapping, no sandbox run (约束 47)",
        f"# source descriptor: {ppath}",
        "[EtherOS Wrapper]",
        f"Format={SOURCE_FORMAT}",
        f"Name={fields.get('Name', '')}",
        f"Exec={fields.get('Exec', '')}",
    ]
    if fields.get("Comment"):
        lines.append(f"Comment={fields['Comment']}")
    if fields.get("Categories"):
        lines.append(f"Categories={fields['Categories']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())

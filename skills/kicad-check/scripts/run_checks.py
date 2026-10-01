#!/usr/bin/env python3
"""Run KiCad ERC + DRC headlessly and print a compact, grouped summary. Stdlib only, any OS.

    python3 run_checks.py board.kicad_pro            # human summary, exit 1 on any error
    python3 run_checks.py . --json                   # machine-readable summary
    python3 run_checks.py board.kicad_pcb --max 30   # show more examples per type

DRC uses the board's own constraints plus <project>.kicad_dru custom rules, so
copy a fab preset (../assets/rules/*.kicad_dru) next to the board first if you
want to check against a specific fab. Raw JSON reports are kept for drill-down.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

# --- shared with kicad-fab-export/scripts/export_fab.py (kept identical; tests enforce it) ---


def find_kicad_cli(explicit=None):
    """Return the kicad-cli command as a list (Flatpak needs a prefix)."""
    for c in (explicit, os.environ.get("KICAD_CLI"), shutil.which("kicad-cli")):
        if c:
            return [c]
    paths = [
        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
        "/usr/bin/kicad-cli",
        "/usr/local/bin/kicad-cli",
    ]
    # Windows installs per major version: C:\Program Files\KiCad\9.0\bin\kicad-cli.exe
    for root in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.path.expanduser(r"~\AppData\Local\Programs")):
        paths += sorted(glob.glob(os.path.join(root, "KiCad", "*", "bin", "kicad-cli.exe")), reverse=True)
    for p in paths:
        if os.path.isfile(p):
            return [p]
    if shutil.which("flatpak"):
        r = subprocess.run(["flatpak", "info", "org.kicad.KiCad"], capture_output=True)
        if r.returncode == 0:
            return ["flatpak", "run", "--command=kicad-cli", "org.kicad.KiCad"]
    sys.exit("kicad-cli not found. Install KiCad 8+ (https://www.kicad.org/download/) "
             "or set KICAD_CLI=/path/to/kicad-cli")


def kicad_version(cli):
    out = subprocess.run(cli + ["version"], capture_output=True, text=True).stdout
    m = re.search(r"(\d+)\.(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def run(cli, args):
    """Run kicad-cli; return (returncode, combined output). Never raises on non-zero."""
    r = subprocess.run(cli + args, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def resolve_project(path):
    """Accept a dir, .kicad_pro, .kicad_pcb or .kicad_sch. Return (pcb, sch, name); missing files are None."""
    p = Path(path).expanduser().resolve()
    if p.is_dir():
        pros = sorted(p.glob("*.kicad_pro")) or sorted(p.glob("*.kicad_pcb"))
        if len(pros) != 1:
            sys.exit(f"Expected exactly one KiCad project in {p}, found: {[x.name for x in pros] or 'none'}")
        p = pros[0]
    if p.suffix not in (".kicad_pro", ".kicad_pcb", ".kicad_sch"):
        sys.exit(f"Not a KiCad file: {p}")
    pcb, sch = p.with_suffix(".kicad_pcb"), p.with_suffix(".kicad_sch")
    if not pcb.exists() and not sch.exists():
        sys.exit(f"No {pcb.name} or {sch.name} next to {p}")
    return (pcb if pcb.exists() else None), (sch if sch.exists() else None), p.stem

# --- end shared ---


def load_violations(report, kind):
    """Flatten an ERC or DRC JSON report into dicts with kind/type/severity/description/items."""
    data = json.loads(Path(report).read_text(encoding="utf-8"))
    lists = []
    if kind == "erc":
        for sheet in data.get("sheets", []):
            lists += [(v, sheet.get("path", "/")) for v in sheet.get("violations", [])]
    else:
        for key in ("violations", "unconnected_items", "schematic_parity"):
            lists += [(dict(v, _group=key), None) for v in data.get(key, [])]
    out = []
    for v, sheet in lists:
        if v.get("excluded"):
            continue
        items = [f'{i.get("description", "")} @ ({i.get("pos", {}).get("x", "?")}, {i.get("pos", {}).get("y", "?")})'
                 for i in v.get("items", [])]
        out.append({"kind": kind, "group": v.get("_group", "erc"), "type": v.get("type", "?"),
                    "severity": v.get("severity", "error"), "description": v.get("description", ""),
                    "sheet": sheet, "items": items})
    return out


def summarize(violations):
    sev = Counter(v["severity"] for v in violations)
    by_type = defaultdict(list)
    for v in violations:
        by_type[(v["kind"], v["severity"], v["type"])].append(v)
    return sev, by_type


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", help="project dir, .kicad_pro, .kicad_pcb or .kicad_sch")
    ap.add_argument("--json", action="store_true", help="print a JSON summary instead of text")
    ap.add_argument("--max", type=int, default=5, help="examples shown per violation type (default 5)")
    ap.add_argument("--kicad-cli", help="path to kicad-cli (else KICAD_CLI env, PATH, standard install dirs)")
    a = ap.parse_args()

    pcb, sch, name = resolve_project(a.project)
    cli = find_kicad_cli(a.kicad_cli)
    version = kicad_version(cli)
    keep = Path(tempfile.mkdtemp(prefix=f"kicad-checks-{name}-"))
    violations, reports, notes = [], {}, []

    if sch:
        rep = keep / "erc.json"
        code, out = run(cli, ["sch", "erc", "--format", "json", "--severity-error", "--severity-warning",
                              "-o", str(rep), str(sch)])
        if not rep.exists():
            sys.exit(f"ERC failed (exit {code}):\n{out}")
        reports["erc"] = str(rep)
        violations += load_violations(rep, "erc")
    else:
        notes.append("no schematic found: ERC and schematic parity skipped")

    if pcb:
        rep = keep / "drc.json"
        args = ["pcb", "drc", "--format", "json", "--severity-error", "--severity-warning", "-o", str(rep)]
        if sch:
            args.append("--schematic-parity")
        if version >= (10, 0):
            args.append("--refill-zones")  # in memory only; without --save-board the file is untouched
        elif "(zone" in pcb.read_text(encoding="utf-8"):
            notes.append("KiCad < 10 CLI checks zones as last filled: refill (B) and save in KiCad first")
        code, out = run(cli, args + [str(pcb)])
        if not rep.exists():
            sys.exit(f"DRC failed (exit {code}):\n{out}")
        reports["drc"] = str(rep)
        violations += load_violations(rep, "drc")
        dru = pcb.with_suffix(".kicad_dru")
        notes.append(f"custom rules: {dru.name}" if dru.exists() else
                     "no .kicad_dru custom rules: DRC used only Board Setup constraints")
    else:
        notes.append("no board found: DRC skipped")

    sev, by_type = summarize(violations)
    errors = sev.get("error", 0)
    if a.json:
        print(json.dumps({
            "kicad": f"{version[0]}.{version[1]}", "project": name, "pass": errors == 0,
            "errors": errors, "warnings": sev.get("warning", 0), "reports": reports, "notes": notes,
            "by_type": [{"kind": k, "severity": s, "type": t, "count": len(vs), "description": vs[0]["description"],
                         "examples": [i for v in vs[:a.max] for i in v["items"][:2]]}
                        for (k, s, t), vs in sorted(by_type.items(), key=lambda kv: (kv[0][1] != "error", -len(kv[1])))],
        }, indent=2, ensure_ascii=False))
    else:
        print(f"KiCad {version[0]}.{version[1]}  project: {name}")
        for n in notes:
            print(f"  note: {n}")
        for kind in ("erc", "drc"):
            if kind not in reports:
                continue
            vs = [v for v in violations if v["kind"] == kind]
            c = Counter(v["severity"] for v in vs)
            print(f"\n{kind.upper()}: {c.get('error', 0)} errors, {c.get('warning', 0)} warnings  ({reports[kind]})")
            for (k, s, t), group in sorted(by_type.items(), key=lambda kv: (kv[0][1] != "error", -len(kv[1]))):
                if k != kind:
                    continue
                print(f"  {s:<7} {t} x{len(group)}: {group[0]['description']}")
                for v in group[:a.max]:
                    for item in v["items"][:2]:
                        print(f"            - {item}")
        print(f"\nRESULT: {'PASS' if errors == 0 else 'FAIL'} ({errors} errors, {sev.get('warning', 0)} warnings)")
    sys.exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()

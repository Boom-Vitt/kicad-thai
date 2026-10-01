"""Run inside the official kicad/kicad Docker image against real KiCad demo projects.

    python3 tests/kicad/integration.py demos-src/demos/pic_programmer demos-src/demos/video
"""
import csv
import re
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPORT = ROOT / "skills/kicad-fab-export/scripts/export_fab.py"
CHECKS = ROOT / "skills/kicad-check/scripts/run_checks.py"
RULES = sorted((ROOT / "skills/kicad-check/assets/rules").glob("*.kicad_dru"))
failures = []


def sh(*args):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        failures.append(msg)


print(sh("kicad-cli", "version")[1].strip())
for demo in map(Path, sys.argv[1:]):
    pro = next(demo.glob("*.kicad_pro"))
    print(f"\n== {pro.name}")
    with tempfile.TemporaryDirectory() as t:
        work = Path(t) / demo.name
        shutil.copytree(demo, work)
        pro = work / pro.name
        out = Path(t) / "fab"

        code, so, se = sh(sys.executable, EXPORT, pro, "--fab", "jlcpcb", "-o", out, "--step")
        check(code == 0, f"export_fab exit 0 ({se.strip()[-300:]})")
        if code == 0:
            s = json.loads(so)
            print("  summary:", json.dumps({k: s[k] for k in ("kicad", "copper_layers", "bom_lines", "placements", "warnings") if k in s}, ensure_ascii=False))
            names = zipfile.ZipFile(out / f"{pro.stem}-gerbers.zip").namelist()
            print("  gerbers:", names)
            check(any(n.endswith((".gtl", ".gbr")) for n in names), "copper gerber present")
            check(sum(n.endswith(".drl") for n in names) >= 1, "drill file present")
            check(any("Edge_Cuts" in n or n.endswith(".gm1") for n in names), "board outline present")
            check(len([n for n in names if "_Cu." in n]) == s["copper_layers"], "one gerber per copper layer")
            bom = list(csv.reader(open(out / f"{pro.stem}-bom-jlcpcb.csv", encoding="utf-8")))
            check(bom[0] == ["Comment", "Designator", "Footprint", "LCSC Part #"], "JLC BOM header")
            check(len(bom) > 3 and all(len(r) == 4 for r in bom), f"BOM rows well-formed ({len(bom) - 1} lines)")
            check(not any(re.search(r"\d-[A-Za-z]", r[1]) for r in bom[1:]), "no ref ranges like R1-R3")
            cpl = list(csv.DictReader(open(out / f"{pro.stem}-cpl-jlcpcb.csv", encoding="utf-8")))
            check(len(cpl) > 3, f"CPL has placements ({len(cpl)})")
            check(all(0 <= float(r["Rotation"]) < 360 and r["Layer"] in ("Top", "Bottom") for r in cpl), "CPL rotation/layer normalised")
            check((out / f"{pro.stem}.step").stat().st_size > 1000, "STEP exported")

        code, so, se = sh(sys.executable, CHECKS, pro, "--json")
        check(code in (0, 1), f"run_checks exit 0/1, got {code} ({se.strip()[-300:]})")
        base = None
        if code in (0, 1):
            c = json.loads(so)
            base = c["errors"] + c["warnings"]
            print(f"  checks: {c['errors']} errors, {c['warnings']} warnings, types={[t['type'] for t in c['by_type']][:8]}")

        for rules in RULES:
            dru = pro.with_suffix(".kicad_dru")
            shutil.copy(rules, dru)
            code, so, se = sh("kicad-cli", "pcb", "drc", "--format", "json", "-o", Path(t) / "r.json", pro)
            print(f"    raw kicad-cli output: {(so + se).strip()[-400:]!r}")
            code, so, se = sh(sys.executable, CHECKS, pro, "--json")
            c = json.loads(so) if code in (0, 1) else {}
            check(code in (0, 1), f"{rules.name} loads ({se.strip()[-200:]})")
            if c:
                print(f"    {rules.name}: {c['errors']} errors, {c['warnings']} warnings; notes={c['notes'][-1:]}")
                bad = [t for t in c["by_type"] if t["type"] in ("assertion_failure", "generic_error")]
                check(not bad, f"{rules.name} produced no rule errors {bad[:1]}")
            dru.unlink()

if failures:
    sys.exit(f"\n{len(failures)} failures:\n  " + "\n  ".join(failures))
print("\nall integration checks passed")

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


VERSION = sh("kicad-cli", "version")[1].strip()
MAJOR = int(VERSION.split(".")[0])
print("kicad-cli", VERSION)
if MAJOR < 9:  # creepage constraint is KiCad 9+
    RULES = [r for r in RULES if "mains" not in r.name]
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
            cu = [n for n in names if re.search(r"\.(gtl|gbl|g\d+)$", n)]
            expected = {"pic_programmer": 2, "video": 4}[demo.name]  # known, not derived from the script
            check(len(cu) == expected == s["copper_layers"], f"{expected} copper gerbers {cu}")
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

        # negative control: KiCad ignores a broken rules file silently; run_checks must catch it (exit 2)
        dru = pro.with_suffix(".kicad_dru")
        dru.write_text('(version 1)\n(rule "bad" (constraint no_such_constraint (min 1mm)))\n')
        code, so, se = sh(sys.executable, CHECKS, pro, "--json")
        check(code == 2 and "did NOT load" in se, f"broken rules file rejected (exit {code})")

        for rules in RULES:
            shutil.copy(rules, dru)
            code, so, se = sh(sys.executable, CHECKS, pro, "--json")
            c = json.loads(so) if code in (0, 1) else {}
            check(code in (0, 1) and "loaded, verified" in " ".join(c.get("notes", [])),
                  f"{rules.name} loads in KiCad {VERSION} ({se.strip()[-200:]})")
            if c:
                print(f"    {rules.name}: {c['errors']} errors, {c['warnings']} warnings")
                print("      top:", [(x["type"], x["count"], x["description"][:90]) for x in c["by_type"][:3]])
        dru.unlink(missing_ok=True)

# The mains add-on must actually FIRE, not just load: AC_L track 1.5 mm from +3V3 and from AC_N.
if MAJOR >= 9:
    print("\n== mains add-on on tests/kicad/mains_creepage")
    with tempfile.TemporaryDirectory() as t:
        for ext in (".kicad_pcb", ".kicad_pro"):
            shutil.copy(ROOT / f"tests/kicad/mains_creepage{ext}", Path(t) / f"mains_creepage{ext}")
        shutil.copy(next(r for r in RULES if "mains" in r.name), Path(t) / "mains_creepage.kicad_dru")
        code, so, se = sh(sys.executable, CHECKS, Path(t) / "mains_creepage.kicad_pcb", "--json")
        descs = Path(json.loads(so)["reports"]["drc"]).read_text() if code in (0, 1) else se
        print("  rules hit:", sorted(set(re.findall(r"rule '([^']+)'", descs))))
        check(code == 1, f"mains board fails DRC (exit {code})")
        check("Mains to low voltage: reinforced clearance" in descs, "3.0 mm mains-to-LV clearance enforced")
        check("Mains to low voltage: reinforced creepage" in descs, "5.0 mm mains-to-LV creepage enforced")
        check("Mains functional (L-N): creepage" in descs, "2.5 mm L-N creepage enforced")

if failures:
    sys.exit(f"\n{len(failures)} failures:\n  " + "\n  ".join(failures))
print("\nall integration checks passed")

"""Offline tests: fake kicad-cli + fixtures. Run: python3 tests/test_scripts.py"""
import csv
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "fixtures"
EXPORT = ROOT / "skills" / "kicad-fab-export" / "scripts" / "export_fab.py"
CHECKS = ROOT / "skills" / "kicad-check" / "scripts" / "run_checks.py"
FAKE = ROOT / "tests" / "fake_kicad_cli.py"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(script, *args, **env):
    e = dict(os.environ, KICAD_CLI=str(FAKE), **env)
    return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True, env=e)


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


class ExportFab(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        self.log = self.out / "argv.log"

    def tearDown(self):
        self.tmp.cleanup()

    def export(self, *args):
        r = run(EXPORT, FIX / "demo.kicad_pro", "-o", self.out, *args, FAKE_LOG=str(self.log))
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_copper_layers_from_layer_table_only(self):
        mod = load(EXPORT)
        self.assertEqual(mod.copper_layers((FIX / "demo.kicad_pcb").read_text()), ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"])
        self.assertEqual(mod.copper_layers('(layers (0 "F.Cu" signal) (31 "B.Cu" signal))'), ["F.Cu", "B.Cu"])
        # KiCad 10 renumbered layers (B.Cu=2, In1.Cu=4); names still drive the order
        self.assertEqual(mod.copper_layers('(layers (0 "F.Cu" signal) (2 "B.Cu" signal) (4 "In1.Cu" signal))'),
                         ["F.Cu", "In1.Cu", "B.Cu"])

    def test_jlcpcb_package(self):
        s = self.export("--fab", "jlcpcb", "--rot", "SOT-23*=180", "--step")
        self.assertEqual(s["copper_layers"], 4)
        names = zipfile.ZipFile(self.out / "demo-gerbers.zip").namelist()
        for want in ("demo-F_Cu.gbr", "demo-In2_Cu.gbr", "demo-B_Cu.gbr", "demo-Edge_Cuts.gbr", "demo.drl"):
            self.assertIn(want, names)

        bom = read_csv(self.out / "demo-bom-jlcpcb.csv")
        self.assertEqual(bom[0], ["Comment", "Designator", "Footprint", "LCSC Part #"])
        rows = {r[1]: r for r in bom[1:]}
        self.assertEqual(rows["C1,C2,C5"], ["100nF", "C1,C2,C5", "C_0402_1005Metric", "C1525"])  # merged rows
        self.assertEqual(rows["C10"][3], "C15850")      # LCSC from "LCSC Part #" field
        self.assertEqual(rows["U1"][3], "C7950")        # multi-unit symbol listed once
        self.assertEqual(rows["R1,R2,R10"][3], "")      # natural ref sort
        self.assertNotIn("R9", " ".join(rows))          # DNP dropped
        self.assertFalse(any(k.startswith("#") for k in rows))  # power symbols dropped
        self.assertEqual(s["placements"], 8)
        self.assertTrue(any("no LCSC" in w for w in s["warnings"]))

        cpl = read_csv(self.out / "demo-cpl-jlcpcb.csv")
        self.assertEqual(cpl[0], ["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
        by = {r[0]: r for r in cpl[1:]}
        self.assertEqual(by["C1"][5], "270")            # -90 normalised to 0..360
        self.assertEqual(by["Q1"][5], "0")              # 180 + 180 rotation fix
        self.assertEqual(by["U1"][6], "Bottom")
        self.assertTrue((self.out / "demo.step").exists())

        gerber_call = next(c for c in self.calls() if c[:3] == ["pcb", "export", "gerbers"])
        self.assertIn("--subtract-soldermask", gerber_call)
        bom_call = next(c for c in self.calls() if c[:3] == ["sch", "export", "bom"])
        self.assertEqual(bom_call[bom_call.index("--ref-range-delimiter") + 1], "")  # no "R1-R3" ranges

    def test_pcbway_bom(self):
        self.export("--fab", "pcbway")
        bom = read_csv(self.out / "demo-bom-pcbway.csv")
        self.assertEqual(bom[0][:3], ["Item #", "Designator", "Qty"])
        u1 = next(r for r in bom if r[1] == "U1")
        self.assertEqual(u1[2:5], ["1", "TI", "LM358DR"])

    def test_bare_board(self):
        s = self.export("--no-assembly")
        self.assertEqual([Path(f).name for f in s["files"]], ["demo-gerbers.zip"])
        self.assertFalse(any(c[:2] == ["sch", "export"] for c in self.calls()))

    def test_bad_rot_spec(self):
        r = run(EXPORT, FIX / "demo.kicad_pro", "-o", self.out, "--rot", "SOT-23")
        self.assertNotEqual(r.returncode, 0)


class RunChecks(unittest.TestCase):
    def test_violations_fail(self):
        r = run(CHECKS, FIX / "demo.kicad_pro", "--json")
        self.assertEqual(r.returncode, 1, r.stderr)
        s = json.loads(r.stdout)
        self.assertEqual((s["errors"], s["warnings"]), (3, 2))   # excluded ERC item ignored
        types = {t["type"]: t["count"] for t in s["by_type"]}
        self.assertEqual(types, {"pin_not_connected": 1, "clearance": 1, "unconnected_items": 1,
                                 "label_dangling": 1, "silk_over_copper": 1})
        self.assertEqual(s["by_type"][0]["severity"], "error")

    def test_text_report_and_parity_flag(self):
        with tempfile.TemporaryDirectory() as t:
            log = Path(t) / "argv.log"
            r = run(CHECKS, FIX / "demo.kicad_pro", FAKE_LOG=str(log))
            drc = next(json.loads(l) for l in log.read_text().splitlines() if json.loads(l)[:2] == ["pcb", "drc"])
        self.assertIn("--schematic-parity", drc)
        self.assertIn("RESULT: FAIL (3 errors, 2 warnings)", r.stdout)
        self.assertIn("clearance x1", r.stdout)

    def test_clean_passes(self):
        r = run(CHECKS, FIX, FAKE_ERC="erc-clean.json", FAKE_DRC="drc-clean.json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESULT: PASS", r.stdout)


class Repo(unittest.TestCase):
    def test_shared_helpers_identical(self):
        block = lambda p: re.sub(r"^# --- shared with .*\n", "", re.search(r"# --- shared with.*?# --- end shared ---",
                                                                             p.read_text(), re.S).group(0))
        self.assertEqual(block(EXPORT), block(CHECKS))

    def test_skill_frontmatter(self):
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skills), 5)
        for md in skills:
            text = md.read_text(encoding="utf-8")
            fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
            self.assertTrue(fm, md)
            name = re.search(r"^name: (.+)$", fm.group(1), re.M).group(1).strip()
            desc = re.search(r"^description: (.+)$", fm.group(1), re.M).group(1).strip()
            self.assertEqual(name, md.parent.name)
            self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertLessEqual(len(name), 64)
            self.assertLessEqual(len(desc), 1024, md)
            self.assertLess(len(text.splitlines()), 500, md)
            for ref in re.findall(r"\]\(((?:references|scripts|assets)/[^)#]+)\)", text):
                self.assertTrue((md.parent / ref).exists(), f"{md}: broken link {ref}")

    def test_manifests_agree(self):
        files = [".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json",
                 "gemini-extension.json"]
        versions = {f: json.loads((ROOT / f).read_text())["version"] for f in files}
        mk = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        versions["marketplace"] = mk["plugins"][0]["version"]
        self.assertEqual(len(set(versions.values())), 1, versions)
        json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())

    def test_dru_presets_parse(self):
        presets = sorted((ROOT / "skills/kicad-check/assets/rules").glob("*.kicad_dru"))
        self.assertGreaterEqual(len(presets), 3)
        for p in presets:
            body = "\n".join(l for l in p.read_text().splitlines() if not l.lstrip().startswith("#"))
            self.assertRegex(body, r"^\(version 1\)", p)
            depth = 0
            for ch in body:
                depth += {"(": 1, ")": -1}.get(ch, 0)
                self.assertGreaterEqual(depth, 0, p)
            self.assertEqual(depth, 0, p)


if __name__ == "__main__":
    unittest.main(verbosity=2)

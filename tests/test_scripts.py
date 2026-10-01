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
        cu = lambda text: [c for c, _ in load(EXPORT).copper_layers(text)]
        self.assertEqual(cu((FIX / "demo.kicad_pcb").read_text()), ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"])
        self.assertEqual(cu('(layers (0 "F.Cu" signal) (31 "B.Cu" signal))'), ["F.Cu", "B.Cu"])
        # KiCad 9+ renumbered layers (B.Cu=2, In1.Cu=4); names still drive the order
        self.assertEqual(cu('(layers (0 "F.Cu" signal) (2 "B.Cu" signal) (4 "In1.Cu" signal))'),
                         ["F.Cu", "In1.Cu", "B.Cu"])

    def test_renamed_copper_layers_still_exported(self):
        # KiCad's own pic_programmer demo names its copper "top_layer"/"bottom_layer";
        # kicad-cli 8.0.9/9.0.9 silently dropped them when asked for F.Cu/B.Cu.
        mod = load(EXPORT)
        board = '(layers (0 "F.Cu" signal "top_layer") (2 "B.Cu" signal "bottom_layer") (5 "F.SilkS" user "F.Silkscreen"))'
        self.assertEqual(mod.copper_layers(board), [("F.Cu", "top_layer"), ("B.Cu", "bottom_layer")])
        self.assertEqual(mod.layer_args(mod.copper_layers(board)), ["F.Cu", "top_layer", "B.Cu", "bottom_layer"])
        with tempfile.TemporaryDirectory() as t:
            proj = Path(t) / "renamed.kicad_pcb"
            proj.write_text((FIX / "demo.kicad_pcb").read_text().replace('(0 "F.Cu" signal)', '(0 "F.Cu" signal "top_layer")'))
            r = run(EXPORT, proj, "-o", Path(t) / "fab", "--no-assembly")
            self.assertEqual(r.returncode, 0, r.stderr)
            names = zipfile.ZipFile(Path(t) / "fab" / "renamed-gerbers.zip").namelist()
            self.assertIn("renamed-top_layer.gtl", names)

    def test_missing_copper_fails_loudly(self):
        mod = load(EXPORT)
        with tempfile.TemporaryDirectory() as t:
            for n in ("b-F_Cu.gtl", "b-Edge_Cuts.gm1", "b-PTH.drl"):
                (Path(t) / n).write_text("x")
            mod.verify_gerbers(t, 1)
            with self.assertRaises(SystemExit):
                mod.verify_gerbers(t, 2)

    def test_jlcpcb_package(self):
        s = self.export("--fab", "jlcpcb", "--rot", "SOT-23*=180", "--step")
        self.assertEqual(s["copper_layers"], 4)
        names = zipfile.ZipFile(self.out / "demo-gerbers.zip").namelist()
        for want in ("demo-F_Cu.gtl", "demo-In2_Cu.g2", "demo-B_Cu.gbl", "demo-Edge_Cuts.gm1", "demo.drl"):
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

    def test_rot_fix_is_mirrored_on_bottom(self):
        self.export("--rot", "SOIC*=90")
        cpl = {r[0]: r for r in read_csv(self.out / "demo-cpl-jlcpcb.csv")[1:]}
        self.assertEqual((cpl["U1"][5], cpl["U1"][6]), ("270", "Bottom"))  # 0 - 90 on the bottom side

    def test_bom_vs_board_cross_check(self):
        s = self.export()
        self.assertTrue(any("not on the board" in w and "C10" in w for w in s["warnings"]), s["warnings"])
        self.assertFalse(any("footprint differs" in w for w in s["warnings"]))
        rows = [{"refs": ["R1"], "footprint": "Resistor_SMD:R_0805_2012Metric"}]
        self.assertIn("footprint differs", load(EXPORT).cross_check(rows, [{"Ref": "R1", "Package": "R_0603_1608Metric"}])[0])

    def test_unannotated_parts_refused(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "bom.csv").write_text('"Reference","Value","Footprint"\n"R?","10k","R_0603"\n')
            fake_fix = FIX / "bom-unannotated.csv"
            fake_fix.write_text((Path(t) / "bom.csv").read_text())
            try:
                r = run(EXPORT, FIX / "demo.kicad_pro", "-o", self.out, FAKE_BOM="bom-unannotated.csv")
            finally:
                fake_fix.unlink()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Unannotated", r.stderr)

    def test_thai_text_warning_on_kicad8(self):
        with tempfile.TemporaryDirectory() as t:
            board = Path(t) / "th.kicad_pcb"
            board.write_text((FIX / "demo.kicad_pcb").read_text().replace("(footprint", '(gr_text "ลายวงจร" (at 1 1 0) (layer "F.SilkS"))\n\t(footprint', 1))
            r8 = run(EXPORT, board, "-o", Path(t) / "f8", "--no-assembly", FAKE_VERSION="8.0.9")
            r9 = run(EXPORT, board, "-o", Path(t) / "f9", "--no-assembly", FAKE_VERSION="9.0.9")
        self.assertTrue(any("drops Thai vowels" in w for w in json.loads(r8.stdout)["warnings"]))
        self.assertFalse(any("drops Thai vowels" in w for w in json.loads(r9.stdout)["warnings"]))

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

    def test_custom_rules_verified_or_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            for f in ("demo.kicad_pcb", "demo.kicad_pro"):
                (Path(t) / f).write_text((FIX / f).read_text())
            dru = Path(t) / "demo.kicad_dru"
            dru.write_text("(version 1)\n(rule ok (constraint track_width (min 0.1mm)))\n")
            ok = run(CHECKS, Path(t) / "demo.kicad_pro", "--json", FAKE_DRC="drc-clean.json")
            dru.write_text("(version 1)\n(rule bad (constraint no_such_constraint (min 1mm)))\n")
            bad = run(CHECKS, Path(t) / "demo.kicad_pro", "--json", FAKE_DRC="drc-clean.json")
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("loaded, verified", " ".join(json.loads(ok.stdout)["notes"]))
        self.assertEqual(bad.returncode, 2)
        self.assertIn("did NOT load", bad.stderr)

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

    def test_mains_rules_copy_in_sync(self):
        addon = (ROOT / "skills/kicad-check/assets/rules/mains-220v-addon.kicad_dru").read_text()
        doc = (ROOT / "skills/thai-pcb-compliance/references/mains-pcb.md").read_text()
        self.assertIn("(rule" + addon.split("\n(rule", 1)[1].rstrip(), doc)

    def test_fab_presets_never_override_netclass_clearance(self):
        # a custom clearance/edge rule beats net classes: a 3 mm Mains class would drop to the fab minimum
        for p in (ROOT / "skills/kicad-check/assets/rules").glob("*.kicad_dru"):
            if "mains" in p.name:
                continue
            body = "\n".join(l for l in p.read_text().splitlines() if not l.lstrip().startswith("#"))
            self.assertNotRegex(body, r"\(constraint (clearance|edge_clearance) ", p.name)

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

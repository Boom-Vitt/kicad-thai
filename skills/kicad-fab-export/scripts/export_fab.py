#!/usr/bin/env python3
"""Export a KiCad 8/9/10 board as a fab-ready package. Stdlib only, any OS.

    python3 export_fab.py board.kicad_pro --fab jlcpcb -o fab/
    python3 export_fab.py . --fab pcbway --no-assembly
    python3 export_fab.py board.kicad_pro --fab jlcpcb --rot "SOT-23*=180" --rot "*QFN*=90"

Writes into the output dir:
    <name>-gerbers.zip     Gerbers + Excellon drill + drill map (upload this to the fab)
    <name>-bom-<fab>.csv   BOM in the fab's column format (needs a .kicad_sch)
    <name>-cpl-<fab>.csv   pick-and-place / centroid file
    <name>.step            only with --step
and prints a JSON summary. Never touches the KiCad source files.
"""
import argparse
import csv
import fnmatch
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# --- shared with kicad-check/scripts/run_checks.py (kept identical; tests enforce it) ---


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


def must(cli, args):
    code, out = run(cli, args)
    if code != 0:
        sys.exit(f"kicad-cli {' '.join(args[:3])} failed (exit {code}):\n{out}")
    return out


def copper_layers(pcb_text):
    """Copper layers from the board's layer table, ordered F.Cu, In1..InN, B.Cu.

    Returns (canonical, user_name_or_None) pairs. Layer-table rows look like
    `(0 "F.Cu" signal "top_layer")`; pad layer lists have no leading number.
    """
    rows = re.findall(r'\(\s*\d+\s+"((?:F|B|In\d+)\.Cu)"\s+\w+(?:\s+"([^"]*)")?\s*\)', pcb_text)
    names = dict(rows)
    inner = sorted((n for n in names if n.startswith("In")), key=lambda n: int(n[2:-3]))
    order = [n for n in ("F.Cu",) if n in names] + inner + [n for n in ("B.Cu",) if n in names]
    return [(n, names[n] or None) for n in order]


def layer_args(copper):
    """kicad-cli 8/9 silently skips a renamed copper layer given by its canonical
    name, so pass the user name too (plotting a layer twice just rewrites one file)."""
    out = []
    for canonical, user in copper:
        out += [canonical] + ([user] if user and user != canonical else [])
    return out


def verify_gerbers(gdir, n_copper):
    """Fail loudly rather than ship a fab zip that is missing copper or the outline."""
    names = [f.name for f in Path(gdir).iterdir()]
    cu = [n for n in names if re.search(r"\.(gtl|gbl|g\d+)$", n)]
    problems = []
    if len(cu) != n_copper:
        problems.append(f"expected {n_copper} copper Gerbers, got {len(cu)}: {sorted(cu)}")
    if not any(n.endswith(".gm1") for n in names):
        problems.append("no board outline (Edge.Cuts .gm1) Gerber")
    if not any(n.endswith(".drl") for n in names):
        problems.append("no Excellon drill file")
    if problems:
        sys.exit("Gerber export incomplete, NOT safe to send to a fab:\n  " + "\n  ".join(problems))


def export_gerbers(cli, pcb, layers, gdir, version):
    # Explicit --layers (not --board-plot-params) so every copper layer is always included.
    args = ["pcb", "export", "gerbers", "-o", str(gdir) + os.sep,
            "--layers", ",".join(layers), "--subtract-soldermask"]
    if version >= (10, 0):
        args.append("--check-zones")  # refill stale zones before plotting (KiCad 10+)
    must(cli, args + [str(pcb)])
    # JLCPCB's KiCad guide: Excellon, mm, decimal, absolute origin, separate PTH/NPTH files.
    must(cli, ["pcb", "export", "drill", "-o", str(gdir) + os.sep,
               "--format", "excellon", "--excellon-units", "mm",
               "--excellon-zeros-format", "decimal", "--excellon-separate-th",
               "--generate-map", "--map-format", "gerberx2", str(pcb)])


def zip_dir(src, dest):
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(Path(src).iterdir()):
            z.write(f, f.name)


def strip_lib(footprint):
    """'Resistor_SMD:R_0603_1608Metric' -> 'R_0603_1608Metric'."""
    return footprint.split(":", 1)[-1]


LCSC_FIELDS = ("LCSC", "LCSC Part", "LCSC Part #", "LCSC#", "JLCPCB Part #", "JLC")
BOM_FIELDS = ["Reference", "Value", "Footprint", "${DNP}", "Manufacturer", "MPN", *LCSC_FIELDS]


def read_symbols(cli, sch, tmp):
    """One dict per placed symbol (multi-unit parts merged), DNP / power / excluded parts dropped."""
    out = Path(tmp) / "raw-bom.csv"
    must(cli, ["sch", "export", "bom", "-o", str(out),
               "--fields", ",".join(BOM_FIELDS), "--labels", ",".join(BOM_FIELDS),
               "--ref-range-delimiter", "", "--string-delimiter", '"', "--exclude-dnp", str(sch)])
    seen, parts = set(), []
    with open(out, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            for ref in re.split(r"[,\s]+", row.get("Reference", "").strip()):
                if not ref or ref.startswith("#") or ref in seen or row.get("${DNP}", "").strip():
                    continue
                seen.add(ref)
                lcsc = next((row[k].strip() for k in LCSC_FIELDS if row.get(k, "").strip()), "")
                parts.append({"ref": ref, "value": row.get("Value", ""), "footprint": row.get("Footprint", ""),
                              "mfr": row.get("Manufacturer", ""), "mpn": row.get("MPN", ""), "lcsc": lcsc})
    return parts


def ref_key(ref):
    m = re.match(r"([A-Za-z_]*)(\d*)", ref)
    return (m.group(1), int(m.group(2) or 0), ref)


def group_parts(parts):
    groups = {}
    for p in parts:
        groups.setdefault((p["value"], p["footprint"], p["lcsc"], p["mpn"]), []).append(p)
    rows = []
    for (value, fp, lcsc, mpn), ps in groups.items():
        refs = sorted((p["ref"] for p in ps), key=ref_key)
        rows.append({"refs": refs, "value": value, "footprint": fp, "lcsc": lcsc,
                     "mpn": mpn, "mfr": ps[0]["mfr"]})
    return sorted(rows, key=lambda r: ref_key(r["refs"][0]))


def write_bom(rows, fab, dest):
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if fab == "jlcpcb":
            w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
            for r in rows:
                w.writerow([r["value"], ",".join(r["refs"]), strip_lib(r["footprint"]), r["lcsc"]])
        elif fab == "pcbway":
            w.writerow(["Item #", "Designator", "Qty", "Manufacturer", "Mfg Part #",
                        "Description / Value", "Package/Footprint", "Type", "Your Instructions / Notes"])
            for i, r in enumerate(rows, 1):
                w.writerow([i, ",".join(r["refs"]), len(r["refs"]), r["mfr"], r["mpn"], r["value"],
                            strip_lib(r["footprint"]), "", ""])
        else:
            w.writerow(["Designator", "Qty", "Value", "Footprint", "Manufacturer", "MPN", "LCSC"])
            for r in rows:
                w.writerow([",".join(r["refs"]), len(r["refs"]), r["value"], r["footprint"],
                            r["mfr"], r["mpn"], r["lcsc"]])


def parse_rot_rules(specs):
    rules = []
    for s in specs:
        pattern, _, deg = s.rpartition("=")
        if not pattern:
            sys.exit(f"--rot expects PATTERN=DEGREES, got {s!r}")
        rules.append((pattern, float(deg)))
    return rules


def read_positions(cli, pcb, tmp, version):
    out = Path(tmp) / "raw-pos.csv"
    args = ["pcb", "export", "pos", "-o", str(out), "--side", "both",
            "--format", "csv", "--units", "mm"]
    if version >= (8, 0):
        args.append("--exclude-dnp")
    must(cli, args + [str(pcb)])
    with open(out, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_cpl(positions, rot_rules, dest):
    """KiCad pos CSV (Ref,Val,Package,PosX,PosY,Rot,Side) -> centroid columns JLCPCB and PCBWay both accept."""
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
        for p in positions:
            rot = float(p["Rot"])
            for pattern, deg in rot_rules:
                if fnmatch.fnmatch(p["Package"], pattern):
                    rot += deg
                    break
            rot %= 360
            w.writerow([p["Ref"], p["Val"], p["Package"], f'{float(p["PosX"]):.4f}', f'{float(p["PosY"]):.4f}',
                        f"{rot:g}", "Top" if p["Side"].lower().startswith("top") else "Bottom"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", help="project dir, .kicad_pro or .kicad_pcb")
    ap.add_argument("--fab", choices=["jlcpcb", "pcbway", "generic"], default="jlcpcb")
    ap.add_argument("-o", "--out", default="fab", help="output dir (default: ./fab next to the project)")
    ap.add_argument("--no-assembly", action="store_true", help="bare PCB only: skip BOM and CPL")
    ap.add_argument("--step", action="store_true", help="also export a STEP 3D model")
    ap.add_argument("--rot", action="append", default=[], metavar="PATTERN=DEG",
                    help="add DEG to CPL rotation for packages matching glob PATTERN (first match wins)")
    ap.add_argument("--kicad-cli", help="path to kicad-cli (else KICAD_CLI env, PATH, standard install dirs)")
    a = ap.parse_args()

    pcb, sch, name = resolve_project(a.project)
    if not pcb:
        sys.exit("No .kicad_pcb found: lay out the board before exporting fab files.")
    cli = find_kicad_cli(a.kicad_cli)
    version = kicad_version(cli)
    if version < (8, 0):
        print(f"warning: kicad-cli {version[0]}.{version[1]} detected; this script targets KiCad 8+", file=sys.stderr)
    out = Path(a.out) if os.path.isabs(a.out) else pcb.parent / a.out
    out.mkdir(parents=True, exist_ok=True)

    pcb_text = pcb.read_text(encoding="utf-8")
    cu = copper_layers(pcb_text)
    layers = layer_args(cu) + ["F.Paste", "B.Paste", "F.SilkS", "B.SilkS", "F.Mask", "B.Mask", "Edge.Cuts"]
    summary = {"kicad": f"{version[0]}.{version[1]}", "fab": a.fab, "copper_layers": len(cu), "files": [],
               "warnings": []}

    with tempfile.TemporaryDirectory() as tmp:
        gdir = Path(tmp) / "gerbers"
        gdir.mkdir()
        export_gerbers(cli, pcb, layers, gdir, version)
        verify_gerbers(gdir, len(cu))
        if version < (10, 0) and "(zone" in pcb_text:
            summary["warnings"].append("KiCad < 10 plots zones as last saved: refill zones (B) and save in KiCad first")
        gzip = out / f"{name}-gerbers.zip"
        zip_dir(gdir, gzip)
        summary["gerber_files"] = sorted(f.name for f in gdir.iterdir())
        summary["files"].append(str(gzip))

        if not a.no_assembly:
            if sch:
                rows = group_parts(read_symbols(cli, sch, tmp))
                bom = out / f"{name}-bom-{a.fab}.csv"
                write_bom(rows, a.fab, bom)
                summary["files"].append(str(bom))
                summary["bom_lines"] = len(rows)
                summary["placements"] = sum(len(r["refs"]) for r in rows)
                if a.fab == "jlcpcb":
                    missing = [",".join(r["refs"]) for r in rows if not r["lcsc"]]
                    if missing:
                        summary["warnings"].append(f"{len(missing)} BOM lines have no LCSC part number: {missing[:10]}")
            else:
                summary["warnings"].append(f"no {name}.kicad_sch next to the board: BOM skipped")
            cpl = out / f"{name}-cpl-{a.fab}.csv"
            write_cpl(read_positions(cli, pcb, tmp, version), parse_rot_rules(a.rot), cpl)
            summary["files"].append(str(cpl))

    if a.step:
        step = out / f"{name}.step"
        code, log = run(cli, ["pcb", "export", "step", "-o", str(step), "--subst-models", "--force", str(pcb)])
        if not step.exists():
            sys.exit(f"STEP export failed (exit {code}):\n{log}")
        missing = log.count("File not found")
        if missing:  # KiCad 10 exits non-zero when 3D models are missing but still writes the board
            summary["warnings"].append(f"STEP written without {missing} missing 3D models (install KiCad's 3D library)")
        summary["files"].append(str(step))

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

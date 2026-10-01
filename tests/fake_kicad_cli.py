#!/usr/bin/env python3
"""Stand-in for kicad-cli so tests run without KiCad. Logs argv, writes fixture outputs."""
import json
import os
import shutil
import sys
from pathlib import Path

FIX = Path(__file__).parent / "fixtures"
argv = sys.argv[1:]
if os.environ.get("FAKE_LOG"):
    with open(os.environ["FAKE_LOG"], "a") as f:
        f.write(json.dumps(argv) + "\n")


def opt(name):
    return argv[argv.index(name) + 1]


cmd = tuple(a for a in argv[:3] if not a.startswith("-"))
if argv[:1] == ["version"]:
    print(os.environ.get("FAKE_VERSION", "9.0.4"))
elif cmd == ("pcb", "export", "gerbers"):
    out, stem = Path(opt("-o")), Path(argv[-1]).stem
    for layer in opt("--layers").split(","):
        (out / f"{stem}-{layer.replace('.', '_')}.gbr").write_text("G04 fake*\nM02*\n")
elif cmd == ("pcb", "export", "drill"):
    out, stem = Path(opt("-o")), Path(argv[-1]).stem
    (out / f"{stem}.drl").write_text("M48\nM30\n")
    (out / f"{stem}-drl_map.gbr").write_text("G04 fake*\nM02*\n")
elif cmd == ("sch", "export", "bom"):
    shutil.copy(FIX / "bom.csv", opt("-o"))
elif cmd == ("pcb", "export", "pos"):
    shutil.copy(FIX / "pos.csv", opt("-o"))
elif cmd == ("pcb", "export", "step"):
    Path(opt("-o")).write_text("ISO-10303-21;\n")
elif cmd == ("sch", "erc"):
    shutil.copy(FIX / os.environ.get("FAKE_ERC", "erc.json"), opt("-o"))
elif cmd == ("pcb", "drc"):
    shutil.copy(FIX / os.environ.get("FAKE_DRC", "drc.json"), opt("-o"))
else:
    sys.exit(f"fake kicad-cli: unsupported {argv}")

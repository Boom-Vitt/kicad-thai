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
    import re
    out, board = Path(opt("-o")), Path(argv[-1])
    renamed = dict(re.findall(r'\(\s*\d+\s+"([^"]+)"\s+\w+\s+"([^"]+)"\s*\)', board.read_text()))
    by_user = {v: k for k, v in renamed.items()}
    ext = {"F.Cu": "gtl", "B.Cu": "gbl", "F.Paste": "gtp", "B.Paste": "gbp", "F.SilkS": "gto", "B.SilkS": "gbo",
           "F.Mask": "gts", "B.Mask": "gbs", "Edge.Cuts": "gm1"}
    for name in opt("--layers").split(","):
        canonical = by_user.get(name, name)
        if name == canonical and canonical.endswith(".Cu") and canonical in renamed:
            continue  # real kicad-cli 8/9 silently skips a renamed copper layer given by canonical name
        e = ext.get(canonical) or "g" + canonical[2:-3]
        (out / f"{board.stem}-{renamed.get(canonical, canonical).replace('.', '_')}.{e}").write_text("G04 fake*\nM02*\n")
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

---
name: kicad-fab-export
description: Generate a fab-ready manufacturing package from a KiCad 8/9/10 board in one command — Gerber + Excellon drill zip, BOM and pick-and-place (CPL/centroid) in JLCPCB or PCBWay format, optional STEP — and walk through the order settings. Use when the user wants to order or manufacture a PCB or PCBA, export Gerbers, make a BOM or CPL, or says ส่งโรงงาน, สั่งผลิต PCB, ทำไฟล์ Gerber, ไฟล์ส่ง JLCPCB, ยิง SMT, ประกอบบอร์ด, ทำ BOM, ไฟล์ตำแหน่งชิ้นส่วน, even if they don't name kicad-cli.
---

# KiCad fab export (Gerber, drill, BOM, CPL)

Reply in Thai when the user writes Thai. Run the checks first: exporting a
board that fails DRC just ships the mistake. If `kicad-check` hasn't passed
with the fab's preset in this session, run it before exporting.

## One command

```bash
python3 "<skill>/scripts/export_fab.py" path/to/project.kicad_pro --fab jlcpcb
python3 "<skill>/scripts/export_fab.py" path/to/project.kicad_pro --fab pcbway
python3 "<skill>/scripts/export_fab.py" path/to/project.kicad_pro --fab generic --no-assembly
```

Output goes to `fab/` next to the project (`-o DIR` to change) and a JSON
summary is printed. Source `.kicad_*` files are never modified.

| File | What it is |
|---|---|
| `<name>-gerbers.zip` | all copper layers found in the board + paste, silk, mask, Edge.Cuts, Excellon drill (mm, decimal) + drill map — upload this |
| `<name>-bom-<fab>.csv` | grouped BOM. JLCPCB: `Comment, Designator, Footprint, LCSC Part #`. PCBWay: their quote template columns |
| `<name>-cpl-<fab>.csv` | `Designator, Val, Package, Mid X, Mid Y, Rotation, Layer` in mm, rotation 0–359 |
| `<name>.step` | with `--step`, for the mechanical/enclosure designer |

Options: `--no-assembly` (bare PCB, no BOM/CPL), `--step`,
`--rot PATTERN=DEG` (see below), `--kicad-cli PATH`.

## BOM fields: set them in the schematic

The BOM comes from symbol fields, so fix data in the schematic, not in the CSV:

- **JLCPCB assembly** needs an LCSC part number (`C` + digits) per line. The script
  reads the first non-empty of these fields: `LCSC`, `LCSC Part`, `LCSC Part #`,
  `LCSC#`, `JLCPCB Part #`, `JLC`. Lines without one are listed in `warnings`.
- **PCBWay / Thai EMS** quote from `Manufacturer` + `MPN`; add both.
- Parts that must not be fitted: set **Do not populate (DNP)** in symbol
  properties. DNP parts, power symbols and "exclude from BOM" parts are left out.
- Identical parts are grouped by Value + Footprint + part number, designators
  listed in full (`R1,R2,R10`) because fabs can't parse ranges like `R1-R3`.

## CPL rotations (the classic JLCPCB problem)

KiCad's footprint zero orientation and the assembler's library don't always
agree (common with SOT-23, SOT-223, QFN, some diodes and connectors). Export, upload,
and check the fab's placement preview. For every part shown rotated wrong, add
a correction and export again:

```bash
python3 "<skill>/scripts/export_fab.py" board.kicad_pro --fab jlcpcb --rot "SOT-23*=180" --rot "*QFN*=90"
```

`PATTERN` is a glob on the footprint name (Package column), first match wins,
and the degrees are added to KiCad's rotation. Write down the corrections that worked
in the project README so the next order uses them. Bottom-side parts are
the other usual suspect: check them in the preview separately.

## Ordering

Order-form settings and fab-specific notes for JLCPCB, PCBWay and Thai local
fabs: [references/fab-houses.md](references/fab-houses.md). Before the user
pays, summarise: layers, size, thickness, finish, quantity, assembly side(s),
number of BOM lines without part numbers, and anything that changes price
(castellated holes, impedance control, ENIG, odd colours).

For where to manufacture in Thailand, import VAT on parcels from China and
local parts sources, use **thai-pcb-sourcing**.

## Manual commands (if the script can't be used)

```bash
kicad-cli pcb export gerbers -o fab/gerbers/ --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask board.kicad_pcb
kicad-cli pcb export drill -o fab/gerbers/ --format excellon --excellon-units mm --excellon-zeros-format decimal --generate-map --map-format gerberx2 board.kicad_pcb
kicad-cli sch export bom -o fab/bom.csv --fields "Reference,Value,Footprint,LCSC" --labels "Designator,Comment,Footprint,LCSC Part #" --group-by "Value,Footprint,LCSC" --ref-range-delimiter "" --exclude-dnp board.kicad_sch
kicad-cli pcb export pos -o fab/pos.csv --side both --format csv --units mm --exclude-dnp board.kicad_pcb
```

Add `In1.Cu,In2.Cu,…` to `--layers` for multilayer boards.

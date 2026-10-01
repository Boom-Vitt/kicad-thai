# Ordering notes per fab (checked 2026-10-02)

Capabilities change; the DRC presets in `kicad-check/assets/rules/` carry the
numbers and source links. This file covers what to upload and which order
options matter.

## JLCPCB

Sources: [Gerber/drill in KiCad 9](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9),
[BOM + centroid from KiCad](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad),
[pick-and-place file](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly),
[capabilities](https://jlcpcb.com/capabilities/pcb-capabilities).

- Upload `<name>-gerbers.zip`. Our export matches JLCPCB's KiCad guide:
  Protel extensions, X2 + netlist attributes, Excellon mm decimal, absolute
  origin, separate PTH/NPTH files.
- Zones: their guide says refill zones before plotting. KiCad 10 does it in the
  CLI (`--check-zones`, used by the script); on KiCad 8/9 press **B** in the PCB
  editor and save before exporting.
- Assembly: BOM columns `Comment, Designator, Footprint, LCSC Part #`; CPL
  columns `Designator, Mid X, Mid Y, Rotation, Layer` (mm, rotation
  counter-clockwise, Layer Top/Bottom). Extra columns (Val, Package) are ignored.
- Rotations: JLCPCB's library zero orientation differs from KiCad for some
  packages; fix with `--rot` after checking their placement preview.
- Order form: layers, size are read from the Gerbers; choose thickness
  (0.4–2.0 mm, 1.6 default), finish (HASL lead-free / ENIG), mask colour,
  "Remove order number" if you don't want their tracking number printed on the silkscreen.
- Cheapest via: ≥ 0.3 mm hole; 0.15 mm holes and 0.2–0.25 mm holes with
  diameter < 0.45 mm cost extra.

## PCBWay

Source: [capabilities](https://www.pcbway.com/capabilities.html).

- Same Gerber zip works. Assembly BOM: their quote template columns
  (`--fab pcbway` writes Item #, Designator, Qty, Manufacturer, Mfg Part #,
  Description/Value, Package, Type, Notes); they source by MPN, so fill
  `Manufacturer` and `MPN` in the schematic.
- Centroid: the CPL file from the script is accepted.
- Standard process: trace/space 0.1/0.1 mm, holes 0.15–6.0 mm (< 0.2 mm costs
  extra), annular ring 0.15 mm, legend ≥ 0.8 mm high / 0.15 mm line.

## Thai local fabs / EMS

- Ask for: capability sheet (min trace/space, drill, annular ring, edge
  clearance, silk), accepted file formats, panel requirements, lead time,
  VAT invoice. Then build a `.kicad_dru` from their numbers (copy
  `thai-conservative.kicad_dru` and tighten).
- EMS houses usually want: Gerber zip, drill, BOM with MPN + approved
  alternates, CPL, assembly drawing (PDF of F.Fab/B.Fab with refs),
  STEP model, test/programming instructions, and IPC class (2 for most
  commercial products, 3 for high reliability).
- Assembly drawing PDF: `kicad-cli pcb export pdf -l F.Fab,Edge.Cuts -o assembly-top.pdf board.kicad_pcb`
  (KiCad 9+ add `--mode-single`).

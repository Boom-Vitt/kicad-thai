# Thai text on the silkscreen (ตัวหนังสือไทยบน PCB)

KiCad's built-in stroke font (Newstroke) has no Thai glyphs: Thai comes out
as empty boxes. Since KiCad 7, text can use any TrueType/OpenType font, but
**only KiCad 9+ plots Thai correctly** — tested in this repo's CI with Sarabun:

| KiCad | `ผู้ใหญ่ ปั๊มน้ำ ที่นี่` on the silkscreen |
|---|---|
| 8.0.9 | **"ผใหญ ปมน ทน"** — every vowel above/below and every tone mark is dropped, silently |
| 9.0.9 | correct |
| 10.0.6 | correct |

So: Thai silkscreen needs KiCad 9.0.9+ or 10.0.6+. `export_fab.py` warns when
it sees Thai text on a board exported with KiCad 8.

## How

1. Install an OFL Thai font on every machine that edits or exports the board
   (including CI): **Sarabun** (Thai government style, very readable when
   small) or **Noto Sans Thai** (looped / loopless). Both are free (OFL).
2. In the PCB editor, select the text → Properties → Font: pick the font.
   In the file this is `(effects (font (face "Sarabun") (size 2 2) (thickness 0.3)))`.
3. KiCad 9+: Board Setup → Embedded Files → **Embed fonts**, so the board
   renders the same on a machine without the font. (The board also stores a
   `render_cache` of the outlines.) Alternatively convert the text to polygons
   (right-click → Shape Modification → Convert to Polygon) for a final, frozen label.
4. Export Gerbers and **look at the silkscreen layer in GerbView** or the
   fab's viewer. Gerbers contain the outlines only, no font, so what you see
   is what gets printed.

## Sizes that survive printing

Thai stacks marks above and below the base line, so the base glyph is small
for a given text height. Fab minimums (JLCPCB: height ≥ 1.0 mm, line
≥ 0.15 mm) are for Latin text; for Thai use:

| Use | Height | Line/thickness |
|---|---|---|
| Minimum that stays legible | 1.5 mm | 0.2 mm |
| Normal labels | 2.0 mm | 0.25 mm |
| Warnings (อันตราย! ไฟฟ้า 220V) | ≥ 2.5 mm | 0.3 mm |

## Known issues

- KiCad 8: drops Thai combining marks (verified above). Related upstream fixes:
  combining vowels for Hindi were fixed in 9.0.7 ([#22402](https://gitlab.com/kicad/code/kicad/-/issues/22402));
  10.0.5 failed to plot text in a non-embeddable outline font ([#25228](https://gitlab.com/kicad/code/kicad/-/issues/25228)).
  9.0.0–9.0.6 were not tested; prefer 9.0.9.
- Thai digits (๐–๙) need the font to contain them (Sarabun does).
- If the font is missing on the exporting machine, KiCad falls back to
  another font: always check the Gerber, not the editor view.

## How this was checked

`tests/kicad/thai_silkscreen.kicad_pcb` (Sarabun at 2.5/2.0/1.5/1.0 mm plus the
stroke font) is plotted by KiCad 8.0.9, 9.0.9 and 10.0.6 in CI; the Gerbers
are rendered to PNG and kept as build artifacts for a visual check. The table
above is from looking at those renders (2026-10-02).

---
name: kicad-pcb
description: End-to-end KiCad 8/9/10 PCB design workflow for Thai engineers, students and factories — requirements, schematic, footprints, board setup, layout, checks and handoff to a fab — plus Thai text on the silkscreen. Use whenever the user works on a KiCad project (.kicad_pro, .kicad_sch, .kicad_pcb), asks to design, lay out or review a circuit board, or writes in Thai about ออกแบบ PCB, วาดวงจร, ลากลาย, ลายวงจร, แผ่นปริ้น, ทำปริ้น, แผ่นวงจรพิมพ์, ทำบอร์ด, ฟุตปริ้น, ตัวหนังสือไทยบนบอร์ด, even if they never say "KiCad". Routes to kicad-check (ERC/DRC/DFM), kicad-fab-export (Gerber/BOM/CPL), thai-pcb-compliance (มอก./กสทช./mains safety) and thai-pcb-sourcing (Thai fabs, parts, import VAT).
---

# KiCad PCB design (Thai industry)

Reply in Thai when the user writes Thai; keep tool names, layer names and
commands in English. Thai engineers mix both ("ลาก trace", "เช็ก DRC"), so
[references/glossary-th.md](references/glossary-th.md) maps the Thai terms
people actually type to KiCad terms.

## 0. Look before touching anything

1. Find the project: `*.kicad_pro` with matching `.kicad_sch` / `.kicad_pcb`.
2. Find KiCad: `kicad-cli version` (macOS: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`,
   Windows: `C:\Program Files\KiCad\<ver>\bin\kicad-cli.exe`, Flatpak:
   `flatpak run --command=kicad-cli org.kicad.KiCad`). The bundled scripts find it automatically.
3. Read the file header `(version YYYYMMDD)` and `(generator_version "9.0")` to
   know which KiCad last saved it. **Newer KiCad saves files older KiCad cannot
   open.** Never re-save a project in a newer major version, or tell a team on
   KiCad 9 to "just open it in 10", without warning them. Details:
   [references/kicad-versions.md](references/kicad-versions.md).
4. If the project is a git repo, check `git status` first so every change you make is reviewable.

## 1. Editing KiCad files safely

KiCad files are S-expressions and the GUI rewrites them on save. Prefer, in order:

1. **kicad-cli** for anything it can do (checks, exports, upgrades) — read-only on sources.
2. **Instructions for the user in the GUI** for layout and routing. Routing is
   visual work; describe *what* and *where* (net, layer, width, which side of a
   part) rather than generating thousands of coordinates.
3. **KiCad's Python/IPC API** for bulk, repeatable changes (rename refs, set
   fields, place parts on a grid) — see references/kicad-versions.md for which API your version has.
4. **Hand-editing the S-expression text** only for small, surgical changes
   (a field value, a net class, a text string). Before that: make sure the file
   is not open in KiCad (a `~<name>.kicad_pcb.lck` file means it is), keep a
   copy or commit, change as little as possible, never invent or reuse UUIDs,
   then prove the file still loads by running `kicad-cli pcb drc` / `sch erc` on it.

## 2. Workflow

Ask only what you cannot infer. These answers change the design, so get them early:

| Question | Why it matters |
|---|---|
| Board size / enclosure / mounting holes? | outline, connector placement |
| Mains (ไฟบ้าน 220 V) on the board? | creepage/clearance, fusing, มอก. → **thai-pcb-compliance** |
| Radio (WiFi/BLE/LoRa/4G)? | antenna keep-out, กสทช. → **thai-pcb-compliance** |
| How many boards, who makes them? | fab rules + layer count → **kicad-check** presets, **thai-pcb-sourcing** |
| Who solders it? (hand / JLCPCB SMT / Thai EMS) | part sizes (0402 vs 0805), BOM fields, fiducials |
| Environment (heat, humidity, vibration, outdoor)? | Thailand is hot and humid: conformal coat, derating, creepage pollution degree |

### Schematic (วาดวงจร)

- Use KiCad's stock symbol/footprint libraries first; they follow the KiCad
  Library Conventions (KLC). Make project-local libraries for custom parts —
  never edit the global ones.
- Every placed part needs: Reference, Value, Footprint, and for assembly an
  `MPN` and/or `LCSC` field. Add these fields while drawing, not at order time:
  `kicad-fab-export` turns them straight into the fab BOM.
- Power: drive every power net (PWR_FLAG on connectors/regulator outputs), add
  no-connect flags on unused pins, one decoupling cap per supply pin close to
  it in the schematic order so it is close on the board.
- Annotate, then run ERC (**kicad-check**) and fix errors before layout.

### Footprints (ฟุตปริ้น)

- Check every footprint you didn't make yourself against the datasheet's
  recommended land pattern: pin 1, pitch, pad size, mechanical drawing view
  (top vs bottom). This is the most common cause of dead first boards.
- For hand soldering prefer 0805/1206 and SOIC; for JLCPCB/EMS assembly 0402/0603 are fine.
- Thermal pads (QFN, DPAK): add vias, decide on solder-paste windowing.

### Board setup (ก่อนลากลาย)

1. Pick the fab first, then load its rules: copy the matching preset from
   `kicad-check/assets/rules/` as `<project>.kicad_dru`, and set the same
   minimums in Board Setup → Constraints.
2. Stackup: 1.6 mm FR-4, 1 oz (35 µm) outer copper is the cheap default
   everywhere; 2 layers for simple boards, 4 layers (sig/GND/PWR/sig) as soon as
   you have fast edges, a radio, USB, or a dense MCU.
3. Net classes: `Default` at the fab minimum + margin, `Power` wider. Size
   power tracks with KiCad's PCB Calculator → Track Width (IPC-2221 based)
   from the real current and allowed temperature rise, rather than a rule of thumb.
4. Mains boards: add a `Mains` net class with large clearance and draw the
   isolation slot/keep-out before routing anything else.

### Layout (ลากลาย)

Guidelines with reasons: [references/layout-guidelines.md](references/layout-guidelines.md).
The short version: place connectors and mechanically fixed parts → place
by signal flow → decoupling caps at the pins → solid ground plane, don't cut
it under fast signals → route critical nets (crystals, USB pairs, switching
regulator loops, RF) first → power → the rest → pour zones → silkscreen last.

### Thai text on the silkscreen (ตัวหนังสือไทยบนบอร์ด)

Needs a TrueType font **and KiCad 9+**: KiCad 8 silently drops every Thai
vowel and tone mark from the Gerbers (verified). How to do it and what to
check: [references/thai-silkscreen.md](references/thai-silkscreen.md).

### Checks and handoff

- Run **kicad-check** (ERC + DRC with fab preset + DFM review) until zero errors,
  and explain every remaining warning you decide to keep.
- Run **kicad-fab-export** for the Gerber zip, BOM and CPL.
- For anything sold in Thailand, run **thai-pcb-compliance** before the first
  production order, not after — moving a mains trace is cheap now, expensive later.
- For "where do I make/buy this in Thailand" questions use **thai-pcb-sourcing**.

## Reporting back

End each step with: what you checked, what you changed (file + what), what the
user must do in the GUI, and what is still unknown. Never say a board is
"ready to manufacture" unless DRC with the fab's rules passed and the Gerbers
were viewed in a Gerber viewer (KiCad's GerbView or the fab's online viewer).

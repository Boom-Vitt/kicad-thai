---
name: kicad-check
description: Run KiCad ERC and DRC headlessly with kicad-cli, check the board against JLCPCB, PCBWay or conservative Thai-fab design-rule presets, explain every violation in Thai or English, and do a DFM/DFA design review before ordering. Use when the user asks to check, verify, review or "ตรวจ" a KiCad schematic or PCB — ตรวจ DRC, ตรวจ ERC, เช็กบอร์ด/เช็คบอร์ดก่อนสั่งผลิต, บอร์ดนี้ผลิตได้ไหม, ลายชิดเกินไหม, design review, DFM — or pastes DRC/ERC errors, even if they don't name kicad-cli.
---

# KiCad checks: ERC, DRC, fab rules, design review

Reply in Thai when the user writes Thai. Scripts live next to this file;
run them with the absolute path of this skill's `scripts/` folder.

## 1. Pick the rule set (before running DRC)

DRC only knows the rules stored in the project. Ask which fab will make the
board (or infer it from context), then:

| Fab | Preset (in `assets/rules/`) |
|---|---|
| JLCPCB, 2 layers | `jlcpcb-2layer.kicad_dru` |
| JLCPCB, 4+ layers | `jlcpcb-multilayer.kicad_dru` |
| PCBWay standard | `pcbway-standard.kicad_dru` |
| Thai local fab / unknown fab / first board | `thai-conservative.kicad_dru` — loose limits most shops can make |
| Mains (220 V) on the board, KiCad 9+ | add `mains-220v-addon.kicad_dru` rules on top of one of the above |

Install the preset as `<project>.kicad_dru` next to the `.kicad_pro`:

```bash
cp -n "<skill>/assets/rules/jlcpcb-2layer.kicad_dru" "<project-dir>/<project>.kicad_dru"
```

`-n` keeps an existing rules file (on Windows, copy only if the file doesn't exist); if one exists, show the user the diff and
merge by hand — custom rules are the user's work.

The presets deliberately contain **no copper `clearance` or `edge_clearance`
rules**: a custom rule overrides net-class clearances, so a fab minimum of
0.1 mm would silently beat a 3 mm `Mains` class. Set those two minimums in
Board Setup → Constraints (each preset's header lists the numbers); check the
`.kicad_pro` `"rules"` section and tell the user if they are looser than the fab.

Fab capability numbers change; the preset headers carry the source URL and
the date they were checked. Re-check the fab's page for anything near a limit.

## 2. Run ERC + DRC

```bash
python3 "<skill>/scripts/run_checks.py" path/to/project.kicad_pro          # readable summary
python3 "<skill>/scripts/run_checks.py" path/to/project.kicad_pro --json   # for you to parse
```

- Runs `kicad-cli sch erc` and `kicad-cli pcb drc --schematic-parity`,
  errors + warnings, excluded markers skipped.
- Proves the `.kicad_dru` actually loaded (KiCad ignores a broken rules file
  without a word, and DRC then "passes"): a copy of the board is checked with
  a canary rule. Exit code 2 if the rules didn't load.
- Exit code 1 when anything has error severity (good for CI).
- Prints where the raw JSON reports are kept; open them for item coordinates.
- Works with KiCad 8, 9 and 10; finds kicad-cli by itself (or `--kicad-cli PATH`).

Without the script: `kicad-cli pcb drc --format json --severity-error --severity-warning --schematic-parity -o drc.json board.kicad_pcb`.

## 3. Explain and fix

For each violation type, say what it means, where it is (ref/net/layer +
coordinates in mm) and the fix. Meanings and usual fixes in Thai and English:
[references/violations.md](references/violations.md).

Rules of thumb:
- `unconnected_items`, `shorting_items`, `clearance` on mains nets, `hole_clearance` and parity errors are never acceptable for an order.
- Don't fix DRC by loosening the rule or excluding the marker unless the user
  confirms the fab can do it; then record why in the exclusion comment.
- Silk and courtyard warnings are cheap to fix now; fix them.
- Re-run after fixes and report the before/after counts.

## 4. Design review (what DRC can't see)

When the user asks for a review, or before any first order, go through
[references/dfm-checklist.md](references/dfm-checklist.md) using the
schematic, the board and the DRC report. Report ❌ items first, each with
the reason and the fix. Mains or radio on the board → also run **thai-pcb-compliance**.

## CI (optional)

The same script works in GitHub Actions with the official KiCad image:

```yaml
- run: docker run --rm -v "$PWD:/w" -w /w kicad/kicad:9.0 python3 path/to/run_checks.py hw/board.kicad_pro
```

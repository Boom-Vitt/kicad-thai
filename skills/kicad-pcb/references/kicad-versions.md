# KiCad versions and automation (checked 2026-10-02)

| | KiCad 8 | KiCad 9 | KiCad 10 |
|---|---|---|---|
| Status | no more updates | last release 9.0.9 (2026-04-28) | current, 10.0.6 (2026-08-29) |
| `kicad-cli sch erc` / `pcb drc` | ✅ (new in 8) | ✅ | ✅ + DRC `--refill-zones`, `--save-board` |
| `sch export bom` | ✅ (new in 8) | ✅ | ✅ (fields with or without `${}`) |
| Gerber zone refill in CLI | ❌ | ❌ | `pcb export gerbers --check-zones` |
| Jobsets (`kicad-cli jobset run`) | ❌ | ✅ | ✅ |
| Creepage DRC constraint | ❌ | ✅ | ✅ |
| `pcb upgrade` / `sch upgrade` | ❌ | ❌ | ✅ |
| Layer IDs in `.kicad_pcb` | F.Cu=0, In1=1…, B.Cu=31 | F.Cu=0, B.Cu=2, In1=4, In2=6… | same as 9 |
| Python | SWIG `pcbnew` | SWIG (deprecated) + IPC API | SWIG (deprecated) + IPC API |

Sources: [KiCad 10.0.0 release](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/),
[9.0.9 release](https://www.kicad.org/blog/2026/04/KiCad-9.0.9-Release/),
CLI reference https://docs.kicad.org/10.0/en/cli/cli.html (also /8.0/, /9.0/).

## Practical consequences

- **Files only move forward.** A board saved by 10 won't open in 9. Before
  editing, check `(generator_version "…")` in the file and ask which version
  the team uses. Never upgrade a shared project silently.
- **Don't parse layer numbers.** They changed in 9; match layers by name
  (`"F.Cu"`), and remember copper layers can have user names
  (`(0 "F.Cu" signal "top_layer")`). Our export script handles both.
- **KiCad 10 boards have no netcodes** (file version 20251028): match nets by name.
- **kicad-cli 8/9 doesn't refill zones.** Zone fills are whatever was saved:
  refill (B) and save in the GUI before DRC/export, or use KiCad 10.
- **kicad-cli 8/9 skips a renamed copper layer** requested by its canonical
  name in `pcb export gerbers --layers` (seen on 8.0.9 and 9.0.9 with KiCad's
  own demos). Pass the user name too, and always count the copper Gerbers.

## Automation options

| Need | Use |
|---|---|
| Checks, exports, CI | `kicad-cli` (all versions, headless) |
| Repeatable output sets | KiCad 9+ jobsets: `kicad-cli jobset run -f outputs.kicad_jobset board.kicad_pro` |
| Edit the open board from a script (move/rename/set fields) | IPC API via `kicad-python` (`pip install kicad-python`, `import kipy`); 9/10: PCB editor only, KiCad GUI must be running with the API server enabled (Preferences → Plugins) |
| Legacy scripts | SWIG `import pcbnew` still works in 9/10 but is deprecated; removal planned for 11 — don't start new work on it |
| Bulk text edits without KiCad | parse the S-expression carefully (see SKILL.md §1) |

Sources: https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/ ,
https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/ ,
https://pypi.org/project/kicad-python/

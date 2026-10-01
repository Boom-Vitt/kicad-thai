<div align="center">

<img src="assets/banner.png" alt="KiCad Thai — KiCad PCB skills for the Thai electronics industry" width="100%">

<br>

**KiCad 8/9/10 agent skills for engineers, makers and factories in Thailand: DRC against fab rule presets, one-command Gerber/BOM/CPL for JLCPCB and PCBWay, TISI (มอก.) / NBTC (กสทช.) and 220 V creepage checklists, Thai sourcing and import VAT, Thai text on the silkscreen.**

[![License: MIT](https://img.shields.io/badge/License-MIT-1F7A4D?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/Boom-Vitt/kicad-thai/test.yml?branch=main&style=flat-square&label=tests)](https://github.com/Boom-Vitt/kicad-thai/actions)
[![KiCad](https://img.shields.io/badge/KiCad-8_·_9_·_10-314CB0?style=flat-square&logo=kicad&logoColor=white)](https://www.kicad.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757?style=flat-square&logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins)
[![Codex](https://img.shields.io/badge/Codex-plugin-000000?style=flat-square&logo=openai&logoColor=white)](https://developers.openai.com/codex)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-Cursor_·_Gemini_·_Copilot_·_OpenCode-E2B450?style=flat-square)](https://agentskills.io)

[ไทย](README.md) · **English**

</div>

---

## Why

AI assistants can draw schematics, but the last mile — fab files and selling in Thailand — goes wrong in the same ways:

- **Gerbers silently missing copper.** If a copper layer has a user name (e.g. `top_layer`), `kicad-cli pcb export gerbers --layers F.Cu` skips it without an error. We hit this on KiCad 8.0.9 and 9.0.9 with KiCad's own demo boards. The export script here passes both names and refuses to finish if any copper layer, the outline or the drill file is missing.
- **JLCPCB BOM rejected:** `R1-R3` ranges, wrong columns, LCSC numbers in random fields, DNP parts leaking in.
- **Rotated parts in the CPL** (SOT-23, QFN, bottom side) — `--rot` corrections.
- **Which มอก. / กสทช. applies**, and what creepage/clearance 220 V needs.
- **Thai silkscreen:** KiCad's stroke font has no Thai; you need a TrueType font and sizes that survive printing.
- **Where to make it and what import VAT/duty will cost** (low-value parcels lost their exemptions in 2024–2026).

## Install

```bash
# Claude Code
claude plugin marketplace add Boom-Vitt/kicad-thai
claude plugin install kicad-thai@kicad-thai

# Codex
codex plugin marketplace add Boom-Vitt/kicad-thai
codex plugin add kicad-thai@kicad-thai

# Gemini CLI
gemini extensions install https://github.com/Boom-Vitt/kicad-thai

# Cursor, GitHub Copilot, OpenCode, Windsurf, Amp and 70+ other agents
npx skills add Boom-Vitt/kicad-thai
```

Or copy any folder from [`skills/`](skills) into `~/.claude/skills/`, `~/.agents/skills/` or `.agents/skills/` — each skill is self-contained.

Requires KiCad 8, 9 or 10 (`kicad-cli` is found automatically on macOS, Windows, Linux and Flatpak) and Python 3.9+ (stdlib only).

## Skills

| Skill | What it does |
|---|---|
| [`kicad-pcb`](skills/kicad-pcb/SKILL.md) | end-to-end design workflow, safe editing of KiCad files, layout guidelines, Thai silkscreen, KiCad 8/9/10 differences, Thai↔English PCB glossary |
| [`kicad-check`](skills/kicad-check/SKILL.md) | headless ERC/DRC with JLCPCB / PCBWay / conservative Thai-fab presets, violations explained in Thai or English, DFM review checklist |
| [`kicad-fab-export`](skills/kicad-fab-export/SKILL.md) | Gerber zip + Excellon + BOM + CPL in JLCPCB/PCBWay format in one command, rotation fixes, ordering notes |
| [`thai-pcb-compliance`](skills/thai-pcb-compliance/SKILL.md) | TISI mandatory standards, NBTC radio rules (2.4 GHz, LoRa AS923, SDoC), 220 V creepage/clearance with KiCad 9+ DRC rules, RoHS, Thai test labs |
| [`thai-pcb-sourcing`](skills/thai-pcb-sourcing/SKILL.md) | China vs Thai fabs/EMS, local part shops, BOM part numbers, landed cost with Thai import VAT and duty |

Every regulatory, tax and company fact links to its source with a check date (2026-10-02); unverified items are marked **UNVERIFIED**, and the skills tell the agent never to invent a standard number or rule.

## Scripts without an AI

```bash
python3 skills/kicad-check/scripts/run_checks.py hw/board.kicad_pro            # exit 1 on errors (CI-friendly)
cp -n skills/kicad-check/assets/rules/jlcpcb-2layer.kicad_dru hw/board.kicad_dru
python3 skills/kicad-fab-export/scripts/export_fab.py hw/board.kicad_pro --fab jlcpcb --step
```

## Tested against real KiCad

CI runs both scripts with the official Docker images of **KiCad 8.0.9, 9.0.9 and 10.0.6** on KiCad's own `pic_programmer` (2-layer) and `video` (4-layer) demos. It checks for complete copper/outline/drill Gerbers, JLCPCB BOM/CPL format, STEP export, and that every rule preset loads (against a deliberately broken rules file as a control). It also exports Thai Sarabun silkscreen text to Gerber and renders it to PNG for a visual check. Offline tests use a fake `kicad-cli`.

## Limits

Not legal advice — confirm with TISI, NBTC, Thai Customs or a test lab (EEI, PTEC) before production. Creepage/clearance values are IEC 62368-1 design-start values for the stated conditions, not a certification. Routing stays a GUI job; the agent tells you what to do and checks the result.

## Contributing

See [AGENTS.md](AGENTS.md). Especially welcome: Thai fab capability sheets (with links), CPL rotation corrections that worked at JLCPCB, newly announced standards. Works well alongside [kicad-happy](https://github.com/aklofas/kicad-happy) and [KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server).

## License

[MIT](LICENSE) © Boom-Vitt

# AGENTS.md

Guide for AI agents and humans changing this repo. Agents *using* the skills
only need `skills/*/SKILL.md`.

## Layout

```
skills/<name>/SKILL.md     single source of truth (Agent Skills format)
skills/<name>/scripts/     stdlib-only Python 3.9+, run on macOS/Windows/Linux
skills/<name>/references/  loaded on demand; keep SKILL.md under 500 lines
skills/<name>/assets/      files copied into user projects (e.g. .kicad_dru presets)
.claude-plugin/ .codex-plugin/ .cursor-plugin/ gemini-extension.json .agents/plugins/
                           thin per-agent manifests, all pointing at ./skills/
tests/                     offline tests with a fake kicad-cli; CI also runs real KiCad 8/9/10
```

## Rules

- Every skill folder must work on its own when copied to `~/.claude/skills/`,
  `~/.agents/skills/` etc. No imports across skills. The small kicad-cli
  helper block is duplicated on purpose; `tests/test_scripts.py` keeps the copies identical.
- `name` in frontmatter = folder name, lowercase-hyphen, ≤ 64 chars;
  `description` ≤ 1024 chars, says what it does **and** when to use it,
  with the Thai phrases users actually type.
- Facts about Thai law, standards, fees and companies go in `references/`
  with a source URL and a "checked" date. Never invent a มอก. number,
  NBTC rule or price. If unsure, say so and point to the regulator.
- Scripts never modify the user's `.kicad_*` files and never overwrite
  an existing `.kicad_dru`.
- Bump the same version in all five manifests (`plugin.json` ×3,
  `marketplace.json`, `gemini-extension.json`); the tests check this.

## Test

```bash
python3 tests/test_scripts.py
claude plugin validate .
```

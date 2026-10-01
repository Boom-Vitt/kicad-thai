---
name: thai-pcb-compliance
description: Thai regulatory and safety checklist for electronic products and PCBs — TISI / สมอ. mandatory standards (มอก. 62368, มอก. 60335, plug มอก. 166), NBTC / กสทช. radio rules (WiFi/BLE 2.4 GHz, LoRa 920-925 MHz, SDoC, Class A/B), 220 V mains creepage and clearance in KiCad, RoHS/WEEE status and Thai test labs (EEI, PTEC). Use when a board or product will be sold, imported or installed in Thailand, has mains (ไฟบ้าน 220V) or a radio, or the user asks ต้องขอ มอก. ไหม, ขออนุญาต กสทช., ขาย IoT ในไทย, SDoC, ระยะ creepage, ปลอดภัยไหม, ส่งออกยุโรป RoHS — even if they only describe the product.
---

# Thai compliance for electronics (มอก. / กสทช. / mains safety)

Reply in Thai when the user writes Thai. You are giving engineering
guidance, not legal advice: state which facts are verified (with the source
from the references) and which are not, and point to the regulator or a
test lab for the final answer. Never invent a มอก. number, a fee, a deadline
or an NBTC rule — if it's not in [references/standards.md](references/standards.md),
say you don't know and how to find out.

## 1. Classify the product (ask or infer)

| Question | Leads to |
|---|---|
| Plugs into mains directly, or contains a mains power supply? | TISI safety standard + mains layout rules (§3) |
| Powered by an external adapter / USB / battery only? | the adapter needs มอก.; the board itself usually doesn't fall under mains safety |
| What is it? AV/ICT device, household appliance, lighting, industrial, medical, automotive? | which มอก. applies — 62368-1 list, 60335-2-x part, 1955 (lighting EMC)… or none |
| Has a radio (WiFi, BLE, LoRa, 4G, 433 MHz, RFID)? | NBTC route (§2) |
| Sold to consumers in Thailand, used in-house, or exported? | licences (ม.20 make / ม.21 import) vs destination rules (EU CE/RoHS…) |

Then produce a short table: requirement → applies? → why → next step → who
to contact. Mark each fact *verified (source)* or *check with regulator*.

## 2. Radio (กสทช.)

Key facts (sources in references/standards.md):
- WiFi/BLE 2.4 GHz at ≤ 100 mW e.i.r.p. (20 dBm **including antenna gain**):
  licence-exempt, **SDoC** to กสทช. มท. 1035. From 1 Feb 2026 the SDoC is
  reported to need an electrical safety report too — confirm with NBTC.
- LoRa AS923 (920–925 MHz): ≤ 50 mW e.i.r.p. → SDoC; above → Class A testing.
- Using a pre-certified module (ESP32-WROOM, etc.) helps with testing, but
  assume the **finished product still needs its own SDoC** under its brand/model.
- Design consequences to check in KiCad: antenna keep-out per the module
  datasheet, RF power configured in firmware so e.i.r.p. stays within the limit
  with the antenna actually used, and a label space for the NBTC marking.

## 3. Mains on the board (ไฟบ้าน 220 V)

Read [references/mains-pcb.md](references/mains-pcb.md) for definitions,
starting values and layout rules. In KiCad 9+:

1. Put every mains net in a net class named `Mains`.
2. Append the mains rules to the project's rules file: from the kicad-check
   skill, `tail -n +2 "<kicad-check>/assets/rules/mains-220v-addon.kicad_dru" >> <project>.kicad_dru`,
   or copy the rule block from references/mains-pcb.md.
3. Run **kicad-check**; `clearance` and `creepage` violations on mains nets are blocking.

KiCad 8 has no creepage check: measure creepage by hand (measure tool along
the board surface, around slots) and tell the user to upgrade if possible.

Push the user toward the simplest safe architecture: an external certified
adapter keeps their own board SELV-only, which is cheaper to certify.

## 4. Materials and environment

- RoHS: Thailand's มอก. 2368-2564 is voluntary; EU exports need EU RoHS. Order
  lead-free HASL or ENIG and lead-free assembly by default.
- WEEE/EPR: still a draft law in Thailand — mention it for product planning only.
- Climate: hot and humid; consider conformal coating, higher creepage
  margins (pollution degree 3 in dirty/condensing locations), and 40 °C+
  ambient derating inside enclosures.

## 5. Where to test

EEI (Samut Prakan) and PTEC/NSTDA (Pathum Thani) do safety and EMC testing in
Thailand; details and links in references/standards.md. Suggest a pre-compliance
scan before the formal test for anything with switching supplies or radios.

## Output

End with: "Verified" facts (with links), "Check with regulator/lab" items,
and the concrete KiCad changes (net classes, rules, keep-outs, slots,
silkscreen warnings and label areas) — so the engineering work can start today.

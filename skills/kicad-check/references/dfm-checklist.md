# Design review checklist (DFM / DFA / bring-up)

DRC proves the board meets *rules*; this list catches what rules can't see.
Go through it by reading the schematic and board files plus the DRC report,
and mark each line ✅ / ⚠️ (explain) / ❌ (must fix) / n/a. Report ❌ first.

## Schematic

- [ ] Every IC power pin has its decoupling cap(s); values match the datasheet
- [ ] Regulator input/output caps, feedback divider values and output voltage recalculated
- [ ] Reset, boot/strapping pins (e.g. ESP32 GPIO0/EN, STM32 BOOT0) at the right level with the right pull resistors
- [ ] Debug/programming access exists (SWD, UART, USB) and is reachable on the board
- [ ] Connector pinouts checked against the mating cable/module, viewed from the correct side
- [ ] Every external connector has ESD/over-voltage protection appropriate to what plugs in
- [ ] Voltage and power rating of every part checked at the worst case (Thai ambient 40 °C+ in an enclosure)
- [ ] Polarised caps have voltage margin (≥ 1.5–2× working for electrolytics, DC-bias derating for MLCCs)

## Board

- [ ] DRC run with the **fab's** preset, 0 errors; every kept warning justified
- [ ] Footprints checked against datasheets (pin 1, pitch, top vs bottom view)
- [ ] Board outline matches the enclosure drawing; mounting holes, connector positions measured
- [ ] Ground plane continuous under high-speed and RF traces; antenna keep-out respected
- [ ] Decoupling caps physically at their pins; switching regulator hot loop compact
- [ ] Thermal: hot parts have copper area/vias; nothing heat-sensitive next to them
- [ ] Mains area: creepage/clearance per thai-pcb-compliance, slots where needed, silkscreen warning
- [ ] Test points on every rail and key signals; ground test point/hook
- [ ] Silkscreen: refs readable, polarity/pin-1 marks visible after assembly, board name + revision + date
- [ ] Copper and silk text not mirrored on the wrong side (DRC `mirrored_text_on_front_layer` warns)

## Assembly (if a fab or EMS solders it)

- [ ] Every BOM line has a part number the assembler can buy (LCSC for JLCPCB, MPN for PCBWay/Thai EMS)
- [ ] DNP parts marked DNP in the schematic (not just left without value)
- [ ] CPL rotations checked in the fab's online preview — the #1 assembly error
- [ ] 3 fiducials (board or panel), part-free border for panel rails/V-score
- [ ] Parts that need special handling flagged: moisture-sensitive (MSL), bottom-side, press-fit, hand-soldered THT

## Before ordering

- [ ] Gerbers opened in a viewer (KiCad GerbView or the fab's viewer): every layer present, outline closed, drills aligned
- [ ] Board thickness, copper weight, surface finish (HASL lead-free / ENIG), mask colour chosen on purpose
- [ ] Quantity and lead time match the plan; import VAT/shipping counted (thai-pcb-sourcing)

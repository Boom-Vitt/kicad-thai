# Mains (220 V) on the PCB — clearance, creepage, layout

Thai homes get 220 V (PEA) or 230 V (MEA) at 50 Hz, so design for ≤ 250 Vrms
working voltage and the mains transient of overvoltage category II (2500 V peak).

## Words

- **Clearance (ระยะห่างในอากาศ)**: shortest distance through air between two conductors. Sets flashover by transients.
- **Creepage (ระยะห่างตามผิวฉนวน)**: shortest path along the surface of the insulation (the board). Sets tracking by dirt + humidity. Thailand's humidity is a reason not to shave this.
- **Functional insulation**: needed for the circuit to work, not for shock protection (e.g. L to N).
- **Basic insulation**: one level of shock protection (e.g. L to earthed metal).
- **Reinforced insulation**: equivalent to double insulation; required between mains and anything a user can touch (SELV: USB, buttons, sensor wires, low-voltage connectors) when there is no protective earth.

## Starting values (IEC 62368-1:2018 = มอก. 62368 เล่ม 1-2563)

Conditions: OVC II (2500 V peak), pollution degree 2, FR-4 (material group III), ≤ 2000 m.

| Between | Working voltage | Insulation | Clearance | Creepage |
|---|---|---|---|---|
| L ↔ N, relay COM ↔ NO | ≤ 250 V | functional (practical minimum) | 1.5 mm | 2.5 mm |
| Mains ↔ low-voltage / user-touchable | ≤ 250 V | reinforced | 3.0 mm | 5.0 mm |
| DC bus / switcher primary ↔ other mains | ≤ 320 V | functional | 1.5 mm | 3.2 mm |
| DC bus / switcher primary ↔ low-voltage | ≤ 320 V | reinforced | 3.0 mm* | 6.4 mm |

\* Rectified 230 V is ~325 V DC, above the 250 V column, and a flyback drain rings
far higher: **measure** the working voltage. Repetitive peaks above the mains
peak need more clearance than 3.0 mm; look it up for the measured peak.

Treat these as the **minimum to start a layout**, then add margin (many
designers use 6–8 mm mains-to-SELV), and confirm with the standard that
applies to the product (62368-1 for AV/ICT, 60335-1 for household appliances,
which has its own tables) and with the test lab. Values with altitude,
pollution degree 3, or other working voltages are different.

KiCad 9+ DRC can enforce these numbers (KiCad 8 can't: no creepage check, and
it silently ignores the whole rules file). Put the mains nets in a net class
named `Mains`, the > 250 V nets in `Mains_HV`, and append these rules to `<project>.kicad_dru` (a fab preset
from kicad-check, or a new file starting with `(version 1)`). The same rules
ship as `kicad-check/assets/rules/mains-220v-addon.kicad_dru`.

```
(rule "Mains functional (L-N): clearance"
	(constraint clearance (min 1.5mm))
	(condition "(A.hasNetclass('Mains') || A.hasNetclass('Mains_HV')) && (B.hasNetclass('Mains') || B.hasNetclass('Mains_HV')) && A.Net != B.Net"))
(rule "Mains functional (L-N): creepage"
	(constraint creepage (min 2.5mm))
	(condition "(A.hasNetclass('Mains') || A.hasNetclass('Mains_HV')) && (B.hasNetclass('Mains') || B.hasNetclass('Mains_HV')) && A.Net != B.Net"))
(rule "Mains_HV functional: creepage"
	(constraint creepage (min 3.2mm))
	(condition "(A.hasNetclass('Mains_HV') || B.hasNetclass('Mains_HV')) && (A.hasNetclass('Mains') || A.hasNetclass('Mains_HV')) && (B.hasNetclass('Mains') || B.hasNetclass('Mains_HV')) && A.Net != B.Net"))
(rule "Mains to low voltage: reinforced clearance"
	(constraint clearance (min 3.0mm))
	(condition "((A.hasNetclass('Mains') || A.hasNetclass('Mains_HV')) && !B.hasNetclass('Mains') && !B.hasNetclass('Mains_HV')) || ((B.hasNetclass('Mains') || B.hasNetclass('Mains_HV')) && !A.hasNetclass('Mains') && !A.hasNetclass('Mains_HV'))"))
(rule "Mains to low voltage: reinforced creepage"
	(constraint creepage (min 5.0mm))
	(condition "((A.hasNetclass('Mains') || A.hasNetclass('Mains_HV')) && !B.hasNetclass('Mains') && !B.hasNetclass('Mains_HV')) || ((B.hasNetclass('Mains') || B.hasNetclass('Mains_HV')) && !A.hasNetclass('Mains') && !A.hasNetclass('Mains_HV'))"))
(rule "Mains_HV to low voltage: reinforced creepage"
	(constraint creepage (min 6.4mm))
	(condition "(A.hasNetclass('Mains_HV') && !B.hasNetclass('Mains') && !B.hasNetclass('Mains_HV')) || (B.hasNetclass('Mains_HV') && !A.hasNetclass('Mains') && !A.hasNetclass('Mains_HV'))"))
```

## Layout rules

1. Group all mains parts in one area at the board edge near the inlet; draw the
   isolation boundary on F.SilkS with a hazard symbol and "อันตราย! ไฟฟ้า 220V".
2. Fuse first, right at the inlet (both for safety and for มอก. testing), then
   MOV / X-capacitor, then the rest. X-caps need a bleeder resistor.
3. Use a **slot** in Edge.Cuts (≥ 1 mm wide) under optocouplers, transformers
   and relays when the pin-to-pin distance can't meet creepage; a slot
   lengthens the surface path.
4. Never route low-voltage traces, pours or vias on *any* layer inside the
   reinforced boundary; check inner layers on 4-layer boards.
5. Isolation parts (optocoupler, transformer, relay, Y-cap across the barrier)
   must themselves carry a safety rating for reinforced insulation. For relays,
   check the datasheet for reinforced insulation between coil and contacts
   (many cheap blue relays don't have the pin spacing for it).
6. Never use a non-isolated supply (capacitive dropper, non-isolated buck)
   when anything is user-touchable (USB, buttons, headers, sensor wires): the
   whole low-voltage side then sits at mains potential. If the AC-DC must be on
   the board, use an encapsulated module with an IEC 62368-1 CB report and
   reinforced insulation, and copy its datasheet layout.
7. Draw a **Rule Area** (Place → Add Rule Area) over the isolation gap on
   **all copper layers**, keeping out tracks, vias and zones: zone fills obey
   clearance, not creepage, so a GND pour will otherwise creep up to the mains side.
8. Make sure every mains net actually lands in the `Mains` class: name the nets
   (`AC_L`, `AC_N`, `AC_L_FUSED`, `RELAY1_COM`…) and assign by pattern in
   Schematic/Board Setup → Net Classes; auto-named nets like `Net-(F1-Pad2)`
   silently stay in `Default` and escape the mains rules.
9. Wide tracks for current (PCB Calculator), no thermal reliefs on high-current
   mains pads that get hot, and keep electrolytics away from heat sources.

## Cheapest way to stay out of mains entirely

Use an external, already-certified adapter (5 V USB or 12 V DC). A mains
adapter sold in Thailand falls under มอก. 62368 เล่ม 1 (power supplies for
electronic appliances are on the mandatory list), so buy one that already
carries the มอก. mark; your board then only handles SELV.

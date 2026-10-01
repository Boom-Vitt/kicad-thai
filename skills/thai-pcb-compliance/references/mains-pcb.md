# Mains (220 V) on the PCB — clearance, creepage, layout

Thai homes get 220 V (PEA) or 230 V (MEA) at 50 Hz, so design for ≤ 250 Vrms
working voltage and the mains transient of overvoltage category II (2500 V peak).

## Words

- **Clearance (ระยะห่างในอากาศ)**: shortest distance through air between two conductors. Sets flashover by transients.
- **Creepage (ระยะห่างตามผิวฉนวน)**: shortest path along the surface of the insulation (the board). Sets tracking by dirt + humidity. Thailand's humidity is a reason not to shave this.
- **Basic insulation**: one level of protection (e.g. L to N, or L to earthed metal).
- **Reinforced insulation**: equivalent to double insulation; required between mains and anything a user can touch (SELV: USB, buttons, sensor wires, low-voltage connectors) when there is no protective earth.

## Starting values (IEC 62368-1:2018 = มอก. 62368 เล่ม 1-2563)

Conditions: ≤ 250 Vrms, OVC II (2500 V peak), pollution degree 2, FR-4 (material group IIIa/b), ≤ 2000 m.

| Between | Insulation | Clearance | Creepage |
|---|---|---|---|
| L ↔ N (before fuse/rectifier) | basic (functional) | 1.5 mm | 2.5 mm |
| Mains ↔ low-voltage / user-touchable | reinforced | 3.0 mm | 5.0 mm |

Treat these as the **minimum to start a layout**, then add margin (many
designers use 6–8 mm mains-to-SELV), and confirm with the standard that
applies to the product (62368-1 for AV/ICT, 60335-1 for household appliances,
which has its own tables) and with the test lab. Values with altitude,
pollution degree 3, or working voltage above 250 V are different.

`kicad-check/assets/rules/mains-220v-addon.kicad_dru` enforces these numbers
in KiCad 9+ DRC (clearance + creepage) for a net class named `Mains`.

## Layout rules

1. Group all mains parts in one area at the board edge near the inlet; draw the
   isolation boundary on F.SilkS with a hazard symbol and "อันตราย ไฟฟ้าแรงสูง".
2. Fuse first, right at the inlet (both for safety and for มอก. testing), then
   MOV / X-capacitor, then the rest. X-caps need a bleeder resistor.
3. Use a **slot** in Edge.Cuts (≥ 1 mm wide) under optocouplers, transformers
   and relays when the pin-to-pin distance can't meet creepage; a slot
   lengthens the surface path.
4. Never route low-voltage traces, pours or vias on *any* layer inside the
   reinforced boundary; check inner layers on 4-layer boards.
5. Isolation parts (optocoupler, transformer, relay, Y-cap across the barrier)
   must themselves carry a safety rating for reinforced insulation.
6. Wide tracks for current (PCB Calculator), no thermal reliefs on high-current
   mains pads that get hot, and keep electrolytics away from heat sources.

## Cheapest way to stay out of mains entirely

Use an external, already-certified adapter (5 V USB or 12 V DC). A mains
adapter sold in Thailand falls under มอก. 62368 เล่ม 1 (power supplies for
electronic appliances are on the mandatory list), so buy one that already
carries the มอก. mark; your board then only handles SELV.

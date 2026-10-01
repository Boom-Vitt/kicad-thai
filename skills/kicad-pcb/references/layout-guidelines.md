# Layout guidelines (with the reason for each)

Use these as review prompts, not dogma. When a rule conflicts with the
datasheet or the application note of the main IC, the datasheet wins — the
vendor measured their part.

## Placement

| Do | Why |
|---|---|
| Fix connectors, mounting holes, switches, LEDs, displays and the antenna first, from the enclosure drawing | they can't move later; everything else can |
| Place by signal flow: input → processing → output | short, uncrossed nets route themselves |
| Keep a 3–5 mm part-free border if the board is V-scored or in a panel | depaneling stress cracks MLCCs near the edge |
| Same orientation for polarised parts (diodes, electrolytics, LEDs) | faster, fewer mistakes in hand assembly and AOI |
| Put tall/heavy parts on one side; SMT-only on the bottom if assembled | one reflow pass, cheaper assembly |
| Leave room for test points on power rails and debug pins (SWD/UART) | bring-up without a microscope probe |
| 3 fiducials on assembled boards (or the panel rails) | machine vision alignment at the SMT line |

## Power and ground

| Do | Why |
|---|---|
| One decoupling cap per supply pin, smallest value closest, via to ground right at the cap pad | the loop area is the inductance; distance kills the decoupling |
| Solid ground plane (4-layer: layer 2), avoid slots/cuts under signals | return current flows right under the trace; a cut forces a detour = antenna |
| Don't split analog/digital ground by default; partition placement instead | split planes create more problems than they solve unless you know exactly where currents return |
| Switching regulator: route the hot loop (input cap – switch – diode/low-side FET) first and tiny, follow the IC app note | this loop is the main EMI source on most boards |
| Thermal: copper pours + via arrays under hot parts, check with the datasheet θJA conditions | Thai ambient is 35–40 °C in a closed box; derate for that, not 25 °C |
| Size tracks with PCB Calculator → Track Width; use 2 oz or pours for >3 A | IPC-2221 charts, not guesses |

## Signals

| Do | Why |
|---|---|
| Crystal: right next to the MCU, short traces, ground guard, nothing routed underneath | low-level oscillator, very sensitive to coupling |
| USB 2.0: route D+/D− as a 90 Ω differential pair, matched length, no stubs, over solid ground | signal integrity and EMC |
| Keep fast/clock traces away from board edges and connectors | edges radiate; connectors carry noise out on cables |
| ESD protection right at the connector, before anything else | the strike must be shunted before it reaches the IC |

## RF / modules (ESP32, LoRa, 4G)

- Follow the module's hardware design guide exactly for antenna placement:
  usually antenna at the board edge or overhanging, **no copper on any layer**
  under the antenna keep-out, ground pour with stitching vias around the
  module. Getting this wrong costs range and can fail radiated-emission tests.
- Use a certified module rather than a chip-down radio unless you have RF
  test capability — it also makes NBTC (กสทช.) approval simpler (see thai-pcb-compliance).

## Mains (220 V AC) boards

- Keep the hazardous-voltage area physically grouped and separated from the
  low-voltage side, with a clearly marked isolation barrier on the silkscreen.
- Clearance and creepage come from the product safety standard and the
  working voltage — use **thai-pcb-compliance**; add slots in the board
  under optocouplers/transformers when the creepage distance isn't enough.
- Fuse at the input, MOV/X-cap after the fuse, bleeder for X-caps per the standard.
- Thai homes: 220 V nominal, 50 Hz, wiring and earthing quality varies — design for surges.

## Silkscreen and documentation

- Reference designators readable and next to their part (or an assembly drawing
  layer if the board is too dense), polarity marks outside the part body.
- Board name, revision, date, and your company/website on F.SilkS — Thai text is
  fine (see thai-silkscreen.md).
- Mains boards: hazard symbol and "อันตราย ไฟฟ้าแรงสูง" / "DANGER HIGH VOLTAGE" near the mains area.
- Leave a white silkscreen box for serial number / QC sticker if the factory asks for one.

---
name: thai-pcb-sourcing
description: Where and how to get PCBs made, assembled and sourced for a project in Thailand — choosing between JLCPCB/PCBWay and Thai fabs/EMS (KCE, Gravitech, PCBCart Thailand, the new BOI PCB plants), buying parts locally (บ้านหม้อ, Arduitronics, Cybertice, ThaiEasyElec, DigiKey TH, LCSC), filling BOM part numbers, and estimating landed cost with Thai import VAT and duty on parcels from China. Use when the user asks สั่งทำ PCB ที่ไหน, โรงงาน PCB ในไทย, ซื้ออะไหล่อิเล็กทรอนิกส์, หาชิ้นส่วน, ภาษีนำเข้า PCB, ค่า VAT พัสดุจีน, ทำ PCBA ในไทย, or needs to pick a fab or supplier for a KiCad BOM.
---

# Sourcing PCBs and parts in Thailand

Reply in Thai when the user writes Thai. Facts, links and their verification
status live in [references/suppliers.md](references/suppliers.md); only
state prices, MOQs or tax rates from there or from a source you just checked,
and say when something is unverified.

## 1. Pick the manufacturing route

| Situation | Recommend | Why |
|---|---|---|
| Prototype, 5–50 boards, cheapest | JLCPCB or PCBWay + parts from LCSC / local shops | lowest cost, ~1 week + customs; use **kicad-fab-export** |
| Prototype with SMT assembly | JLCPCB / PCBWay assembly | needs LCSC (JLC) or MPN (PCBWay) fields in the schematic |
| Want a Thai invoice, Thai-speaking support, or local pickup | Gravitech, PCBCart (Samut Prakan factory) — ask for quote + capability sheet | VAT invoice, easier B2B paperwork |
| Volume production (thousands+) for an OEM | Thai EMS (Cal-Comp, Hana, SVI, Benchmark, Fabrinet, Delta) and the Thai PCB plants (KCE, Zhen Ding, Dynamic, WUS…) | local supply chain, BOI ecosystem; they need full fab + assembly data packs |

Ask the fab for its capability sheet before layout; then apply the matching
DRC preset with **kicad-check** (`thai-conservative` if unknown).

## 2. Fill the BOM so it can be bought

1. Every line gets `Manufacturer` + `MPN`; for JLCPCB also `LCSC` (C-number).
2. Prefer parts stocked by more than one source (e.g. LCSC and DigiKey, or a
   Ban Mo shop) for anything that would stop production if it went out of stock.
3. Check lifecycle (Active vs NRND/EOL) on the distributor page before committing.
4. Hand-soldered prototypes: buy 10–20 % extra of small passives.
5. Write the fields into the schematic symbols (not only the CSV) so the next
   export from **kicad-fab-export** carries them.

## 3. Landed cost of an order from China

Estimate before the user orders, and show the arithmetic:

```
goods (boards + assembly + parts) + shipping  = CIF value (THB)
+ import duty   (HS-code dependent — check itariff.customs.go.th; unverified for HS 8534)
+ VAT 7 %       on (CIF + duty)
+ courier clearance/handling fee (ask the courier)
= landed cost
```

Boards with a radio (WiFi/BLE/LoRa) can be held at customs for NBTC
paperwork — ask the courier before shipping (UNVERIFIED how strictly this is
applied to prototype quantities).

Since 2024–2026 low-value parcels no longer escape VAT/duty (see references);
couriers like DHL pay at the border and invoice the receiver. VAT-registered companies can
usually claim the import VAT back as input tax — tell them to keep the import
documents (ใบขนสินค้า / receipt) for their accountant.

## 4. Local parts in a hurry

Ban Mo (บ้านหม้อ) for same-day connectors, passives and tools; Arduitronics,
Cybertice, ThaiEasyElec for modules and maker parts; DigiKey TH for exact MPNs
in ~4 days (buyer pays duty/VAT). Always give the exact MPN and package
when asking a shop — "ตัวต้านทาน 10k" alone gets you the wrong size.

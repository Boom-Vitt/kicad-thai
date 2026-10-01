# Common ERC/DRC violations — meaning and usual fix (ไทย/English)

`type` is the key in the JSON report (`run_checks.py` groups by it). Fix the
cause, not the symptom: widening the rule or excluding the marker hides the
problem from DRC but not from the fab or the customer.

## ERC (schematic)

| type | ความหมาย | Usual fix |
|---|---|---|
| `pin_not_connected` | ขาอุปกรณ์ไม่ได้ต่อ | wire it, or place a no-connect flag (X) if it is really unused |
| `power_pin_not_driven` | ขาไฟเลี้ยงไม่มีแหล่งจ่าย | net comes from a connector/regulator KiCad can't see: add `PWR_FLAG` on that net |
| `pin_not_driven` | ขาอินพุตไม่มีสัญญาณขับ | connect it, or tie it high/low as the datasheet says |
| `pin_to_pin` | ชนิดขาขัดกัน (เช่น output ชน output) | real bug or wrong pin type in a custom symbol — check before suppressing |
| `label_dangling` / `global_label_dangling` | ป้ายชื่อ net ลอย ไม่ได้ต่อสาย | wire end not exactly on the label anchor; drag the wire onto it |
| `wire_dangling` | สายไฟปลายลอย | delete stray wire segments |
| `unannotated` / `duplicate_reference` | ยังไม่ได้ใส่เลขอ้างอิง / ซ้ำ | Tools → Annotate Schematic |
| `multiple_net_names` | net เดียวมีหลายชื่อ | two labels on one wire; keep one |
| `different_unit_footprint` | ยูนิตของชิปเดียวกันมี footprint ต่างกัน | set the same footprint on every unit |
| `missing_unit` / `missing_power_pin` | ใช้ชิปหลายยูนิตแต่ไม่ได้วางครบ / ขาไฟไม่ได้วาง | place the power unit (e.g. op-amp unit C) and connect it |
| `lib_symbol_issues` / `lib_symbol_mismatch` | สัญลักษณ์ไม่ตรงกับไลบรารี | update from library, or ignore if intentionally modified locally |
| `footprint_link_issues` | footprint ที่ระบุหาไม่เจอในไลบรารี | fix the library nickname in the Footprint field |
| `endpoint_off_grid` | ปลายสาย/ขาไม่อยู่บนกริด | KiCad grid 50 mil (1.27 mm) for symbols; move to grid |
| `similar_labels` | ชื่อ net คล้ายกันจนน่าจะพิมพ์ผิด (`SDA` vs `sda`) | rename consistently |

## DRC (board)

| type | ความหมาย | Usual fix |
|---|---|---|
| `unconnected_items` | ยังลากลายไม่ครบ (มี ratsnest) | route it; never ship with unconnected items |
| `clearance` | ทองแดงชิดกันเกินกฎ | move/re-route; only lower the net-class clearance if the fab supports it **and** the net isn't mains |
| `shorting_items` | ทองแดงต่างสัญญาณแตะกัน (ช็อต) | real short: fix immediately |
| `track_width` | ลายแคบกว่าค่าต่ำสุด | widen, or check the net class |
| `annular_width` | วงแหวนรอบรูบางเกิน | larger pad/via diameter or smaller drill |
| `drill_out_of_range` / `via_diameter` | รูเจาะเล็ก/ใหญ่เกินที่โรงงานทำได้ | change via size to a fab-supported one |
| `hole_clearance` / `hole_to_hole` | รูชิดทองแดง / รูชิดรู | move the via or the track; drill wander needs margin |
| `copper_edge_clearance` | ทองแดงชิดขอบบอร์ด | keep ≥ fab edge clearance (more for V-score) |
| `courtyards_overlap` | อุปกรณ์วางทับกัน | move parts; overlapping courtyards = pick-and-place collision |
| `missing_courtyard` / `malformed_courtyard` | footprint ไม่มี courtyard | fix the footprint (KLC requires one) |
| `solder_mask_bridge` | สะพาน solder mask ระหว่างแพดแคบเกิน | allowed for fine-pitch ICs if the fab can't hold the web; otherwise space pads |
| `silk_over_copper` | ตัวหนังสือทับแพด | move the text; fabs clip silk on pads anyway, and you lose the label |
| `silk_overlap` / `silk_edge_clearance` | ซิลก์ทับกัน / ชิดขอบ | tidy up; readability matters for assembly and repair |
| `text_height` / `text_thickness` | ตัวหนังสือเล็ก/บางเกินพิมพ์ได้ | raise to fab minimum; Thai text needs more than Latin (see kicad-pcb thai-silkscreen.md) |
| `isolated_copper` | ทองแดงเกาะลอยไม่ต่อกับอะไร | remove islands in zone settings |
| `starved_thermal` | ขา thermal relief ต่อกับ zone น้อยเกิน | add spokes or a via |
| `lib_footprint_mismatch` | footprint บนบอร์ดต่างจากในไลบรารี | update from library unless the change is deliberate |
| `footprint_type_mismatch` | ชนิด SMD/THT ไม่ตรงกับแพดจริง | fix footprint attributes (affects the CPL) |
| `extra_footprint` / `missing_footprint` / `net_conflict` | บอร์ดกับวงจรไม่ตรงกัน (schematic parity) | Tools → Update PCB from Schematic (F8) |
| `invalid_outline` | ขอบบอร์ดไม่ปิด | Edge.Cuts must be one closed shape |
| `creepage` (KiCad 9+) | ระยะตามผิวฉนวนไม่พอ | add distance or a slot; see thai-pcb-compliance |
| `diff_pair_gap_out_of_range` / `length_out_of_range` | คู่สัญญาณ/ความยาวไม่ตามกฎ | re-route with the diff-pair/tune tools |

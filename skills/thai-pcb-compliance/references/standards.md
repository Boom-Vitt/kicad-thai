# Thai regulatory facts for electronics (checked 2026-10-02)

Every line has a source. "UNVERIFIED" means we found only secondary or
conflicting sources: say so to the user and point them to the regulator.
Regulations change: re-check anything that decides money or a launch date.

## TISI / สมอ. (Thai Industrial Standards Institute, สำนักงานมาตรฐานผลิตภัณฑ์อุตสาหกรรม)

| Fact | Source |
|---|---|
| **มอก. 62368 เล่ม 1-2563** = IEC 62368-1:2018 (audio/video, ICT safety). Replaced มอก. 1195-2536. Mandatory (มาตรฐานบังคับ) for a **list of products**, not all electronics: items 1–19 (radio/TV receivers, amplifiers, disc players, game consoles, active speakers, AV players, internet AV receivers, power supplies for electronic appliances…) from **21 Dec 2022**; item 20 (power supplies for mobile phones/tablets) from **17 Oct 2023** | [UL summary](https://taiwan.ul.com/gma/202208-thailand-tisi-announce-tis-62368-part-1-2563-as-mandatory-standard/), [ASEAN regulatory matrix Sep 2025](https://asean.org/wp-content/uploads/2026/04/TH_Updated-Regulatory-Regime_September-2025-Clean.pdf) |
| **มอก. 60335** series = IEC 60335-2-x household appliances; many parts mandatory (e.g. มอก. 60335 เล่ม 2(3)-2567 irons, 2(25) microwave ovens) | ASEAN matrix above |
| Mandatory EMC: only **มอก. 1955-2551** (lighting, based on CISPR 15) appears in the matrix. A mandatory TIS based on CISPR 32 was not found — UNVERIFIED that none exists | ASEAN matrix above |
| Plug/socket configuration **มอก. 166-2549** (Thai 3-round-pin, เต้าเสียบ–เต้ารับ); cord sets (มอก. 2432-2555) must match it | ASEAN matrix above |
| Licences under พ.ร.บ.มาตรฐานผลิตภัณฑ์อุตสาหกรรม พ.ศ. 2511: **ม.20** manufacturing licence (ใบอนุญาตทำ, form มอ.3) before production; **ม.21** import licence (ใบอนุญาตนำเข้า, form มอ.5) before customs release; product carries the มอก. mark + standard number + licensee name/trademark | [NSTDA summary (PDF)](https://waa.inter.nstda.or.th/stks/pub/qri/20250203-tisi.pdf) |
| **มอก. 2368-2564** hazardous substances, aligned with EU RoHS2: **voluntary** (มาตรฐานทั่วไป), effective 6 Jan 2022. Exports to the EU still need EU RoHS 2011/65/EU + 2015/863 | [Enviliance](https://enviliance.com/regions/southeast-asia/th/report_7121) |
| WEEE / EPR law: still a **draft** (latest PCD draft Sep 2025) | [Enviliance](https://enviliance.com/regions/southeast-asia/th/report_14575), [Nation Thailand](https://www.nationthailand.com/news/policy/40061077) |

Official lookup: https://www.tisi.go.th (search the product's มอก. number and
whether it is มาตรฐานบังคับ).

## NBTC / กสทช. (radio equipment, เครื่องโทรคมนาคมและอุปกรณ์)

| Fact | Source |
|---|---|
| Class A: samples tested in an NBTC-recognised lab. Class B: foreign reports (FCC/RED) accepted via a conformity body. **SDoC** (แบบรับรองตนเองของผู้ประกอบการ): self-declaration filed with NBTC, technical file kept for market surveillance | [IB-Lenhardt](https://ib-lenhardt.com/type-approval/thailand) |
| **2.4 GHz (2400–2500 MHz) ≤ 100 mW e.i.r.p.** (WiFi/BLE): licence-exempt to own, use, sell, make, import (ได้รับยกเว้นใบอนุญาต มี ใช้ ค้า ทำ นำเข้า นำออก ตั้ง); SDoC against **กสทช. มท. 1035-2562** (a 1035-2565 revision exists) | [Raspberry Pi Pico W Thai SDoC](https://pip-assets.raspberrypi.com/categories/688-approvals/documents/RP-003617-CF-1-Thailand.pdf), https://standard.nbtc.go.th |
| From **1 Feb 2026** an SDoC for WiFi/BT/SRD must include an electrical safety report (IEC 62368-1 / IEC 60950-1 / มอก. 1561) — test-house source, confirm with NBTC | [5M Global](https://5mglobal.com/nbtc-thailand-mandates-electrical-safety-testing-for-bluetooth-equipment/) |
| **LoRa 920–925 MHz (AS923)**, non-voice, NBTC TS 1033-2560: ≤ 50 mW e.i.r.p. → SDoC; > 50–500 mW → Class A (use still licence-exempt); > 500 mW–4 W → Class A + radio licences | [TCT IoT 920–925 MHz](https://www.tct.or.th/images/article/member/25601214/IoT-in-920-925-MHz-Basic-Info.pdf) |
| 433 MHz: UNVERIFIED (only a forum claim of licence-exempt below ~10 mW) | — |
| Whether a certified module's SDoC covers your finished product: UNVERIFIED — assume the **finished product needs its own SDoC** under its own brand/model | — |

## Product liability (applies even without a mandatory มอก.)

| Fact | Source |
|---|---|
| **พ.ร.บ.ความรับผิดต่อความเสียหายที่เกิดขึ้นจากสินค้าที่ไม่ปลอดภัย พ.ศ. 2551** (Product Liability Act B.E. 2551): manufacturers, importers and sellers can be liable for damage from unsafe products without the injured party proving negligence. Reason to safety-test mains products even when no มอก. is mandatory | law name well known; check details with a lawyer — https://www.krisdika.go.th |

## Mains supply

| Fact | Source |
|---|---|
| MEA (Bangkok, Nonthaburi, Samut Prakan): 230 V single-phase (214–237 V), 400 V three-phase | ASEAN matrix above |
| PEA (rest of Thailand): 220 V (200–240 V), 380 V three-phase | ASEAN matrix above |
| 50 Hz ± 1 % | ASEAN matrix above |
| Thai safety standards are identical adoptions of IEC (62368-1, 60335), so creepage/clearance come from those IEC tables | — |

## Test labs and training in Thailand

| Who | What | Source |
|---|---|---|
| **EEI** สถาบันไฟฟ้าและอิเล็กทรอนิกส์, Bangpoo, Samut Prakan | ISO/IEC 17025, IECEE CB test lab under TISI; safety, EMC, energy efficiency | https://www.thaieei.com/en/service/ |
| **PTEC** ศูนย์ทดสอบผลิตภัณฑ์ไฟฟ้าและอิเล็กทรอนิกส์ (NSTDA), Thailand Science Park, Pathum Thani | EMC, safety, telecom, automotive, medical | [ASEAN listing](https://asean.org/wp-content/uploads/2026/04/Final-Listing-of_PTEC_TL-ao-17042026.pdf) |
| IPC / Global Electronics Association SEA training | IPC-A-610J, J-STD-001J, IPC-A-600, 7711/21, A-620, CID courses in Bangkok and Chiang Mai | https://www.electronics.org/SEA-Training-Calendar-Thailand |

# Making and buying electronics in Thailand (checked 2026-10-02)

Listing a company here is not an endorsement; we only checked that it exists
and what it says it does. Prices, MOQs and lead times: ask the supplier.

## Component shops and distributors

| Name | Type | Notes | Link |
|---|---|---|---|
| บ้านหม้อ (Ban Mo), Phra Nakhon, Bangkok | street of electronics shops | same-day parts, connectors, tools; bring the exact part number | [Yellow Pages](https://www.yellowpages.co.th/catalog/item/จำหน่ายอุปกรณ์อิเล็คทรอนิคส์-04-qaBXuLR) |
| Arduitronics | online, maker modules | site active Oct 2026 | https://www.arduitronics.com/ |
| Cybertice | online, maker modules | same-day shipping, VAT invoices | https://www.cybertice.com/ |
| ThaiEasyElec | online, modules and parts | | https://www.thaieasyelec.com/ |
| Gravitech | parts + PCB design + PCBA, Pathum Thani | | https://www.gravitechthai.com/ |
| DigiKey Thailand | global distributor | THB prices, free shipping from ฿1,600, CPT terms: **buyer pays duty and VAT**, ~4 days | https://www.digikey.co.th/ |
| Mouser, element14/Farnell | global distributors | Thai sites live; check shipping/tax terms at checkout | https://th.mouser.com/ · https://th.element14.com/ |
| LCSC | Chinese distributor (JLCPCB's parts library) | use LCSC part numbers for JLCPCB assembly | https://www.lcsc.com/ |

## PCB fabrication and assembly

| Need | Options |
|---|---|
| Prototypes, 5–100 boards | JLCPCB, PCBWay (China, courier to TH in ~1 week + customs). Use kicad-fab-export. |
| Small-batch PCBA with a Thai contact | Gravitech (Pathum Thani); PCBCart has a factory in Asia Industrial Estate, Samut Prakan (1–10,000+ pcs) — https://www.pcbcart.com/ |
| Volume bare boards made in Thailand | KCE Electronics (Lat Krabang, automotive PCBs, since 1982) and the new BOI-promoted plants: Zhen Ding (Kabin Buri, Prachinburi), Dynamic Electronics, Taihua, Thai Kun Circuit (304 Industrial Park, Prachinburi), WUS Printed Circuit (Rojana, Ayutthaya), Gold Circuit Electronics. These serve OEM volumes, not hobby orders. |
| EMS / contract manufacturing | Cal-Comp, Hana Microelectronics (Lamphun, Ayutthaya), SVI, Benchmark, Fabrinet (Chonburi), Delta Electronics (Thailand) |

We could not verify a purely Thai quick-turn bare-board fab for hobby
quantities. If the user knows one, use the `thai-conservative` DRC preset and
ask the shop for its capability sheet.

Sources: [KCE](https://sg.finance.yahoo.com/quote/NVPA.F/profile),
[Zhen Ding](https://www.nationthailand.com/thailand/general/40034612),
[Dynamic](https://www.yicaiglobal.com/news/dynamic-electronics-to-build-usd2107-million-thai-plant-to-supply-pcbs-for-ai-sector),
[WUS](https://pcdandf.com/pcdesign/index.php/editorial/menu-news/fab-news/16599-wus-printed-circuit-to-spend-280m-on-new-thai-plant),
[Taihua / Thai Kun](https://www.nationthailand.com/pr-news/40057458),
[Gold Circuit](https://www.digitimes.com/news/a20230515PD211.html),
[BOI: 180+ PCB projects, > THB 200 bn, 2022–Jun 2025](https://www.nationthailand.com/business/investment/40062873),
[Fabrinet](https://www.marketbeat.com/instant-alerts/fabrinet-q4-earnings-call-highlights-2026-08-17/).

## Importing boards from JLCPCB / PCBWay

| Fact | Status | Source |
|---|---|---|
| VAT 7 % applies to imported goods of any value, including ≤ ฿1,500, since 5 Jul 2024 | verified for 2024; continuation since then reported, legal instrument for 2025+ unverified | [Kaohoon](https://www.kaohoon.com/news/683923), [Thansettakij](https://www.thansettakij.com/economy/648429) |
| Import **duty** exemption for parcels ≤ ฿1,500 (CIF) abolished from 1 Jan 2026 — duty and VAT from the first baht | reported (DHL, BDO, news); notice number unverified | [BDO](https://www.bdo.global/en-gb/insights/tax/indirect-tax/thailand-new-vat-rules-for-low-value-imported-goods-now-in-effect), [Dailynews](https://www.dailynews.co.th/news/5419832/) |
| Duty rate for bare PCBs (HS 8534) | **UNVERIFIED / conflicting** (one aggregator says 35 % for 8534.00.10; Thailand is in the WTO ITA, which normally means 0 %; ACFTA Form E may give 0 %) | check https://itariff.customs.go.th |
| Assembled boards (PCBA) are usually classified by function, not 8534 | UNVERIFIED | ask the courier/customs broker |
| DHL/FedEx clear the parcel and invoice the receiver for duty + VAT | verified (DHL) | [DHL TH customs](https://www.dhl.com/th-en/home/express/products-and-solutions/products-and-services-overview/customs-services.html) |

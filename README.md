<div align="center">

<img src="assets/banner.png" alt="KiCad Thai ลายวงจร — ปลั๊กอินออกแบบ PCB ด้วย KiCad สำหรับอุตสาหกรรมไทย" width="100%">

<br>

**สั่ง AI ช่วยออกแบบ PCB ด้วย KiCad แบบที่วิศวกรไทยใช้งานจริง: ตรวจ DRC ตามสเปกโรงงาน, export ไฟล์ Gerber/BOM/CPL ส่ง JLCPCB หรือ PCBWay ในคำสั่งเดียว, เช็กลิสต์ มอก./กสทช. และระยะห่างไฟบ้าน 220V, หาโรงงานและอะไหล่ในไทย, ใส่ตัวหนังสือไทยบนบอร์ด**

[![License: MIT](https://img.shields.io/badge/License-MIT-1F7A4D?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/Boom-Vitt/kicad-thai/test.yml?branch=main&style=flat-square&label=tests)](https://github.com/Boom-Vitt/kicad-thai/actions)
[![KiCad](https://img.shields.io/badge/KiCad-8_·_9_·_10-314CB0?style=flat-square&logo=kicad&logoColor=white)](https://www.kicad.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757?style=flat-square&logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins)
[![Codex](https://img.shields.io/badge/Codex-plugin-000000?style=flat-square&logo=openai&logoColor=white)](https://developers.openai.com/codex)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-Cursor_·_Gemini_·_Copilot_·_OpenCode-E2B450?style=flat-square)](https://agentskills.io)
[![GitHub stars](https://img.shields.io/github/stars/Boom-Vitt/kicad-thai?style=flat-square&color=yellow)](https://github.com/Boom-Vitt/kicad-thai/stargazers)

**ไทย** · [English](README.en.md)

[ติดตั้ง](#-ติดตั้ง) · [Skills](#-skills) · [ตัวอย่างคำสั่ง](#-ตัวอย่างคำสั่ง) · [ใช้สคริปต์ตรงๆ](#-ใช้สคริปต์ตรงๆ-ไม่ต้องมี-ai) · [ทดสอบแล้ว](#-ทดสอบกับ-kicad-จริง) · [ร่วมพัฒนา](#-ร่วมพัฒนา)

</div>

---

## 🤔 ทำไมต้อง kicad-thai

AI ช่วยวาดวงจรได้ แต่พอถึงขั้น "ส่งโรงงาน" กับ "ขายในไทย" มักพลาดเรื่องเดิมๆ:

- **ไฟล์ Gerber ขาดชั้นทองแดงโดยไม่มีอะไรเตือน**: ถ้าเลเยอร์ทองแดงถูกตั้งชื่อเอง (เช่น `top_layer`) `kicad-cli --layers F.Cu` จะข้ามเลเยอร์นั้นไปเฉยๆ เราเจอเองใน demo ของ KiCad บน 8.0.9 และ 9.0.9 สคริปต์ในนี้แก้แล้ว และนับไฟล์ทองแดงทุกครั้ง ขาดเมื่อไหร่ก็หยุดทันที
- **BOM ส่ง JLCPCB ไม่ผ่าน**: เจอปัญหา `R1-R3` แบบช่วง, คอลัมน์ไม่ตรง, เลข LCSC อยู่คนละ field, หรือชิ้นที่ DNP หลุดเข้าไปใน BOM
- **ชิ้นส่วนหมุนผิดในไฟล์ CPL**: SOT-23, QFN และชิ้นที่ลงด้านล่าง มีตัวเลือก `--rot` ไว้แก้มุม
- **ไม่รู้ว่าต้องขอ มอก. / กสทช. อะไร** และระยะ creepage/clearance ของไฟ 220V ควรเท่าไหร่
- **ตัวหนังสือไทยบนบอร์ดหายเงียบๆ** ฟอนต์มาตรฐานของ KiCad ไม่มีภาษาไทย และ **KiCad 8 ตัดสระบน สระล่าง และวรรณยุกต์ทิ้งทั้งหมดตอนสร้าง Gerber** ("ผู้ใหญ่" กลายเป็น "ผใหญ") เราทดสอบแล้วว่าต้องใช้ KiCad 9 ขึ้นไป สคริปต์จะเตือนให้อัตโนมัติ
- **กฎ DRC เขียนผิดแต่ KiCad ไม่เตือน** ไฟล์ `.kicad_dru` ที่อ่านไม่ได้จะถูกข้ามไปเฉยๆ แล้ว DRC ก็ "ผ่าน" สคริปต์ตรวจด้วยกฎทดสอบ (canary) ว่ากฎโหลดจริง
- **ไม่รู้จะสั่งผลิตที่ไหน และภาษีนำเข้าเท่าไหร่**: ตั้งแต่ 2024–2026 พัสดุมูลค่าต่ำไม่ได้รับยกเว้น VAT/อากรแล้ว

kicad-thai รวมความรู้เหล่านี้ไว้เป็น [Agent Skills](https://agentskills.io) ที่ Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot และเครื่องมืออื่นใช้ได้ทันที ข้างในมีแค่ `kicad-cli` กับสคริปต์ Python ที่ใช้ไลบรารีมาตรฐานล้วน ทำงานในเครื่องทั้งหมด ไม่ต้องอัปโหลดไฟล์งานไปไหน

## 📦 ติดตั้ง

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude plugin marketplace add Boom-Vitt/kicad-thai
claude plugin install kicad-thai@kicad-thai
```

หรือพิมพ์ในแชต: `/plugin marketplace add Boom-Vitt/kicad-thai` แล้ว `/plugin install kicad-thai@kicad-thai`

</details>

<details open>
<summary><b>Codex</b></summary>

```bash
codex plugin marketplace add Boom-Vitt/kicad-thai
codex plugin add kicad-thai@kicad-thai
```

</details>

<details>
<summary><b>Gemini CLI</b></summary>

```bash
gemini extensions install https://github.com/Boom-Vitt/kicad-thai
```

</details>

<details>
<summary><b>Cursor, GitHub Copilot, OpenCode, Windsurf, Amp และอื่นๆ (ใช้ได้กับเครื่องมือกว่า 70 ตัว)</b></summary>

```bash
npx skills add Boom-Vitt/kicad-thai
```

หรือคัดลอกเองก็ได้: ทุกโฟลเดอร์ใน [`skills/`](skills) ทำงานได้ด้วยตัวเอง ไม่ต้องพึ่งโฟลเดอร์อื่น วางไว้ที่ `~/.claude/skills/`, `~/.agents/skills/` หรือ `.agents/skills/` ในโปรเจกต์

```bash
git clone https://github.com/Boom-Vitt/kicad-thai
cp -r kicad-thai/skills/* ~/.agents/skills/
```

</details>

### สิ่งที่ต้องมีในเครื่อง

| โปรแกรม | จำเป็น | หมายเหตุ |
|---|---|---|
| [KiCad](https://www.kicad.org/download/) 8, 9 หรือ 10 | ✅ | สคริปต์หา `kicad-cli` เองบน macOS, Windows, Linux และ Flatpak |
| Python 3.9+ | ✅ | ใช้แค่ไลบรารีมาตรฐาน ไม่ต้อง `pip install` อะไร |
| ฟอนต์ไทย [Sarabun](https://fonts.google.com/specimen/Sarabun) / Noto Sans Thai | ถ้าจะใส่ตัวหนังสือไทยบนบอร์ด | ใช้ได้ฟรี (OFL) |

## 🧰 Skills

| Skill | ทำอะไร | ทำงานเมื่อพิมพ์ประมาณว่า |
|---|---|---|
| [`kicad-pcb`](skills/kicad-pcb/SKILL.md) | ขั้นตอนออกแบบตั้งแต่ต้นจนจบ, แก้ไฟล์ KiCad อย่างปลอดภัย, แนวทางวางชิ้นส่วนและลากลาย, ตัวหนังสือไทยบนบอร์ด, ความต่างของ KiCad 8/9/10, คำศัพท์ไทย-อังกฤษ | "ออกแบบ PCB", "วาดวงจร", "ลากลาย", "ใส่ตัวหนังสือไทยบนบอร์ด" |
| [`kicad-check`](skills/kicad-check/SKILL.md) | รัน ERC/DRC แบบไม่ต้องเปิดโปรแกรม พร้อมกฎสำเร็จรูปของ JLCPCB, PCBWay และโรงงานไทย อธิบายแต่ละ error เป็นไทย และรีวิว DFM | "ตรวจ DRC", "บอร์ดนี้ผลิตได้ไหม", "เช็กก่อนสั่งผลิต" |
| [`kicad-fab-export`](skills/kicad-fab-export/SKILL.md) | ทำไฟล์ Gerber zip + ไฟล์เจาะ + BOM + CPL ในรูปแบบของ JLCPCB/PCBWay ในคำสั่งเดียว และแก้มุมหมุนชิ้นส่วน | "ส่งโรงงาน", "ไฟล์ส่ง JLCPCB", "ยิง SMT", "ทำ BOM" |
| [`thai-pcb-compliance`](skills/thai-pcb-compliance/SKILL.md) | มอก. 62368/60335/166, กสทช. (WiFi/BLE, LoRa 920–925 MHz, SDoC), creepage/clearance ของไฟ 220V พร้อมกฎ DRC, RoHS, แล็บทดสอบในไทย | "ต้องขอ มอก. ไหม", "ขอ กสทช.", "ไฟบ้านต้องห่างเท่าไหร่" |
| [`thai-pcb-sourcing`](skills/thai-pcb-sourcing/SKILL.md) | เลือกระหว่างสั่งจีนกับโรงงาน/EMS ในไทย, ร้านอะไหล่ (บ้านหม้อ ฯลฯ), เติมเลขชิ้นส่วนใน BOM, คำนวณภาษีนำเข้าและ VAT | "สั่ง PCB ที่ไหน", "ภาษีนำเข้า", "ประกอบบอร์ดในไทย" |

ข้อมูลกฎหมาย มาตรฐาน และบริษัททุกบรรทัดมีลิงก์แหล่งที่มาและวันที่ตรวจ (2 ต.ค. 2026) อะไรที่ยืนยันไม่ได้จะเขียนว่า **UNVERIFIED** ชัดเจน และ AI ถูกสั่งไม่ให้แต่งเลข มอก. หรือกฎ กสทช. ขึ้นมาเอง

## 💬 ตัวอย่างคำสั่ง

```text
ตรวจ DRC บอร์ด hw/sensor.kicad_pro ตามสเปก JLCPCB 2 ชั้น แล้วสรุปเป็นภาษาไทยว่าต้องแก้อะไรก่อน
```
```text
export ไฟล์ส่ง JLCPCB ประกอบ SMT ด้านบน มีชิ้นไหนยังไม่มีเลข LCSC บอกด้วย
```
```text
บอร์ด ESP32 คุมรีเลย์ไฟบ้าน 220V จะขาย 500 ชิ้นในไทย ต้องขอ มอก. หรือ กสทช. อะไร และต้องตั้งระยะห่างใน KiCad ยังไง
```
```text
ใส่ชื่อบริษัทเป็นภาษาไทยบนซิลก์สกรีนด้านหน้า ขนาดที่โรงงานพิมพ์ออกมาได้
```
```text
สั่ง PCBA จาก JLCPCB รวม 110 ดอลลาร์ ต้องจ่ายภาษีนำเข้าเท่าไหร่ หรือมีที่ประกอบในไทยไหม
```

## ⚡ ใช้สคริปต์ตรงๆ (ไม่ต้องมี AI)

```bash
# ERC + DRC พร้อมสรุป (exit 1 ถ้ามี error ใช้ใน CI ได้)
python3 skills/kicad-check/scripts/run_checks.py hw/board.kicad_pro

# ใช้กฎของ JLCPCB (ไฟล์ .kicad_dru ที่มีอยู่แล้วจะไม่ถูกเขียนทับ)
cp -n skills/kicad-check/assets/rules/jlcpcb-2layer.kicad_dru hw/board.kicad_dru

# ไฟล์ส่งโรงงาน: Gerber zip + BOM + CPL (+ STEP)
python3 skills/kicad-fab-export/scripts/export_fab.py hw/board.kicad_pro --fab jlcpcb --step
python3 skills/kicad-fab-export/scripts/export_fab.py hw/board.kicad_pro --fab jlcpcb --rot "SOT-23*=180"
```

กฎ DRC สำเร็จรูปใน [`skills/kicad-check/assets/rules/`](skills/kicad-check/assets/rules): `jlcpcb-2layer`, `jlcpcb-multilayer`, `pcbway-standard`, `thai-conservative` (ค่าแบบปลอดภัยไว้ก่อน สำหรับโรงงานไทยหรือโรงงานที่ไม่รู้สเปก) และ `mains-220v-addon` (creepage/clearance ของไฟบ้าน ใช้ได้ตั้งแต่ KiCad 9)

## ✅ ทดสอบกับ KiCad จริง

ทุกครั้งที่ push CI จะรันสคริปต์กับ **KiCad 8.0.9, 9.0.9 และ 10.0.6** (Docker image ทางการ) โดยใช้โปรเจกต์ demo ของ KiCad เอง คือ `pic_programmer` (2 ชั้น) และ `video` (4 ชั้น) แล้วตรวจว่า:

- Gerber ครบทุกชั้นทองแดง มีขอบบอร์ด และไฟล์เจาะแยก PTH/NPTH
- BOM เป็นรูปแบบของ JLCPCB, ไม่มี designator แบบช่วง และ CPL ได้มุม 0–359 พร้อม Top/Bottom
- STEP export ได้
- กฎ DRC สำเร็จรูปทุกไฟล์โหลดได้จริง (ยืนยันด้วยกฎ canary) และไฟล์กฎที่จงใจเขียนผิดต้องถูกจับได้
- ตัวหนังสือไทยฟอนต์ Sarabun ใน Gerber ซิลก์สกรีน render เป็นภาพให้ตรวจด้วยตา: 9.0.9 และ 10.0.6 ถูกต้อง ส่วน 8.0.9 สระกับวรรณยุกต์หาย

ส่วนการทดสอบแบบไม่ใช้ KiCad (`python3 tests/test_scripts.py`) ใช้ `kicad-cli` จำลอง ตรวจตรรกะ BOM/CPL, กรณีเลเยอร์ถูกเปลี่ยนชื่อ, frontmatter ของ skill และให้ทุก manifest มีเวอร์ชันตรงกัน

## ⚠️ ข้อจำกัด

- ไม่ใช่คำปรึกษาทางกฎหมาย ข้อมูล มอก./กสทช./ภาษีตรวจล่าสุดวันที่ 2 ต.ค. 2026 ก่อนผลิตจริงให้ยืนยันกับ สมอ., กสทช., กรมศุลกากร หรือแล็บทดสอบ (EEI, PTEC)
- ระยะ creepage/clearance ที่ให้ไว้เป็น **ค่าเริ่มต้นสำหรับออกแบบ** ตาม IEC 62368-1 ในเงื่อนไขที่ระบุไว้ ยังไม่ใช่ผลการรับรอง
- การลากลายยังเป็นงานที่ต้องทำใน GUI ส่วน AI จะบอกว่าควรทำอะไรและตรวจผลให้

## 🤝 ร่วมพัฒนา

อ่าน [AGENTS.md](AGENTS.md) ก่อน (โครงสร้างไฟล์, กติกา, วิธีรันเทสต์) ส่ง PR ได้เลย โดยเฉพาะ:
ความสามารถของโรงงาน PCB ในไทย (พร้อมลิงก์), มุมหมุน CPL ที่ใช้ได้จริงกับ JLCPCB และมาตรฐานที่ประกาศใหม่

โปรเจกต์ที่ทำงานร่วมกันได้: [kicad-happy](https://github.com/aklofas/kicad-happy) (DigiKey/Mouser/SPICE/EMC), [KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server) (คุม KiCad ผ่าน MCP)

## License

[MIT](LICENSE) © Boom-Vitt

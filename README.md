# RealIndustry — Mindustry Mod

Mod อุตสาหกรรมจำลองสำหรับ Mindustry ที่อิงจากตารางธาตุและเคมีในโลกจริง
An industry mod based on real-world chemistry, with a full waste-management loop.

- **เข้ากันได้ (Compatible):** Mindustry v7 (build 146) และ v8 — PC และ Android
- **รูปแบบ (Format):** JSON/Hjson เท่านั้น (ไม่มีโค้ด Java)
- **ตรวจสอบแล้ว (Verified):** โหลดสำเร็จบนเซิร์ฟเวอร์ v146 และ v159.7 แบบ headless

## การติดตั้ง (Install)

**PC:** คัดลอกโฟลเดอร์ `RealIndustry` (หรือไฟล์ `RealIndustry.zip`) ไปที่โฟลเดอร์ mods
- Windows: `%appdata%/Mindustry/mods/`
- Linux: `~/.local/share/Mindustry/mods/`
- macOS: `~/Library/Application Support/Mindustry/mods/`

**Android:** เปิดเกม → Settings → Mods → Import From File → เลือก `RealIndustry.zip`

## เนื้อหา (Content)

### แร่ธาตุ 10 ชนิด (10 ores)
bauxite, hematite, chalcopyrite, cassiterite, galena, uraninite, quartz,
graphite, limestone, beryl

### เครื่องจักร 14 ชนิด (14 machines)
| เครื่อง | วัตถุดิบเข้า | ผลผลิต |
|---|---|---|
| เครื่องเจาะโรตารี (rotary-drill) | พลังงาน | แร่ทุกชนิด (tier 7) |
| เตาถลุงทองแดง (copper-smelter) | chalcopyrite 2 | copper 1 + ตะกรัน |
| เตาถลุงเหล็ก (blast-furnace) | hematite 3 + coal 2 | steel 2 + ตะกรัน |
| เตาหลอมโลหะผสม (alloy-furnace) | copper 2 + cassiterite 2 | bronze 2 |
| เตาเผาซีเมนต์ (cement-kiln) | limestone 2 + coal 1 | cement 2 |
| เครื่องอิเล็กโทรไลซิส (electrolysis-plant) | bauxite 4 + graphite 1 | aluminum 1 + กรดใช้แล้ว |
| เครื่องแปรรูปเคมี (chemical-processor) | quartz 2 + coal 1 | silicon 1 + กากตะกอน |
| เครื่องเหวี่ยง (centrifuge) | uraninite 5 | enriched-uranium 1 |
| เตาปฏิกรณ์นิวเคลียร์ (nuclear-reactor) | enriched-uranium | ไฟ 20 u/s (เสถียร ไม่ระเบิด) |
| โรงไฟฟ้าถ่านหิน (coal-generator) | coal | ไฟ 5 u/s |
| เซลล์แบตเตอรี่ (battery-cell) | — | เก็บไฟ 500 u |
| เครื่องรีไซเคิล (recycler) | ตะกรัน (ของเหลว) | gravel 2 |
| เครื่องปรับสภาพของเสีย (neutralizer) | กรดใช้แล้ว + limestone 1 | น้ำ + ปุ๋ย |
| เครื่องอัดกากตะกอน (filter-press) | กากตะกอน | ปุ๋ย |

### อาวุธ 4 อัน (4 turrets)
| ปืน | กระสุน | ลักษณะ |
|---|---|---|
| ปืนกลบรอนซ์ (bronze-gun) | copper / bronze | ปืนกลพื้นฐาน ยิงได้ทั้งบก-อากาศ |
| ปืนใหญ่เหล็กกล้า (steel-howitzer) | steel | ครกระเบิดเนื้อแรง ยิงโค้ง ไม่ตีอากาศ |
| ปืนฟลัคอะลูมิเนียม (aluminum-flak) | aluminum | ต่อต้านอากาศยานเท่านั้น |
| ปืนเรลแกนยูเรเนียม (uranium-lance) | enriched-uranium | เรลแกนทะลุ 3 เป้า ยุคอะตอม |

### หุ่นรบ (units)
โรงงานหุ่นรบ (unit-factory) ผลิตได้ 3 แบบ:
- ครอว์เลอร์บรอนซ์ (bronze-crawler) — หุ่นพื้นเบา ราคาถูก
- วอสป์อะลูมิเนียม (aluminum-wasp) — หุ่นบินเร็ว ปืนกลคู่
- บรอว์เลอร์เหล็กกล้า (steel-brawler) — หุ่นพื้นหนัก เกราะ 6

### กำแพง 5 แบบ (walls)
cement-wall / bronze-wall / steel-wall / steel-wall-large (2x2) / aluminum-wall (กันลำแสง)

### แกนกลาง 2 ชั้น (cores)
- แกนฐานอินดัสทรี (core-industry) 3x3 — แกนเริ่มต้นของโมดูล +2 วงเงินหุ่น
- แกนป้อมฟอร์เทรส (core-fortress) 4x4 — ยุคอะตอม +6 วงเงินหุ่น

### การวิจัย (Research)
ทุกโหนดใช้ต้นทุนวัตถุ RealIndustry (bronze/steel/aluminum/enriched-uranium/cement/gravel)
มี 3 ราก: เครื่องเจาะโรตารี, แกนอินดัสทรี — แยกย่อยตามยุคโลหะ → ไฟฟ้า → อะตอม

### ระบบของเสีย (Waste system)
ของเสีย 3 ชนิดเป็นของเหลว: **ตะกรัน (slag)**, **กรดใช้แล้ว (spent-acid)**, **กากตะกอน (waste-sludge)**
- เครื่องจะ**หยุดทำงานเอง**เมื่อของเสียล้น (ต่อท่อส่งออกไปจัดการ)
- ตะกรันใช้ของเหลว slag ของเกม ส่งด้วยท่อ (conduit) ไปที่เครื่องรีไซเคิล
- ใช้ท่อแยกสำหรับของเสียแต่ละชนิด อย่าให้ปนกัน

## การวิจัย (Research)
ยุคโลหะ → ยุคไฟฟ้า → ยุคอะตอม เริ่มจาก `เครื่องเจาะโรตารี` (แผนวิจัยของโมดูแยกจากแผนปกติ)

## ข้อจำกัดสำคัญ (Ore spawning)
แร่ใหม่**ไม่่เกิดขึ้นเอง**บนแผนที่แคมเปญปกติ (การแก้ planet generation ต้องใช้ Java)
วิธีทดสอบ/เล่น:
1. เปิด Sandbox/Editor → วาดแร่ด้วยเครื่องมือ Floor/Overlay (ค้นหา "ore-bauxite" ฯลฯ)
2. หรือใช้แผนที่ที่สร้างจาก editor ที่มีแร่วางไว้

## โครงสร้าง (Structure)
```
mod.hjson            ข้อมูลโมดู
content/items/       ไอเทม 16 ชนิด
content/liquids/     ของเหลว 3 ชนิด
content/blocks/      เครื่องจักร 13 + แร่ 10
sprites/             ไอคอนและสไปรต์ (สร้างด้วย tools/gen_sprites.py)
```

ปรับแต่งค่าสมดุล: แก้ตัวเลข `craftTime` (หน่วย tick, 60 = 1 วินาที), `consumePower`
(หน่วยต่อ tick, u/s ÷ 60), และปริมาณของเหลวในไฟล์ `content/blocks/*.hjson`

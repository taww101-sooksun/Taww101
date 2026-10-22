นำเข้า base64
นำเข้าปฏิทิน
นำเข้า itertools
นำเข้า json
นำเข้า mimetypes
นำเข้าแบบสุ่ม
นำเข้าคณิตศาสตร์
จากการนำเข้า datetime, date, datetime
จาก pathlib นำเข้า Path

import streamlit as st
import streamlit.components.v1 as components


# ========================================================
# หมายเลขลึกลับของ SYNAPSE
# ========================================================

APP_DIR = Path(__file__).resolve().parent
นามสกุลไฟล์เพลง = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac"}

เดือนไทย = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
    "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
    "กันยายน", "ที่นี่", "พฤศจิกายน", "ธันวาคม"
]

#ตามกติกาที่กำหนด: วันจันทร์ = 1
หมายเลขวัน = {
    0: 1, # วันจันทร์
    1:2, #วันอังคาร
    2: 3, # วันพุธ
    3: 4, # วันพฤหัสบดี
    4:5, #วันศุกร์
    5: 6, # วันเสาร์
    6:7, #วันอาทิตย์
}

THAI_WEEKDAYS = [
    "วันจันทร์", "อังคาร", "พุธ"
    "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"
]

st.set_page_config(
    page_title="SYNAPSE MYSTIC NUMBER",
    page_icon="🔮",
    เลย์เอาต์="กว้าง"
    initial_sidebar_state="ยุบ"
)


# ========================================================
# สไตล์นีออน
# ========================================================

st.markdown("""
<style>
:root {
    --syn-bg: #050814;
    --syn-panel: #0b1428;
    --syn-blue: #63f4ff;
    --syn-gold: #ffe66d;
    --syn-red: #d94a5a;
    --syn-silver: #e8edf5;
    --syn-muted: #a8b7d9;
}
.stApp {
    พื้นหลัง:
      radial-gradient(ellipse at 10% 0%, #102c45 0%, transparent 36%),
      radial-gradient(ellipse at 90% 15%, #351522 0%, transparent 32%),
      linear-gradient(145deg, #050814, #080d1b 55%, #120b16);
    สี: var(--syn-silver);
}
ส่วนหัว [data-testid = "stHeader"] { พื้นหลัง: rgba (0,0,0,0); }
h1, h2, h3 {
    สี: var(--syn-blue) !important;
    เงาข้อความ: 0 0 10px #63f4ff55;
}
p, label, .stMarkdown { color: #e1eaff; }
.hero {
    จัดแนวข้อความ: กึ่งกลาง;
    padding: 24px 10px;
    ขอบโค้งมน: 22px;
    เส้นขอบ: var ทึบ 1px (--syn-gold);
    พื้นหลัง: การไล่ระดับสีเชิงเส้น (130 องศา, #091629, #21121c, #0a1728);
    box-shadow: 0 0 18px #63f4ff20, inset 0 0 20px #ffe66d10;
    ระยะขอบล่าง: 18px;
}
.hero-title {
    ขนาดตัวอักษร: แคลมป์(24px, 5vw, 40px);
    น้ำหนักตัวอักษร: 900;
    ระยะห่างระหว่างตัวอักษร: 2px;
    สี: var(--syn-gold);
    text-shadow: 0 0 8px #ffe66d66, 0 0 22px #63f4ff55;
}
.hero-sub {
    ขนาดตัวอักษร: 12px;
    ระยะห่างระหว่างตัวอักษร: 2px;
    สี: var(--syn-blue);
    ระยะขอบบน: 8px;
}
.neon-card {
    พื้นหลัง: การไล่ระดับสีเชิงเส้น (135 องศา, #0a1426, #17131d);
    ขอบ: 1px ทึบ #63f4ff80;
    ขอบโค้งมน: 16px;
    ระยะห่าง: 14px;
    ระยะขอบ: 8px 0;
    เงาของกล่อง: 0 0 10px #63f4ff18;
}
.neon-number {
    ขนาดตัวอักษร: 27px;
    น้ำหนักตัวอักษร: 900;
    สี: var(--syn-gold);
    เงาข้อความ: 0 0 10px #ffe66d66;
    จัดแนวข้อความ: กึ่งกลาง;
}
.neon-label { color: var(--syn-blue); font-size: 13px; text-align: center; }
[data-testid="stMetric"] {
    พื้นหลัง: การไล่ระดับสีเชิงเส้น (135 องศา, #0b1830, #20151e);
    ขอบ: 1px ทึบ #ffe66d70;
    ขอบโค้งมน: 14px;
    ระยะห่าง: 14px;
    เงาของกล่อง: 0 0 12px #63f4ff15;
}
[data-testid="stMetricValue"] { สี: var(--syn-gold) !สำคัญ; }
[data-testid="stMetricLabel"] { สี: var(--syn-blue) !สำคัญ; }
div.stButton > ปุ่ม, div.stDownloadButton > ปุ่ม {
    สี: #f5f7ff;
    พื้นหลัง: การไล่ระดับสีเชิงเส้น (110 องศา, #102d43, #38202a);
    เส้นขอบ: var ทึบ 1px (--syn-blue);
    ขอบโค้งมน: 12px;
    เงาของกล่อง: 0 0 8px #63f4ff25;
    การเปลี่ยนผ่าน: ทั้งหมด 0.2 วินาทีอย่างราบรื่น;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    สีขอบ: var(--syn-gold);
    สี: #ffffff;
    เงาของกล่อง: 0 0 14px #ffe66d40;
}
input, textarea, [data-baseweb="select"] > div {
    สีขอบ: #63f4ff70 !สำคัญ;
}
hr { border-color: #34465b; }
.small-note { color: var(--syn-muted); font-size: 12px; }
</style>
<div class="hero">
  <div class="hero-title">✦ หมายเลขลึกลับของ SYNAPSE ✦</div>
  <div class="hero-sub">วันที่ • ข้างขึ้นข้างแรม • เมทริกซ์ตัวเลข • เพลงนีออน</div>
</div>
""", unsafe_allow_html=True)


# ========================================================
# ฟังก์ชันการคำนวณ
# ========================================================

def last_digit(n):
    """ใช้มูลค่า ยกเว้นองค์ประกอบ"""
    คืนค่า abs(int(n)) % 10


def lunar_estimate(d):
    """
    กระดานดำจันทร์จากกระดานดำ
    การค้นหาข้อมูลทางโทรศัพท์ไทย
    """
    อ้างอิง = datetime(2000, 1, 6, 18, 14)
    target = datetime(d.year, d.month, d.day, 12, 0)
    รอบ = 29.530588853
    อายุ = ((เป้าหมาย - อ้างอิง).จำนวนวินาทีทั้งหมด() / 86400) % รอบ

    #เด็กจันทร์ 0-14.999 = เวลาที่เหลือขึ้นโดยประมาณ
    ถ้าอายุ < รอบ / 2:
        side = "ด้านข้างขึ้น"
        วันจันทร์ = min(15, max(1, int(อายุ) + 1))
    อื่นๆ:
        side = "ข้างแรม"
        อายุที่ลดลง = อายุ - รอบ / 2
        lunar_day = min(15, max(1, int(waning_age) + 1))

    ความสว่าง = (1 - math.cos(2 * math.pi * อายุ / รอบ)) / 2 * 100

    ถ้าอายุ < 1.85 หรืออายุ >= 27.68:
        phase = "เดือนดับ"
    ถ้าอายุ < 7.38:
        phase = "จันทร์เสี้ยวข้างขึ้น"
    ถ้าอายุ < 11.07:
        phase = "เฟสลูดวงข้างขึ้น"
    ถ้าอายุ < 14.77 ปี:
        phase = "เฟสวันเพ็ญ"
    ถ้าอายุ < 18.46 ปี:
        phase = "จันทร์เกือบเต็มดวงข้างแรม"
    ถ้าอายุ < 22.15:
        phase = "เฟสลูดวงข้างแรม"
    อื่นๆ:
        phase = "จันทร์เสี้ยวข้างแรม"

    ส่งคืน {
        "อายุ": ปัดเศษ(อายุ, 2),
        "ด้าน": ด้านข้าง
        "day": lunar_day,
        "phase": phase,
        "illumination": round(illumination, 1),
    }


def create_four_numbers(day_number, lunar_number):
    """
    การจัดองค์ประกอบชั้น 4 ตัวอย่าง:
    1. เรียงใหม่
    2. การกำหนดตำแหน่งข้างขึ้น/ข้างแรม
    3. ผลบวกองค์ประกอบ
    4. ผลต่างองค์ประกอบ มูลค่า มูลค่า มูลค่า มูลค่า
    """
    การบวก = หลักสุดท้ายของ (หมายเลขวัน + หมายเลขจันทรคติ)
    การลบ = หลักสุดท้ายของ (เลขจันทรคติ - เลขวัน)

    ส่งคืน [
        หมายเลขวัน
        เลขจันทรคติ
        นอกจากนี้
        การลบ
    ]


def create_48_doors(numbers):
    """
    3 คน: การเรียงสับเปลี่ยนของเลข 4 คนที่ชื่อ 3 ตำแหน่ง = 24 ชุด
    2 คนที่: เลือกคู่โดยไม่ซ้ำแล้วสร้างเลขตรงและเลขกลับ
    """
    ตัวเลขสามหลัก = [
        "".join(map(str, p))
        สำหรับ p ใน itertools.permutations(numbers, 3)
    ]

    pairs = list(itertools.combinations(numbers, 2))
    two_digit_top = [
        "".join(map(str, pair))
        สำหรับคู่ในคู่
    ]
    two_digit_bottom = [
        ค่า[::-1] สำหรับค่าในสองหลักบนสุด
    ]

    ส่งคืนค่าสามหลัก, ตัวเลขสองหลักด้านบน, ตัวเลขสองหลักด้านล่าง


def find_music_files():
    ถ้า APP_DIR ไม่มีอยู่:
        ส่งคืน []
    ส่งคืนเรียงลำดับ (
        [
            p สำหรับ p ใน APP_DIR.iterdir()
            ถ้า p.is_file() และ p.suffix.lower() อยู่ใน MUSIC_EXTENSIONS
        ],
        key=lambda p: p.name.lower()
    )


# ========================================================
# ช่องป้อนวันที่
# ========================================================

st.header("📅 รับวันเพื่อทำอาหาร")

วันนี้ = date.today()
current_be = today.year + 543

c1, c2, c3 = st.columns(3)

ด้วย c1:
    day_value = st.selectbox(
        "องค์ประกอบ",
        ช่วง (1, 32)
        index=today.day - 1
    )

ด้วย c2:
    ค่าเดือน = st.selectbox(
        "เดือน"
        ช่วง (1, 13)
        index=today.month - 1,
        format_func=lambda x: THAI_MONTHS[x - 1]
    )

ด้วย c3:
    year_options = list(range(current_be - 100, current_be + 11))
    year_be = st.selectbox(
        "ปี พ.ศ.",
        ตัวเลือกปี
        index=year_options.index(current_be)
    )

ปีหลัง = ปีเกิด - 543
max_day = calendar.monthrange(year_ad, month_value)[1]

ถ้า day_value > max_day:
    st.error(f"เดือนนี้มีเพียง {max_day} วันที่วันที่ใหม่")
    chosen_date = None
อื่นๆ:
    chosen_date = date(year_ad, month_value, day_value)


# ========================================================
# ป้อนเลขจันทรคติ
# ========================================================

ถ้า chosen_date:
    d = chosen_date
    weekday_name = THAI_WEEKDAYS[d.weekday()]
    day_number = DAY_NUMBERS[d.weekday()]
    ดวงจันทร์ = ประมาณการดวงจันทร์(d)

    st.divider()
    st.header("🌙 เลื่อนไปทางขวาใกล้ด้านบน– ใกล้แรม")

    st.caption(
        "ระบบจัดการข้อมูลให้ถูกต้อง"
        "องค์ประกอบและองค์ประกอบนี้เองที่มันทำงาน"
    )

    l1, l2 = st.columns(2)

    ด้วย l1:
        lunar_side = st.selectbox(
            "องค์ประกอบเว็บเพจ",
            [" ข้างขึ้น", " ข้างแรม"],
            index=0 ถ้า lunar["side"] == "ข้างขึ้น" else 1
        )

    ด้วย l2:
        lunar_number = st.selectbox(
            "องค์ประกอบเว็บเพจ (1–15)",
            ช่วง (1, 16)
            index=lunar["day"] - 1
        )

    st.markdown(
        f"""
        <div class="neon-card">
          <div class="neon-label">ป้ายไฟ</div>
          <div class="neon-number">{weekday_name}</div>
          <div class="neon-label">
            {d.day} {THAI_MONTHS[d.month - 1]} พ.ศ. {วันปี + 543}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)
    a.metric("จำนวนวัน", day_number)
    b.metric("ตัวเลขข้างขึ้น/ข้างแรม", lunar_number)
    c.metric("ดวงจันทร์สว่าง", f'{lunar["illumination"]}%')

    st.caption(
        f" อายุจันทร์ตามปกติ {lunar['age']} วัน · {lunar['phase']}. "
        "การเลื่อนนี้ไม่ใช่การเลื่อนตามการเลื่อนไทย"
    )

    # ------------------------------------------------------
    # หมายเลขเมล็ดพันธุ์ทั้งสี่
    # ------------------------------------------------------

    st.divider()
    st.header("🔢 สูตรคำนวณเลขตั้งต้น 4 คน")

    four_numbers = create_four_numbers(day_number, lunar_number)

    plus_result = หมายเลขวัน + หมายเลขจันทรคติ
    ผลลัพธ์ลบ = เลขจันทรคติ - เลขวัน

    st.markdown(
        f"""
        <div class="neon-card">
          <div class="neon-label">ป้ายไฟ</div>
          <div class="neon-number">{day_number}</div>
          <div class="neon-label"> ด้านข้าง {lunar_side}</div>
          <div class="neon-number">{lunar_number}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    f1, f2 = st.columns(2)

    ด้วย f1:
        st.markdown("### ➕ สูตรบวก")
        st.write(f"{day_number} + {lunar_number} = {plus_result}")
        st.write(f"ลำดับหลัก: **{last_digit(plus_result)}**")

    ด้วย f2:
        st.markdown("### ➖ สูตรลบ")
        st.write(f"{lunar_number} − {day_number} = {minus_result}")
        st.write(f" ค่าสุดท้าย ตัวเลขหลัก: **{last_digit(minus_result)}**")

    st.markdown("### ✨เลขตั้งต้น 4 คน")

    seed_cols = st.columns(4)
    สำหรับคอลัมน์ ตัวเลข ป้ายกำกับในรหัสไปรษณีย์(
        seed_cols,
        ตัวเลขสี่ตัว
        ["เลขวัน", "เลขหน่วยความจำ", "เลขบวก", "เลขลบ"]
    ):
        ด้วย col:
            st.markdown(
                f"""
                <div class="neon-card">
                  <div class="neon-label">{label}</div>
                  <div class="neon-number">{number}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    ถ้าความยาวของชุดตัวเลขสี่ตัวไม่เท่ากับ 4:
        st.warning(
            "องค์ประกอบต้นมีองค์ประกอบกัน ระบบกราฟิกชุดที่บล็อกทั้งหมด"
            "แต่บางชุดบางชุดบางชุดบางชุด"
        )

    # ------------------------------------------------------
    # 48 ประตู
    # ------------------------------------------------------

    three_numbers, two_top, two_bottom = create_48_doors(four_numbers)

    st.divider()
    st.header("🚪 ธีมชุด")

    st.markdown(
        "### 🔷 3 คนบน — 24 ชุด"
    )
    st.caption("เรียงตามลำดับเลขตั้งต้น 4 ตัวอักษรในส่วนที่ 3 ตำแหน่ง")

    สำหรับการเริ่มต้นในช่วง (0, ความยาวของตัวเลขสามตัว) 6:
        cols = st.columns(6)
        สำหรับ col, value ใน zip(cols, three_numbers[start:start + 6]):
            ด้วย col:
                st.markdown(
                    f"""
                    <div class="neon-card">
                      <div class="neon-number">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("### 🟣 2 คนบน–ล่าง — 12 รายการ")

    pair_rows = list(zip(two_top, two_bottom))
    สำหรับการเริ่มต้นในช่วง (0, ความยาวของคู่แถว), 3:
        cols = st.columns(3)
        สำหรับคอลัมน์ (บนสุด, ล่างสุด) ใน zip(คอลัมน์, pair_rows[start:start + 3]):
            ด้วย col:
                st.markdown(
                    f"""
                    <div class="neon-card">
                      <div class="neon-label">บน ↔ ล่าง</div>
                      <div class="neon-number">{top} ↔ {bottom}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.divider()
    st.header("💠 ส่วนหัวของหน้าเว็บ")

    s1, s2, s3 = st.columns(3)
    s1.metric("3 คนบน", f"{len(three_numbers)} ชุด")
    s2.metric("2 คนบน", f"{len(two_top)} ชุด")
    s3.metric("2 ตัวล่าง", f"{len(two_bottom)} ชุด")

    total_doors = len(three_numbers) + len(two_top) + len(two_bottom)
    st.metric("รวมทั้งหมด", f"{total_doors} รายการ")

    st.caption(
        "หากคิดรายการละ 1 บาทจะเป็นยอดสมมติ "
        f"{total_doors} ประตูทั้งหมดมีผล"
    )

    # ------------------------------------------------------
    # ส่งออก CSV
    # ------------------------------------------------------

    export_rows = [
        ["หน้าเว็บ", "หน้าเว็บ"],
    ]
    Export_rows += [["3 คนบน", n] สำหรับ n ใน three_numbers]
    Export_rows += [["2 คนบน", n] สำหรับ n ใน two_top]
    Export_rows += [["2 คนล่าง", n] สำหรับ n ใน two_bottom]

    csv_text = "\ufeff" + "\n".join(
        f'"{row[0]}","{row[1]}"' สำหรับแถวใน export_rows
    )

    st.download_button(
        "⬇️ ดาวน์โหลดชุดไฟล์ CSV",
        data=csv_text.encode("utf-8"),
        file_name=f"numbers_{d.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )


# ========================================================
# เครื่องเล่นเพลงนีออน
# ========================================================

st.divider()
st.header("🎧 เครื่องเล่นเพลง SYNAPSE NEON")

music_files = find_music_files()

st.caption(
    " ฝังไฟล์เพลง อัปโหลดไฟล์ Ta_app.py "
    "รองรับ MP3, WAV, OGG, M4A, AAC และ FLAC"
)

ถ้าไม่ใช่ไฟล์เพลง:
    st.warning(
        "ยังไม่พบไฟล์เพลงเพิ่มไฟล์เพลงใน GitHub "
        "องค์ประกอบ Ta_app.py"
    )
อื่นๆ:
    st.success(f" โหลดเพลง {len(music_files)} เพลง")

    ด้วย st.expander("📜 รายการเพลงทั้งหมด", Extended=True):
        สำหรับ index, music_file ใน enumerate(music_files, start=1):
            st.write(f"{index}. 🎵 {music_file.name}")

    # ฝังแทร็กไว้ใน iframe เดียว วิธีนี้ช่วยหลีกเลี่ยงการแทนที่โหนด DOM
    # ในหน้า Streamlit หลัก
    แทร็ก = []

    สำหรับไฟล์เพลงแต่ละไฟล์ในโฟลเดอร์ music_files:
        ลองดู:
            mime, _ = mimetypes.guess_type(music_file.name)
            ถ้าไม่ใช่ mime หรือไม่ใช่ mime.startswith("audio/"):
                mime = "audio/mpeg"

            เข้ารหัส = base64.b64encode(
                music_file.read_bytes()
            ).decode("ascii")

            tracks.append({
                "name": music_file.name,
                "mime": mime,
                "ข้อมูล": เข้ารหัส
            })
        ยกเว้น OSError:
            st.warning(f" อ่านไฟล์ไม่จริง: {music_file.name}")

    ถ้าติดตาม:
        tracks_json = json.dumps(tracks, ensure_ascii=True)

        player_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
เนื้อหา {
  ระยะขอบ: 0;
  ระยะห่าง: 8px;
  สี: #e8edf5;
  พื้นหลัง: โปร่งใส;
  ตระกูลฟอนต์: Arial, sans-serif;
}
.player {
  ขอบ: 1px ทึบ #ffe66d;
  ขอบโค้งมน: 18px;
  ระยะห่าง: 16px;
  พื้นหลัง: linear-gradient(135deg,#091629,#21121c,#101b2b);
  เงาของกล่อง: 0 0 16px #63f4ff22;
}
.title {
  สี: #63f4ff;
  ขนาดตัวอักษร: 18px;
  น้ำหนักตัวอักษร: 900;
  เงาข้อความ: 0 0 10px #63f4ff;
}
.track {
  สี: #ffe66d;
  ระยะขอบ: 10px 0;
  overflow-wrap: anywhere;
}
.status {
  สี: #a8b7d9;
  ขนาดตัวอักษร: 12px;
  ระยะขอบ: 8px 0;
}
เสียง { ความกว้าง: 100%; ระยะขอบ: 8px 0; }
ปุ่ม {
  สี: #fff;
  พื้นหลัง: #102d43;
  ขอบ: 1px ทึบ #63f4ff;
  ขอบโค้งมน: 10px;
  padding: 10px 12px;
  ระยะขอบ: 3px;
}
ปุ่ม:เมื่อวางเมาส์เหนือปุ่ม { พื้นหลัง: #38202a; }
.list {
  ระยะขอบบน: 12px;
  ความสูงสูงสุด: 155px;
  overflow-y: auto;
  ขอบบน: 1px ทึบ #34465b;
  padding-top: 8px;
}
.item {
  ขนาดตัวอักษร: 12px;
  ระยะห่าง: 7px;
  สี: #e8edf5;
  ขอบโค้งมน: 7px;
  overflow-wrap: anywhere;
}
.item.active {
  สี: #ffe66d;
  พื้นหลัง: #20151e;
  ขอบ: 1px ทึบ #ffe66d;
}
.note {
  สี: #a8b7d9;
  ขนาดตัวอักษร: 11px;
  line-height: 1.5;
}
</style>
</head>
<body>
<div class="player">
  <div class="title">✦ NEON MUSIC ✦</div>
  <div id="track" class="track">เล่นเพลง...</div>
  <audio id="audio" controls playsinline></audio>
  <div>
    <button id="play">▶ เล่น</button>
    <button id="pause">⏸ห</button>
    <button id="next">⏭ เพลงถัดไป</button>
    <button id="shuffle">🔀 สับเปลี่ยนใหม่</button>
  </div>
  <div id="status" class="status"></div>
  <div id="list" class="list"></div>
  <p class="note">
    เพลงจะเล่นและเล่นเพลงเมื่อเพลงจบ
    ถ้าบล็อกการเล่นอัตโนมัติให้แตะปุ่ม ▶ เล่นก่อนแสดง
  </p>
</div>
<script>
const tracks = TRACKS_PLACEHOLDER;
const audio = document.getElementById("audio");
const trackLabel = document.getElementById("track");
const statusLabel = document.getElementById("status");
const list = document.getElementById("list");

ให้ลำดับ = [];
กำหนดให้ตำแหน่งเท่ากับ 0;
ให้ค่าปัจจุบันเท่ากับ -1;
let userStarted = false;

ฟังก์ชัน shuffleArray(array) {
  const result = array.slice();
  สำหรับ (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  ส่งคืนผลลัพธ์;
}

ฟังก์ชัน makeOrder() {
  ลำดับ = สุ่มสลับอาร์เรย์แทร็ก (tracks.map((_, i) => i));
  ถ้า (ความยาวลำดับ > 1 และ ลำดับที่ 0 === ปัจจุบัน) {
    [order[0], order[1]] = [order[1], order[0]];
  }
  ตำแหน่ง = 0;
}

ฟังก์ชัน renderList() {
  list.replaceChildren();
  tracks.forEach((item, i) => {
    const row = document.createElement("div");
    row.className = "item" + (i === current ? " active" : "");
    row.textContent = (i + 1) + ". " + item.name;
    row.addEventListener("click", () => {
      userStarted = true;
      playIndex(i, true);
    });
    list.appendChild(row);
  });
}

ฟังก์ชันอะซิงโครนัส playIndex(index, attemptPlay) {
  ถ้า (!tracks.length) ให้คืนค่า;
  ปัจจุบัน = ดัชนี;
  const item = tracks[index];

  trackLabel.textContent =
    "กำลังเลือก: " + item.name + " (" + (index + 1) + "/" +tracks.length + ")";

  audio.src = "data:" + item.mime + ";base64," + item.data;
  audio.load();
  renderList();

  ถ้า (attemptPlay) {
    ลอง {
      await audio.play();
      statusLabel.textContent = "เล่นเพลง";
    } catch (error) {
      statusLabel.textContent =
        "องค์ประกอบเล่นได้ ยกเว้นองค์ประกอบเล่นได้";
    }
  }
}

ฟังก์ชัน nextTrack() {
  ถ้า (!tracks.length) ให้คืนค่า;
  ถ้า (position >= order.length) ให้สร้างคำสั่งซื้อ (makeOrder())

  ดัชนีคงที่ = ลำดับ[ตำแหน่ง];
  ตำแหน่ง += 1;
  playIndex(index, userStarted);
}

document.getElementById("play").addEventListener("click", async () => {
  userStarted = true;
  ลอง {
    ถ้า (current < 0) {
      nextTrack();
    } มิฉะนั้น {
      await audio.play();
      statusLabel.textContent = "เล่นเพลง";
    }
  } catch (error) {
    statusLabel.textContent = "เล่นไม่ได้โปรดลองเลือกเพลงจากรายชื่อ";
  }
});

document.getElementById("pause").addEventListener("click", () => {
  audio.pause();
  statusLabel.textContent = "สถานะ";
});

document.getElementById("next").addEventListener("click", () => {
  userStarted = true;
  nextTrack();
});

document.getElementById("shuffle").addEventListener("click", () => {
  makeOrder();
  userStarted = true;
  nextTrack();
});

audio.addEventListener("ended", () => {
  nextTrack();
});

audio.addEventListener("ข้อผิดพลาด", () => {
  statusLabel.textContent =
    "ไฟล์นี้เล่นไม่ได้ ไฟล์ MP3 หรือ WAV ได้ตรวจสอบไฟล์อีกครั้ง";
});

makeOrder();
renderList();

// ลอง


from datetime import date, datetime
from pathlib import Path
import calendar
import math
import io
import csv

import streamlit as st

# =========================================================
# SYNAPSE MYSTIC NUMBER
# Date calculator - Streamlit
# =========================================================

st.set_page_config(
    page_title="SYNAPSE | MYSTIC NUMBER",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- THEME ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Noto+Sans+Thai:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans Thai', sans-serif;
}
.stApp {
    background:
        radial-gradient(ellipse at 15% 0%, #10244a 0%, transparent 40%),
        radial-gradient(ellipse at 90% 15%, #32141e 0%, transparent 35%),
        linear-gradient(145deg, #03050b, #090d19 55%, #03050b);
    color: #f2f5ff;
}
.block-container {
    max-width: 1200px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #f4d68a !important;
}
.synapse-title {
    font-family: 'Orbitron', sans-serif;
    text-align: center;
    font-size: clamp(28px, 5vw, 48px);
    font-weight: 800;
    letter-spacing: 5px;
    background: linear-gradient(90deg, #5bbcff, #f5df9b, #ff626b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.synapse-subtitle {
    text-align: center;
    color: #78caff;
    letter-spacing: 3px;
    font-size: 13px;
    margin-bottom: 20px;
}
.panel {
    background: linear-gradient(135deg, rgba(15,27,49,.96),
        rgba(8,11,23,.96));
    border: 1px solid #244b78;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 0 22px rgba(27,117,255,.08);
}
.metric-card {
    background: linear-gradient(140deg, #111d32, #0a0e1b);
    border: 1px solid #244a73;
    border-radius: 14px;
    padding: 16px;
    min-height: 112px;
}
.metric-label {
    color: #9cb1d1;
    font-size: 13px;
    margin-bottom: 7px;
}
.metric-value {
    color: #f2d58a;
    font-size: clamp(19px, 3vw, 28px);
    font-weight: 700;
    overflow-wrap: anywhere;
}
.metric-note {
    color: #70c9ff;
    font-size: 12px;
    margin-top: 5px;
}
div.stButton > button {
    background: linear-gradient(100deg, #104b91, #176fba);
    color: white;
    border: 1px solid #6fcaff;
    border-radius: 10px;
    font-weight: 600;
    min-height: 44px;
}
div.stButton > button:hover {
    border-color: #f4d68a;
    color: #f4d68a;
    box-shadow: 0 0 15px #1265a866;
}
[data-testid="stSidebar"] {
    background: #080d19;
    border-right: 1px solid #233d62;
}
hr { border-color: #243c60; }
.small-note {
    color: #a4b1c9;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------- THAI DATE HELPERS ----------
THAI_DAYS = [
    "วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี",
    "วันศุกร์", "วันเสาร์", "วันอาทิตย์"
]
THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
    "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
    "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]
THAI_ANIMALS = [
    "ชวด (หนู)", "ฉลู (วัว)", "ขาล (เสือ)", "เถาะ (กระต่าย)",
    "มะโรง (งูใหญ่)", "มะเส็ง (งู)", "มะเมีย (ม้า)",
    "มะแม (แพะ)", "วอก (ลิง)", "ระกา (ไก่)",
    "จอ (สุนัข)", "กุน (หมู)"
]
THAI_ZODIAC = [
    ("มังกร", (1, 1), (1, 19)),
    ("กุมภ์", (1, 20), (2, 18)),
    ("มีน", (2, 19), (3, 20)),
    ("เมษ", (3, 21), (4, 19)),
    ("พฤษภ", (4, 20), (5, 20)),
    ("เมถุน", (5, 21), (6, 20)),
    ("กรกฎ", (6, 21), (7, 22)),
    ("สิงห์", (7, 23), (8, 22)),
    ("กันย์", (8, 23), (9, 22)),
    ("ตุล", (9, 23), (10, 22)),
    ("พิจิก", (10, 23), (11, 21)),
    ("ธนู", (11, 22), (12, 21)),
]


def thai_weekday(d):
    # Python: Monday = 0
    return THAI_DAYS[d.weekday()]


def thai_date_text(d, buddhist=True):
    year = d.year + 543 if buddhist else d.year
    return f"{d.day} {THAI_MONTHS[d.month - 1]} {year}"


def digit_sum(number_string):
    return sum(int(ch) for ch in number_string if ch.isdigit())


def reduce_number(n):
    # Repeated digit sum; zero remains zero.
    while n >= 10:
        n = sum(int(ch) for ch in str(n))
    return n


def western_zodiac(d):
    md = (d.month, d.day)
    for name, start, end in THAI_ZODIAC:
        if start <= md <= end:
            return name
    # Capricorn crosses the year boundary.
    return "มังกร" if md >= (12, 22) or md <= (1, 19) else "ไม่ทราบ"


def animal_year_approx(d):
    # Approximation based on Gregorian year only.
    # Traditional lunar new year may fall later than Jan 1.
    animals = THAI_ANIMALS
    return animals[(d.year - 4) % 12]


def moon_phase_approx(d):
    """
    Approximate lunar phase.
    Reference new moon: 2000-01-06 18:14 UTC.
    Date-only input does not contain a precise observation time.
    This is NOT an official Thai lunar-calendar calculation.
    """
    reference = datetime(2000, 1, 6, 18, 14)
    target = datetime(d.year, d.month, d.day, 12, 0)
    synodic_month = 29.530588853

    days = (target - reference).total_seconds() / 86400
    age = days % synodic_month
    phase = age / synodic_month
    illumination = (1 - math.cos(2 * math.pi * phase)) / 2 * 100

    if age < 1.5 or age >= 28.0:
        label = "ใกล้วันเดือนดับ"
    elif age < 6.5:
        label = "ข้างขึ้น (เสี้ยว)"
    elif age < 8.5:
        label = "ใกล้วันครึ่งดวงข้างขึ้น"
    elif age < 13.5:
        label = "ข้างขึ้น (เกือบเต็มดวง)"
    elif age < 15.5:
        label = "ใกล้วันเพ็ญ"
    elif age < 21.5:
        label = "ข้างแรม"
    elif age < 23.5:
        label = "ใกล้วันครึ่งดวงข้างแรม"
    else:
        label = "ข้างแรม (เสี้ยว)"

    return label, age, illumination


def calculate_numbers(d):
    ymd = d.strftime("%Y%m%d")
    dmy = d.strftime("%d%m%Y")
    ddmm = d.strftime("%d%m")
    yyyy = str(d.year)
    digits = [int(x) for x in d.strftime("%d%m%Y")]

    total = sum(digits)
    return {
        "เลขวันที่ (DDMMYYYY)": dmy,
        "เลขวันที่ (YYYYMMDD)": ymd,
        "เลขวันและเดือน (DDMM)": ddmm,
        "เลขวันในเดือน": d.day,
        "เลขเดือน": d.month,
        "ปี ค.ศ.": d.year,
        "ปี พ.ศ.": d.year + 543,
        "ผลรวมเลขวันที่": total,
        "ผลรวมลดเลขหลักเดียว": reduce_number(total),
        "ผลรวมวันเดือนปี (DDMM)": digit_sum(ddmm),
        "ผลรวมปี ค.ศ.": digit_sum(yyyy),
        "ผลรวมวันที่ (YYYYMMDD)": digit_sum(ymd),
        "วันลำดับที่ของปี": d.timetuple().tm_yday,
        "สัปดาห์ ISO": d.isocalendar().week,
        "เลขวันในสัปดาห์ (จันทร์=1)": d.isoweekday(),
        "เลขวันในสัปดาห์ (อาทิตย์=1)": (d.weekday() + 1) % 7 + 1,
        "เลขกลับวันเดือนปี": dmy[::-1],
        "จำนวนวันในเดือน": calendar.monthrange(d.year, d.month)[1],
    }


# ---------- HEADER ----------
logo_path = Path(__file__).parent / "logo1.png"

if logo_path.exists():
    left, center, right = st.columns([1, 3, 1])
    with center:
        st.image(str(logo_path), use_container_width=True)

st.markdown(
    '<div class="synapse-title">SYNAPSE</div>'
    '<div class="synapse-subtitle">MYSTIC NUMBER • DATE INTELLIGENCE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p style="text-align:center;color:#a9b9d4;">'
    'ค้นหาข้อมูลวันและตัวเลขจากวันที่ที่คุณเลือก'
    '</p>',
    unsafe_allow_html=True,
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## ⚙️ ตั้งค่า")
    calendar_type = st.radio(
        "รูปแบบปีที่เลือก",
        ["ค.ศ.", "พ.ศ."],
        index=0,
    )
    st.caption("เลือกปี พ.ศ. ได้ แอปจะแปลงเป็น ค.ศ. ก่อนคำนวณ")
    st.divider()
    st.markdown("### 🌌 เกี่ยวกับแอป")
    st.write("SYNAPSE MYSTIC NUMBER")
    st.caption("เวอร์ชัน 1.0 • Date Calculator")
    st.caption("ตัวเลขเป็นผลคำนวณ ไม่ใช่การยืนยันผลการเสี่ยงโชค")


# ---------- DATE INPUT ----------
today = date.today()

st.markdown('<div class="panel">', unsafe_allow_html=True)
st.subheader("📅 เลือกวันที่ต้องการค้นหา")

if calendar_type == "พ.ศ.":
    default_year = today.year + 543
    selected = st.date_input(
        "เลือกวัน / เดือน / ปี (พ.ศ.)",
        value=today,
        format="DD/MM/YYYY",
        help="ปฏิทินของ Streamlit รับค่าเป็นวันที่สากล ค่าปีที่แสดงอาจขึ้นกับเบราว์เซอร์",
    )
    # Date input still stores Gregorian date internally.
    chosen_date = selected
    st.caption(
        f"วันที่ที่ใช้คำนวณ: {chosen_date.day:02d}/"
        f"{chosen_date.month:02d}/{chosen_date.year + 543} พ.ศ."
    )
else:
    chosen_date = st.date_input(
        "เลือกวัน / เดือน / ปี (ค.ศ.)",
        value=today,
        format="DD/MM/YYYY",
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------- RESULTS ----------
st.markdown("## ✨ ผลการคำนวณ")

weekday = thai_weekday(chosen_date)
thai_date = thai_date_text(chosen_date, buddhist=True)
gregorian_date = thai_date_text(chosen_date, buddhist=False)
numbers = calculate_numbers(chosen_date)
moon_label, moon_age, moon_light = moon_phase_approx(chosen_date)
zodiac = western_zodiac(chosen_date)
animal = animal_year_approx(chosen_date)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">วันในสัปดาห์</div>'
        f'<div class="metric-value">{weekday}</div>'
        f'<div class="metric-note">อ้างอิงปฏิทินสากล</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">วันที่ พ.ศ.</div>'
        f'<div class="metric-value">{thai_date}</div>'
        f'<div class="metric-note">ปีไทย = ค.ศ. + 543</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">วันที่ ค.ศ.</div>'
        f'<div class="metric-value">{gregorian_date}</div>'
        f'<div class="metric-note">Gregorian calendar</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

c4, c5, c6 = st.columns(3)
with c4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">ผลรวมเลขวันที่</div>'
        f'<div class="metric-value">{numbers["ผลรวมเลขวันที่"]}</div>'
        f'<div class="metric-note">รวมตัวเลข DDMMYYYY</div></div>',
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">ผลรวมลดเหลือหลักเดียว</div>'
        f'<div class="metric-value">{numbers["ผลรวมลดเลขหลักเดียว"]}</div>'
        f'<div class="metric-note">บวกซ้ำจนเหลือเลขเดียว</div></div>',
        unsafe_allow_html=True,
    )
with c6:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">ราศีสากลโดยประมาณ</div>'
        f'<div class="metric-value">{zodiac}</div>'
        f'<div class="metric-note">ใช้ช่วงวันตามราศีตะวันตก</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

c7, c8, c9 = st.columns(3)
with c7:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">ปีนักษัตรโดยประมาณ</div>'
        f'<div class="metric-value">{animal}</div>'
        f'<div class="metric-note">คำนวณจากปี ค.ศ. ยังไม่ปรับวันปีใหม่จันทรคติ</div></div>',
        unsafe_allow_html=True,
    )
with c8:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">ระยะจันทร์โดยประมาณ</div>'
        f'<div class="metric-value">{moon_label}</div>'
        f'<div class="metric-note">อายุจันทร์ {moon_age:.1f} วัน</div></div>',
        unsafe_allow_html=True,
    )
with c9:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">ความสว่างดวงจันทร์โดยประมาณ</div>'
        f'<div class="metric-value">{moon_light:.1f}%</div>'
        f'<div class="metric-note">ค่าประมาณทางดาราศาสตร์</div></div>',
        unsafe_allow_html=True,
    )

st.write("")
st.markdown("### 🔢 ตารางเลขทั้งหมด")

number_rows = [
    ("เลขวันที่ DDMMYYYY", numbers["เลขวันที่ (DDMMYYYY)"]),
    ("เลขวันที่ YYYYMMDD", numbers["เลขวันที่ (YYYYMMDD)"]),
    ("เลขวันและเดือน DDMM", numbers["เลขวันและเดือน (DDMM)"]),
    ("เลขวันในเดือน", numbers["เลขวันในเดือน"]),
    ("เลขเดือน", numbers["เลขเดือน"]),
    ("ปี ค.ศ.", numbers["ปี ค.ศ."]),
    ("ปี พ.ศ.", numbers["ปี พ.ศ."]),
    ("ผลรวมเลขวันที่ DDMMYYYY", numbers["ผลรวมเลขวันที่"]),
    ("ผลรวมลดเหลือหลักเดียว", numbers["ผลรวมลดเลขหลักเดียว"]),
    ("ผลรวมวันและเดือน", numbers["ผลรวมวันเดือนปี (DDMM)"]),
    ("ผลรวมปี ค.ศ.", numbers["ผลรวมปี ค.ศ."]),
    ("ผลรวมวันที่ YYYYMMDD", numbers["ผลรวมวันที่ (YYYYMMDD)"]),
    ("เลขกลับวันเดือนปี", numbers["เลขกลับวันเดือนปี"]),
    ("วันลำดับที่ของปี", numbers["วันลำดับที่ของปี"]),
    ("สัปดาห์ ISO", numbers["สัปดาห์ ISO"]),
    ("เลขวันในสัปดาห์ (จันทร์=1)", numbers["เลขวันในสัปดาห์ (จันทร์=1)"]),
    ("เลขวันในสัปดาห์ (อาทิตย์=1)", numbers["เลขวันในสัปดาห์ (อาทิตย์=1)"]),
    ("จำนวนวันในเดือน", numbers["จำนวนวันในเดือน"]),
]

st.dataframe(
    [{"รายการ": name, "ผลลัพธ์": value} for name, value in number_rows],
    use_container_width=True,
    hide_index=True,
)

# ---------- SAVE / DOWNLOAD ----------
st.markdown("### 💾 บันทึกผล")

if "history" not in st.session_state:
    st.session_state.history = []

if st.button("➕ เพิ่มวันที่นี้ลงในประวัติ", use_container_width=True):
    entry = {
        "วันที่ ค.ศ.": chosen_date.isoformat(),
        "วันที่ พ.ศ.": thai_date,
        "วันในสัปดาห์": weekday,
        "ผลรวมเลขวันที่": numbers["ผลรวมเลขวันที่"],
        "เลขหลักเดียว": numbers["ผลรวมลดเลขหลักเดียว"],
        "ราศี": zodiac,
        "ปีนักษัตรโดยประมาณ": animal,
        "ข้างขึ้นข้างแรมโดยประมาณ": moon_label,
    }
    st.session_state.history.append(entry)
    st.success("เพิ่มผลการคำนวณลงในประวัติแล้ว")

if st.session_state.history:
    st.dataframe(
        st.session_state.history,
        use_container_width=True,
        hide_index=True,
    )
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(
        csv_buffer,
        fieldnames=list(st.session_state.history[0].keys()),
    )
    writer.writeheader()
    writer.writerows(st.session_state.history)

    st.download_button(
        "⬇️ ดาวน์โหลดประวัติเป็น CSV",
        data="\ufeff" + csv_buffer.getvalue(),
        file_name="synapse_mystic_number_history.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.button("🗑️ ล้างประวัติในเซสชันนี้"):
        st.session_state.history = []
        st.rerun()

# ---------- DISCLAIMER ----------
st.divider()
st.markdown("""
<div class="panel">
<strong style="color:#f2d58a;">หมายเหตุสำคัญ</strong><br>
<span class="small-note">
วันในสัปดาห์และผลรวมตัวเลขคำนวณจากวันที่ที่เลือกโดยตรง
ส่วนปีนักษัตรเป็นค่าประมาณจากปี ค.ศ. และราศีใช้ช่วงวันตามราศีตะวันตก
ระยะจันทร์เป็นค่าประมาณทางดาราศาสตร์ ไม่ใช่ปฏิทินจันทรคติไทยอย่างเป็นทางการ
จึงยังไม่ควรใช้ระยะจันทร์นี้ยืนยันวันขึ้นหรือวันแรมตามปฏิทินไทย
ประวัติที่บันทึกไว้เก็บในเซสชันปัจจุบัน และอาจหายเมื่อเซสชันสิ้นสุด
</span>
</div>
""", unsafe_allow_html=True)

st.caption("SYNAPSE MYSTIC NUMBER • Date Calculator")

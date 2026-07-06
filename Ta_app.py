import streamlit as st
from datetime import date
import math

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="NEON MOON SYSTEM",
    layout="centered"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

body{
    background-color:#050505;
}

.stApp{
    background:
    radial-gradient(circle at top,
    #111111 0%,
    #050505 60%);
    color:white;
}

.main-title{

    text-align:center;

    font-size:58px;
    font-weight:bold;

    color:white;

    text-shadow:
    0 0 10px #00ccff,
    0 0 20px #00ccff,
    0 0 40px #cc00ff,
    0 0 80px #00ff99;
}

.sub-title{

    text-align:center;
    color:#cccccc;
    font-size:18px;
    margin-bottom:30px;
}

.neon-box{

    border:2px solid #00ccff;

    border-radius:20px;

    padding:25px;

    background:rgba(0,0,0,0.45);

    box-shadow:
    0 0 10px #00ccff,
    0 0 20px #cc00ff,
    0 0 40px #00ff99;

    margin-top:20px;
}

.result{

    text-align:center;

    font-size:65px;
    font-weight:bold;

    color:#00ff99;

    text-shadow:
    0 0 10px #00ff99,
    0 0 20px #00ff99,
    0 0 40px #00ff99;
}

.label{

    color:#00ccff;
    font-size:22px;
    font-weight:bold;
}

.info{

    font-size:20px;
    color:white;
    line-height:2;
}

.footer{

    text-align:center;
    color:#888888;
    margin-top:40px;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================

st.markdown("""
<div class="main-title">
NEON MOON SYSTEM
</div>

<div class="sub-title">
Automatic Cosmic Lunar Calculator
</div>
""", unsafe_allow_html=True)

# =========================================
# DATE INPUT
# =========================================

birth_date = st.date_input(
    "เลือกวันเดือนปี",
    value=date.today()
)

# =========================================
# AUTO CALCULATE
# =========================================

year = birth_date.year
month = birth_date.month
day_num = birth_date.day

# -----------------------------------------
# DAY OF WEEK
# -----------------------------------------

weekday_index = birth_date.weekday()

# Monday = 0
# Convert to Sunday = 1

day_value = ((weekday_index + 1) % 7) + 1

day_names = {
    1:"อาทิตย์",
    2:"จันทร์",
    3:"อังคาร",
    4:"พุธ",
    5:"พฤหัส",
    6:"ศุกร์",
    7:"เสาร์"
}

# -----------------------------------------
# CHINESE ZODIAC
# -----------------------------------------

zodiac_list = [
    "ชวด",
    "ฉลู",
    "ขาล",
    "เถาะ",
    "มะโรง",
    "มะเส็ง",
    "มะเมีย",
    "มะแม",
    "วอก",
    "ระกา",
    "จอ",
    "กุน"
]

zodiac_value = (year - 4) % 12
zodiac_name = zodiac_list[zodiac_value]

# ค่า 1-12
zodiac_number = zodiac_value + 1

# -----------------------------------------
# MOON PHASE CALCULATION
# -----------------------------------------

# วันที่อ้างอิงดวงจันทร์ใหม่
known_new_moon = date(2000, 1, 6)

days_difference = (birth_date - known_new_moon).days

moon_cycle = 29.530588

moon_age = days_difference % moon_cycle

moon_day = int(moon_age) + 1

# -----------------------------------------
# DETECT ข้างขึ้น / ข้างแรม
# -----------------------------------------

if moon_day <= 15:
    moon_phase_text = f"ขึ้น {moon_day} ค่ำ"
else:
    waning_day = moon_day - 15
    moon_phase_text = f"แรม {waning_day} ค่ำ"

# -----------------------------------------
# GOLDEN FORMULA
# -----------------------------------------

GOLDEN_RATIO = 1.618033988

day_energy = day_value / 7
month_energy = month / 12
moon_energy = moon_day / moon_cycle
zodiac_energy = zodiac_number / 12

total_energy = (
    day_energy
    +
    month_energy
    +
    moon_energy
    +
    zodiac_energy
)

final_energy = total_energy * GOLDEN_RATIO

# =========================================
# RESULT
# =========================================

st.markdown(f"""
<div class="neon-box">

<div class="info">

🌌 วัน:
<b>{day_names[day_value]}</b>

<br>

📅 เดือน:
<b>{month}</b>

<br>

🌙 จันทรคติ:
<b>{moon_phase_text}</b>

<br>

🐉 นักษัตร:
<b>{zodiac_name}</b>

</div>

</div>
""", unsafe_allow_html=True)

# =========================================
# ENERGY RESULT
# =========================================

st.markdown(f"""
<div class="neon-box">

<div style='
text-align:center;
font-size:28px;
color:#cc00ff;
margin-bottom:20px;
'>

COSMIC ENERGY

</div>

<div class="result">

{final_energy:.6f}

</div>

</div>
""", unsafe_allow_html=True)

# =========================================
# EXPLAIN
# =========================================

st.markdown("""
<div class="neon-box">

# ความหมายของระบบ

### 7
รอบวันของโลก

### 12
รอบเดือน และ 12 นักษัตร

### 29.530588
รอบดวงจันทร์จริง

### 1.618
Golden Ratio
สัดส่วนสมดุลธรรมชาติ

</div>
""", unsafe_allow_html=True)

# =========================================
# FOOTER
# =========================================

st.markdown("""
<div class="footer">

NEON MOON SYSTEM • CYBER COSMIC ENERGY

</div>
""", unsafe_allow_html=True)

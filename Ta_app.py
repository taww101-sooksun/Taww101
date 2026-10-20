
import itertools
from pathlib import Path
from datetime import date

import streamlit as st

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="แอปคำนวณตัวเลขประจำวัน",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------
# CUSTOM STYLE
# -------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #10291f 0%, #173c2b 45%, #f5f0df 100%);
}
.block-container {
    max-width: 850px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
.hero {
    background: linear-gradient(135deg, #173c2b, #285b3c);
    padding: 24px;
    border-radius: 22px;
    text-align: center;
    border: 1px solid #c9a85b;
    color: #fff7dc;
    margin-bottom: 20px;
}
.hero h1 {
    color: #f5d889;
    font-size: 1.8rem;
}
.hero p {
    color: #f8f1d8;
}
.result-card {
    background: #fffdf5;
    border: 1px solid #d7bd79;
    padding: 16px;
    border-radius: 16px;
    color: #193b2a;
    margin: 8px 0;
}
.number-box {
    background: #fffdf5;
    border: 1px solid #d7bd79;
    border-radius: 14px;
    text-align: center;
    padding: 14px 4px;
    color: #173c2b;
}
.number-box strong {
    font-size: 1.8rem;
}
div.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 46px;
}
h2, h3 {
    color: #f5d889;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# WEEKDAY NUMBERS
# Monday = 1 ... Sunday = 7
# -------------------------------
WEEKDAY_NUMBERS = {
    0: ("วันจันทร์", 1),
    1: ("วันอังคาร", 2),
    2: ("วันพุธ", 3),
    3: ("วันพฤหัสบดี", 4),
    4: ("วันศุกร์", 5),
    5: ("วันเสาร์", 6),
    6: ("วันอาทิตย์", 7),
}

# -------------------------------
# LOGO
# Put logo1.jpg in the same folder
# -------------------------------
logo_path = Path(__file__).parent / "logo1.jpg"

if logo_path.exists():
    st.image(str(logo_path), width=150)

st.markdown("""
<div class="hero">
    <h1>🌙 แอปคำนวณตัวเลขประจำวัน</h1>
    <p>วันประจำสัปดาห์ • ข้างขึ้น • ข้างแรม • สูตรตัวเลข</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# DATE INPUT
# -------------------------------
st.subheader("📅 เลือกวันที่")

selected_date = st.date_input(
    "วัน เดือน ปี",
    value=date.today(),
    format="DD/MM/YYYY",
)

weekday_name, weekday_number = WEEKDAY_NUMBERS[
    selected_date.weekday()
]

st.markdown(
    f"""
    <div class="result-card">
        <div>วันที่เลือก</div>
        <h2 style="color:#173c2b">
            {selected_date.strftime("%d/%m/%Y")}
        </h2>
        <div>วันในสัปดาห์: <b>{weekday_name}</b></div>
        <div>เลขประจำวัน: <b>{weekday_number}</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# LUNAR DATE INPUT
# Manual entry until a verified
# Thai lunar calendar is connected.
# -------------------------------
st.subheader("🌗 ข้อมูลจันทรคติ")

st.info(
    "กรอกข้อมูลข้างขึ้นหรือข้างแรมจากปฏิทินจันทรคติ "
    "เพื่อให้สูตรตัวเลขใช้ข้อมูลที่ถูกต้อง "
    "โค้ดรุ่นนี้ยังไม่ได้คำนวณวันจันทรคติอัตโนมัติ"
)

phase = st.radio(
    "เลือกข้าง",
    ["ข้างขึ้น", "ข้างแรม"],
    horizontal=True,
)

lunar_day = st.selectbox(
    "วันที่จันทรคติ",
    list(range(1, 16)),
    index=8,
    format_func=lambda n: f"{n} ค่ำ",
)

# -------------------------------
# USER FORMULA
# -------------------------------
st.subheader("🧮 คำนวณตามสูตร")

last_digit = lunar_day % 10

if phase == "ข้างขึ้น" and lunar_day > 9:
    operation = "หาร"
    result = (
        weekday_number / last_digit
        if last_digit != 0
        else None
    )
    formula = (
        f"{weekday_number} ÷ {last_digit}"
        if result is not None
        else "ไม่สามารถหารด้วยศูนย์ได้"
    )

elif phase == "ข้างแรม" and lunar_day > 9:
    operation = "คูณ"
    result = weekday_number * last_digit
    formula = f"{weekday_number} × {last_digit}"

else:
    operation = "บวกและลบ"
    add_result = weekday_number + lunar_day
    subtract_result = abs(weekday_number - lunar_day)
    result = None
    formula = (
        f"{weekday_number} + {lunar_day} = {add_result}\n\n"
        f"{lunar_day} - {weekday_number} = {subtract_result}"
    )

st.markdown(
    f"""
    <div class="result-card">
        <div>วัน: <b>{weekday_name}</b></div>
        <div>ข้าง: <b>{phase} {lunar_day} ค่ำ</b></div>
        <div>เครื่องหมาย: <b>{operation}</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### ผลการคำนวณ")

if result is not None:
    st.code(formula, language=None)
    st.metric("ผลลัพธ์ตามจริง", f"{result:.10g}")
else:
    st.code(formula, language=None)

# -------------------------------
# FOUR DIGIT SET
# Example follows Tuesday 2,
# waxing 9 => 2, 9, 7, 1.
# For other cases, review the
# rule before interpreting digits.
# -------------------------------
st.subheader("🔢 ชุดตัวเลข")

if phase == "ข้างขึ้น" and lunar_day <= 9:
    add_result = weekday_number + lunar_day
    subtract_result = abs(weekday_number - lunar_day)

    digits = [
        str(weekday_number),
        str(lunar_day),
        str(subtract_result),
        str(add_result % 10),
    ]

    st.caption(
        "ชุดตัวอย่างนี้ใช้เลขวัน เลขจันทรคติ "
        "ผลต่าง และเลขท้ายของผลบวก"
    )

    cols = st.columns(4)
    for col, digit in zip(cols, digits):
        with col:
            st.markdown(
                f'<div class="number-box">'
                f'<strong>{digit}</strong></div>',
                unsafe_allow_html=True,
            )

    # 24 permutations when all four digits differ.
    permutations = sorted(
        set(itertools.permutations(digits))
    )

    st.markdown("### ชุดเรียงสลับ")
    st.caption(
        f"ชุดเรียงที่ไม่ซ้ำกัน: {len(permutations)} ชุด "
        f"(หากมีเลขซ้ำ จำนวนชุดจะน้อยกว่า 24)"
    )

    pairs = [
        "".join(p)
        for p in permutations
    ]

    for start in range(0, len(pairs), 4):
        st.write("　".join(pairs[start:start + 4]))

    st.info(
        "จำนวน 48 ตำแหน่งต้องกำหนดกติกาการกลับบน–ล่าง "
        "เพิ่มเติม เพื่อไม่ให้เกิดชุดซ้ำโดยไม่ตั้งใจ"
    )

else:
    st.warning(
        "ส่วนสร้างชุดตัวเลข 4 ตัวสำหรับกรณีคูณหรือหาร "
        "ยังต้องกำหนดกติกาจัดชุดตามสูตรของคุณให้ครบก่อน"
    )

st.divider()

st.caption(
    "หมายเหตุ: วันในสัปดาห์คำนวณจากวันที่สากล "
    "ส่วนวันจันทรคติให้กรอกตรวจสอบจากปฏิทินที่เชื่อถือได้ "
    "ผลลัพธ์ชุดตัวเลขเป็นไปตามสูตรที่กำหนด ไม่ใช่การรับประกันผลใด ๆ"
)

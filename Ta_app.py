from datetime import date
from pathlib import Path
from itertools import permutations
import streamlit as st

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Ta App | คำนวณตัวเลขประจำวัน",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "logo1.jpg"

# ==================================================
# STYLE
# ==================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #102b20, #1c4932 50%, #f6f1e4 50%);
}
.block-container {
    max-width: 850px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}
.hero {
    background: linear-gradient(135deg, #163b29, #285c3c);
    border: 1px solid #d9b966;
    border-radius: 22px;
    padding: 24px 16px;
    text-align: center;
    color: #fff8e5;
    margin-bottom: 20px;
}
.hero h1 {
    color: #f3d58a;
    font-size: 1.8rem;
}
.hero p {
    margin-bottom: 0;
}
.card {
    background: #fffdf7;
    border: 1px solid #d9c58d;
    border-radius: 16px;
    padding: 16px;
    margin: 10px 0;
    color: #183d2a;
}
.number-card {
    background: #fffdf7;
    border: 1px solid #d9c58d;
    border-radius: 12px;
    padding: 12px 4px;
    text-align: center;
    color: #183d2a;
}
.number-card strong {
    font-size: 1.6rem;
}
.stButton button {
    border-radius: 12px;
    font-weight: bold;
    min-height: 44px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# WEEKDAY NUMBER
# Monday = 1, Tuesday = 2, ... Sunday = 7
# ==================================================
WEEKDAYS = {
    0: ("วันจันทร์", 1),
    1: ("วันอังคาร", 2),
    2: ("วันพุธ", 3),
    3: ("วันพฤหัสบดี", 4),
    4: ("วันศุกร์", 5),
    5: ("วันเสาร์", 6),
    6: ("วันอาทิตย์", 7),
}

# ==================================================
# HEADER AND LOGO
# ==================================================
if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=150)

st.markdown("""
<div class="hero">
    <h1>🌙 Ta App</h1>
    <p>ปฏิทิน • ข้างขึ้นข้างแรม • คำนวณชุดตัวเลข</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# DATE SELECTION
# ==================================================
st.subheader("📅 เลือกวันที่ต้องการตรวจสอบ")

selected_date = st.date_input(
    "วัน / เดือน / ปี",
    value=date.today(),
    format="DD/MM/YYYY",
)

weekday_name, weekday_number = WEEKDAYS[selected_date.weekday()]

st.markdown(f"""
<div class="card">
    <h3 style="color:#183d2a;">ข้อมูลวันที่เลือก</h3>
    <p>วันที่: <b>{selected_date.strftime("%d/%m/%Y")}</b></p>
    <p>วันประจำสัปดาห์: <b>{weekday_name}</b></p>
    <p>เลขประจำวัน: <b>{weekday_number}</b></p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# LUNAR DATE
#
# IMPORTANT:
# This version requires the lunar date to be entered
# from a verified Thai lunar calendar.
# It does NOT guess the lunar date.
# ==================================================
st.subheader("🌗 ข้อมูลปฏิทินจันทรคติไทย")

st.warning(
    "โปรดตรวจสอบข้างขึ้น–ข้างแรมจากปฏิทินไทยที่เชื่อถือได้ "
    "แอปเวอร์ชันนี้ยังไม่มีระบบเชื่อมต่อข้อมูลจันทรคติอัตโนมัติ "
    "จึงไม่ควรถือว่าข้อมูลที่กรอกเป็นข้อมูลที่แอปตรวจสอบแล้ว"
)

phase = st.radio(
    "เลือกข้าง",
    ["ข้างขึ้น", "ข้างแรม"],
    horizontal=True,
)

lunar_day = st.selectbox(
    "เลือกวันที่จันทรคติ",
    range(1, 16),
    format_func=lambda n: f"{n} ค่ำ",
    index=8,
)

st.caption(
    "เลขวันจันทรคติเป็นข้อมูลที่ผู้ใช้กรอก "
    "ไม่ใช่ผลการตรวจสอบอัตโนมัติจากปฏิทิน"
)

# ==================================================
# USER FORMULA
# ==================================================
st.subheader("🧮 ผลคำนวณตามสูตร")

last_digit = lunar_day % 10

if lunar_day > 9 and phase == "ข้างขึ้น":
    formula = f"{weekday_number} ÷ {last_digit}"
    result = (
        weekday_number / last_digit
        if last_digit != 0
        else None
    )
    operation = "หาร"

elif lunar_day > 9 and phase == "ข้างแรม":
    formula = f"{weekday_number} × {last_digit}"
    result = weekday_number * last_digit
    operation = "คูณ"

else:
    sum_value = weekday_number + lunar_day
    difference = abs(weekday_number - lunar_day)

    formula = (
        f"{weekday_number} + {lunar_day} = {sum_value}\n"
        f"{lunar_day} - {weekday_number} = {difference}"
    )
    result = None
    operation = "บวกและลบ"

st.markdown(f"""
<div class="card">
    <p>วัน: <b>{weekday_name}</b></p>
    <p>ข้าง: <b>{phase} {lunar_day} ค่ำ</b></p>
    <p>วิธีคำนวณ: <b>{operation}</b></p>
</div>
""", unsafe_allow_html=True)

st.code(formula, language=None)

if result is not None:
    st.metric("ผลลัพธ์ตามจริง", f"{result:.10g}")

# ==================================================
# FOUR CORE DIGITS
#
# For waxing/waning days 1-9:
# weekday number, lunar day,
# absolute difference, last digit of sum.
#
# Other cases require the user's complete
# digit-generation rule before automatic generation.
# ==================================================
st.subheader("🔢 เลขหลัก 4 ตัว")

core_digits = None

if lunar_day <= 9:
    sum_value = weekday_number + lunar_day
    difference = abs(weekday_number - lunar_day)

    core_digits = [
        str(weekday_number),
        str(lunar_day),
        str(difference),
        str(sum_value % 10),
    ]

    cols = st.columns(4)

    for col, digit in zip(cols, core_digits):
        with col:
            st.markdown(
                f'<div class="number-card">'
                f'<strong>{digit}</strong></div>',
                unsafe_allow_html=True,
            )

    st.caption(
        "ใช้เลขประจำวัน, เลขจันทรคติ, "
        "ผลต่าง และเลขท้ายของผลบวก"
    )
else:
    st.info(
        "กรณีข้างขึ้นหรือข้างแรมเกิน 9 "
        "แอปแสดงผลคำนวณด้านบนแล้ว "
        "แต่ยังไม่สร้างเลขหลัก 4 ตัวอัตโนมัติ "
        "จนกว่าจะยืนยันวิธีแปลงผลหารหรือผลคูณ "
        "เป็นเลขหลักตามสูตรของคุณ"
    )

# ==================================================
# GENERATE 3-DIGIT NUMBERS
# ==================================================
st.subheader("📌 เลข 3 ตัว")

if core_digits is not None and len(set(core_digits)) == 4:
    three_digit_numbers = [
        "".join(p)
        for p in permutations(core_digits, 3)
    ]

    st.success(f"ทั้งหมด {len(three_digit_numbers)} ชุด")

    # Show 4 numbers per row
    for start in range(0, len(three_digit_numbers), 4):
        row = three_digit_numbers[start:start + 4]
        cols = st.columns(4)

        for col, number in zip(cols, row):
            with col:
                st.markdown(
                    f'<div class="number-card">'
                    f'<strong style="font-size:1.05rem;">'
                    f'{number}</strong></div>',
                    unsafe_allow_html=True,
                )

    st.download_button(
        "📥 ดาวน์โหลดเลข 3 ตัว",
        data="\n".join(three_digit_numbers),
        file_name="three_digit_numbers.txt",
        mime="text/plain",
        use_container_width=True,
    )

    # ==================================================
    # GENERATE 2-DIGIT PAIRS
    # 12 unordered pairs, each with a reverse.
    # ==================================================
    st.subheader("📌 เลข 2 ตัวบน–ล่าง")

    unique_pairs = []

    for i in range(len(core_digits)):
        for j in range(i + 1, len(core_digits)):
            a = core_digits[i]
            b = core_digits[j]
            unique_pairs.append((a + b, b + a))

    st.success(
        f"{len(unique_pairs)} คู่กลับ "
        f"({len(unique_pairs) * 2} ตำแหน่ง)"
    )

    lines = []

    for top, bottom in unique_pairs:
        st.markdown(
            f'<div class="card" style="padding:10px 16px;">'
            f'<b>{top}</b>'
            f'<span style="float:right;">'
            f'<b>{bottom}</b></span></div>',
            unsafe_allow_html=True,
        )
        lines.append(f"{top} - {bottom}")

    st.download_button(
        "📥 ดาวน์โหลดเลข 2 ตัวบน–ล่าง",
        data="\n".join(lines),
        file_name="two_digit_pairs.txt",
        mime="text/plain",
        use_container_width=True,
    )

    # ==================================================
    # COST ESTIMATE
    # ==================================================
    st.subheader("💰 คำนวณเงิน")

    price_three = st.number_input(
        "ราคาต่อชุดเลข 3 ตัว (บาท)",
        min_value=0.0,
        value=1.0,
        step=1.0,
    )

    price_two = st.number_input(
        "ราคาต่อตำแหน่งเลข 2 ตัว (บาท)",
        min_value=0.0,
        value=1.0,
        step=1.0,
    )

    total_three = len(three_digit_numbers) * price_three
    total_two = len(unique_pairs) * 2 * price_two
    total_cost = total_three + total_two

    col1, col2 = st.columns(2)

    with col1:
        st.metric("เลข 3 ตัว", f"{total_three:,.2f} บาท")

    with col2:
        st.metric("เลข 2 ตัว", f"{total_two:,.2f} บาท")

    st.markdown(
        f"""
        <div class="hero">
            <p>รวมค่าใช้จ่ายตามจำนวนชุด</p>
            <h1>{total_cost:,.2f} บาท</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.warning(
        "ระบบจะสร้างชุดเลขอัตโนมัติเมื่อเลขหลัก 4 ตัว "
        "ไม่ซ้ำกัน เพื่อให้ได้ 24 ชุดสำหรับเลข 3 ตัว "
        "และ 24 ตำแหน่งสำหรับเลข 2 ตัว"
    )

st.divider()

st.caption(
    "Ta App — ตรวจสอบวันที่และสูตรก่อนนำผลลัพธ์ไปใช้ "
    "ข้างขึ้น–ข้างแรมยังต้องตรวจสอบจากปฏิทินอ้างอิง"
)

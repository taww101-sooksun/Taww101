import streamlit as st
import pandas as pd
from datetime import datetime, date
import itertools
import random

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v11: TAROT & DESTINY", layout="wide")
st.markdown("<style>.main { background-color: #0b1016; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# --- DATA: ไพ่ยิปซี (Major Arcana 22 ใบ) ---
TAROT_DECK = {
    "The Fool": "การเริ่มต้นใหม่ ความอิสระ เสี่ยงแต่คุ้ม",
    "The Magician": "ความฉลาด มีไหวพริบ จัดการปัญหาได้ทุกอย่าง",
    "The High Priestess": "ลางสังหรณ์แม่นยำ มีความลับที่ยังไม่เปิดเผย",
    "The Empress": "ความอุดมสมบูรณ์ การดูแลเอาใจใส่ ความสำเร็จ",
    "The Emperor": "อำนาจ บารมี ความมั่นคง การตัดสินใจที่เด็ดขาด",
    "The Hierophant": "ความเชื่อ ศีลธรรม มีผู้ใหญ่คอยช่วยเหลือ",
    "The Lovers": "การตัดสินใจ ความรัก การเลือกทางเดินชีวิต",
    "The Chariot": "การพุ่งไปข้างหน้า ชัยชนะจากการต่อสู้",
    "Strength": "ความอดทน สยบปัญหาด้วยความอ่อนโยน",
    "The Hermit": "การทบทวนตัวเอง ความสงบ ค้นพบความจริง",
    "Wheel of Fortune": "กงล้อแห่งโชคชะตา โอกาสดีๆ กำลังจะมา",
    "Justice": "ความยุติธรรม ความสมดุล ผลจากการกระทำ",
    "The Hanged Man": "การรอคอย การเสียสละเพื่อสิ่งที่ดีกว่า",
    "Death": "การจบเพื่อเริ่มใหม่ การเปลี่ยนแปลงครั้งใหญ่",
    "Temperance": "การปรับตัว ความพอดี การเจรจาที่ลงตัว",
    "The Devil": "กิเลส ตัณหา สิ่งล่อใจที่ต้องระวัง",
    "The Tower": "เหตุการณ์กะทันหัน การพังทลายเพื่อสร้างใหม่",
    "The Star": "ความหวัง แรงบันดาลใจ ความราบรื่น",
    "The Moon": "ความกังวล ความสับสน ให้ระวังคนหลอกลวง",
    "The Sun": "ความสุข ความสำเร็จ โชคลาภสว่างไสว",
    "Judgement": "การตื่นรู้ การหลุดพ้นจากปัญหาเดิมๆ",
    "The World": "ความสมบูรณ์แบบ บรรลุเป้าหมายที่ตั้งไว้"
}

# --- FUNCTIONS ---
def get_thai_astrology(date_obj):
    day, month = date_obj.day, date_obj.month
    year_th = date_obj.year + 543
    # 12 ราศี & ธาตุ
    if (month == 4 and day >= 13) or (month == 5 and day <= 13): r, t = "เมษ", "ไฟ"
    elif (month == 5 and day >= 14) or (month == 6 and day <= 14): r, t = "พฤษภ", "ดิน"
    elif (month == 6 and day >= 15) or (month == 7 and day <= 15): r, t = "เมถุน", "ลม"
    elif (month == 7 and day >= 16) or (month == 8 and day <= 16): r, t = "กรกฎ", "น้ำ"
    elif (month == 8 and day >= 17) or (month == 9 and day <= 16): r, t = "สิงห์", "ไฟ"
    elif (month == 9 and day >= 17) or (month == 10 and day <= 16): r, t = "กันย์", "ดิน"
    elif (month == 10 and day >= 17) or (month == 11 and day <= 15): r, t = "ตุลย์", "ลม"
    elif (month == 11 and day >= 16) or (month == 12 and day <= 15): r, t = "พิจิก", "น้ำ"
    elif (month == 12 and day >= 16) or (month == 1 and day <= 14): r, t = "ธนู", "ไฟ"
    elif (month == 1 and day >= 15) or (month == 2 and day <= 12): r, t = "มังกร", "ดิน"
    elif (month == 2 and day >= 13) or (month == 3 and day <= 13): r, t = "กุมภ์", "ลม"
    else: r, t = "มีน", "น้ำ"
    z_list = ["ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง"]
    eff_y = year_th - 1 if (month < 4 or (month == 4 and day < 13)) else year_th
    return r, t, z_list[eff_y % 12]

# --- SIDEBAR ---
st.sidebar.header("🧭 ตั้งค่าข้อมูล")
name1 = st.sidebar.text_input("ชื่อของคุณ", "บาส")
date1 = st.sidebar.date_input(f"วันเกิดคุณ {name1}", value=date(1984, 5, 18), min_value=date(1960, 1, 1))

st.sidebar.divider()
show_tarot = st.sidebar.checkbox("🔮 เปิดฟีเจอร์ไพ่ยิปซี", value=True)

# --- MAIN APP ---
st.title("🛰️ SYNAPSE: DESTINY COMMANDER v11")
st.write(f"**วันปัจจุบัน:** {datetime.now().strftime('%d/%m/%Y')} | **BY:** Ta101")

# ส่วนที่ 1: ข้อมูลราศี
st.divider()
r1, t1, a1 = get_thai_astrology(date1)
col1, col2, col3 = st.columns(3)
with col1: st.metric("ราศี", r1)
with col2: st.metric("ปีนักษัตร", a1)
with col3: st.metric("ธาตุ", t1)

# ส่วนที่ 2: ฟีเจอร์ไพ่ยิปซี
if show_tarot:
    st.divider()
    st.subheader("🔮 เปิดไพ่ยิปซีพยากรณ์ดวงชะตา")
    if st.button("🃏 กดเพื่อเสี่ยงทายไพ่"):
        card_name, card_meaning = random.choice(list(TAROT_DECK.items()))
        st.balloons()
        st.markdown(f"### คุณได้ไพ่: **{card_name}**")
        st.info(f"**คำทำนาย:** {card_meaning}")
        st.caption("หมายเหตุ: นี่คือการสุ่มเพื่อแนวทางสถิติ 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# ส่วนที่ 3: วิเคราะห์เลข (สั้นๆ ท้ายแอป)
st.divider()
st.subheader("🔢 วิเคราะห์เลขมงคล 18 ประตู")
lottery_num = st.text_input("กรอกเลข 3 ตัว", "785", max_chars=3)
if len(lottery_num) == 3:
    p3 = sorted(set([''.join(p) for p in itertools.permutations(lottery_num)]))
    st.code(" | ".join(p3))

st.divider()
st.caption("ความจริงสำคัญที่สุด... พัฒนาโดย Ta101")

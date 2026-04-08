import streamlit as st
import pandas as pd
from datetime import datetime
import itertools

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")
st.title("🛡️ SYNAPSE - 18 GATES ANALYZER")
st.subheader("ID: Ta101 | 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- LOGIC 1: 18 ประตู (7-8-5) ---
def generate_gates(digits):
    # 3 ตัวบนกลับ (6 ประตู)
    three_digits = [''.join(p) for p in itertools.permutations(digits)]
    # 2 ตัวบน-ล่าง วินกัน (12 ชุด รวมกลับหน้าหลัง)
    two_digits_raw = list(itertools.combinations(digits, 2))
    two_digits = []
    for pair in two_digits_raw:
        two_digits.append(f"{pair[0]}{pair[1]}")
        two_digits.append(f"{pair[1]}{pair[0]}")
    return three_digits, two_digits

# --- LOGIC 2: วิเคราะห์ความเหมาะสม (Strategy) ---
def analyze_strategy(target_date):
    # ตรรกะคืนมืดสนิท (แรม 14 ค่ำ เดือน 5)
    # วันพฤหัสบดีที่ 16 เมษา 2569
    strategy = {
        "Phase": "🌑 มืดสนิท (New Moon)",
        "Day": "วันพฤหัสบดี (สีส้ม - เลข 5 เด่น)",
        "History": "ตรงกับปี 2552 (ออก 587) และ 2542 (ออก 507/11)"
    }
    return strategy

# --- INTERFACE ---
col1, col2 = st.columns(2)

with col1:
    st.write("### 🔢 ชุดเลขวิเคราะห์ (Target)")
    my_digits = st.text_input("ใส่เลข 3 ตัว", value="785")
    
    if st.button("ประมวลผล 18 ประตู"):
        top3, bottom2 = generate_gates(my_digits)
        
        st.info("🎯 3 ตัวบน (6 ประตู)")
        st.write(", ".join(top3))
        
        st.success("🎯 2 ตัวบน-ล่าง (12 ประตู)")
        st.write(", ".join(bottom2))

with col2:
    st.write("### 🌑 สภาวะท้องฟ้า & สถิติ")
    analysis = analyze_strategy("2026-04-16")
    
    st.warning(f"ข้างขึ้นข้างแรม: {analysis['Phase']}")
    st.write(f"วันในสัปดาห์: {analysis['Day']}")
    st.write(f"บันทึกประวัติศาสตร์: {analysis['History']}")

# --- FOOTER ---
st.divider()
st.caption("ระบบรันข้อมูลตามสถิติและความจริง 'ไม่โกหก' ตามหลักการของ Ta101")

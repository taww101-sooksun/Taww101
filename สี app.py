import streamlit as st
from datetime import datetime

# --- UI STYLE ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ff00; }
    .stMetric { border: 1px solid #ff00ff; border-radius: 10px; padding: 10px; }
    .synapse-box { border: 2px solid #00ffff; padding: 20px; border-radius: 15px; background: #001515; }
    .standard-box { border: 2px solid #ff7f50; padding: 20px; border-radius: 15px; background: #150a00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌌 SYNAPSE DUAL-DECODER")

# รับวันที่
selected_date = st.date_input("📅 เลือกวันที่ต้องการถอดรหัส", datetime.now())
PHI = 1.618
day_of_week = selected_date.isoweekday()

# --- 1. สูตรเดิมของคุณต๊ะ (29.53 Fixed) ---
def get_synapse_logic(date):
    ref = datetime(2000, 1, 6)
    diff = (date - ref.date()).days
    cycle = 29.53
    pos = (diff % cycle)
    label = "ขึ้น" if pos <= 14.76 else "แรม"
    step = round(pos if pos <= 14.76 else pos - 14.76)
    sign = 1 if pos > 14.76 else -1
    res = (day_of_week * PHI) + ((step - 7.5) * sign)
    return label, step, res

# --- 2. สูตรมาตรฐานปัจจุบัน (Astronomical Approximation) ---
def get_standard_logic(date):
    # ปรับจูน Reference ให้ใกล้เคียงปฏิทินไทยปี 2026 มากขึ้น
    ref = datetime(2000, 1, 6, 18, 14) 
    diff = (date - ref.date()).days
    cycle = 29.530588853
    pos = (diff % cycle)
    label = "ขึ้น" if pos <= 14.765 else "แรม"
    step = round(pos if pos <= 14.765 else pos - 14.765)
    sign = 1 if pos > 14.765 else -1
    res = (day_of_week * PHI) + ((step - 7.5) * sign)
    return label, step, res

s_label, s_step, s_res = get_synapse_logic(selected_date)
t_label, t_step, t_res = get_standard_logic(selected_date)

# --- DISPLAY ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="synapse-box">', unsafe_allow_html=True)
    st.subheader("⚡ SYNAPSE LOGIC")
    st.write(f"จันทรคติ: {s_label} {s_step} ค่ำ")
    st.metric("Index (29.53)", f"{abs(s_res):.4f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="standard-box">', unsafe_allow_html=True)
    st.subheader("🌐 STANDARD LOGIC")
    st.write(f"จันทรคติ: {t_label} {t_step} ค่ำ")
    st.metric("Index (Global)", f"{abs(t_res):.4f}")
    st.markdown('</div>', unsafe_allow_html=True)

st.info(f"💡 ความต่างคือ: {abs(s_res - t_res):.4f} (นี่คือช่องว่างของมิติเวลาที่คุณค้นพบ)")

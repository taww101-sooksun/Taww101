import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import math
import hashlib
import pandas as pd
from datetime import datetime, date, timedelta
from streamlit_js_eval import get_geolocation
import streamlit.components.v1 as components

# --- [ 1. CONFIG บนสุด ห้ามย้าย! ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

# --- [ 2. การเชื่อมต่อ FIREBASE ] ---
if not firebase_admin._apps:
    try:
        import json
        key_dict = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["databaseURL"]
        })
    except Exception as e:
        st.error(f"❌ Firebase Error: {e}")
        st.stop()

# --- [ 3. ฟังก์ชันการคำนวณ (The Truth) ] ---
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]
    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "formula": formula}

# --- [ 4. จัดการสถานะ (SESSION STATE) ] ---
states = {
    'main_color': "#00f3ff",
    'sub_color': "#ff00de",
    'page': "HOME",
    'logged_in': False,
    'user': "Agent"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- [ 5. สไตล์หน้าจอ (UI/CSS) ] ---
logo_b64 = get_base64_data("logo1.png")
st.markdown(f"""
    <style>
    :root {{ --primary: {st.session_state.main_color}; --secondary: {st.session_state.sub_color}; }}
    .stApp {{ background: #000; color: #fff; }}
    header, footer, #MainMenu {{ visibility: hidden; }}
    .neon-text {{ text-align: center; color: var(--primary); text-shadow: 0 0 10px var(--primary); font-weight: bold; font-family: 'Orbitron', sans-serif; }}
    .stButton>button {{ border: 1px solid var(--primary) !important; background: rgba(0,0,0,0.5) !important; color: white !important; border-radius: 12px; transition: 0.3s; }}
    .stButton>button:hover {{ box-shadow: 0 0 20px var(--secondary); border-color: var(--secondary) !important; transform: scale(1.02); }}
    .global-logo {{ position: fixed; top: 10px; right: 10px; width: 55px; z-index: 1000; filter: drop-shadow(0 0 8px var(--primary)); }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="global-logo">
""", unsafe_allow_html=True)

# --- [ 6. ระบบลงทะเบียนเข้าใช้งาน ] ---
if not st.session_state.logged_in:
    st.markdown("<h1 class='neon-text'>SYNAPSE SYSTEM</h1>", unsafe_allow_html=True)
    with st.container():
        new_user = st.text_input("รหัสเรียกขาน (Agent Name):", placeholder="ระบุชื่อของคุณ").strip()
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if new_user:
                st.session_state.user = new_user
                st.session_state.logged_in = True
                st.rerun()
            else: st.warning("กรุณาใส่ชื่อเพื่อเข้าใช้งาน")
    st.stop()

# --- [ 7. ปุ่มย้อนกลับ (Global) ] ---
if st.session_state.page != "HOME":
    if st.button("⬅️ BACK TO MAIN"):
        st.session_state.page = "HOME"
        st.rerun()

# --- [ 8. การจัดการห้องต่างๆ (NAVIGATION) ] ---

# --- หน้า HOME (ศูนย์ควบคุม) ---
if st.session_state.page == "HOME":
    st.markdown("<h2 class='neon-text'>SYNAPSE COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.write(f"<p style='text-align:center;'>Welcome, Agent: <b style='color:var(--primary);'>{st.session_state.user}</b></p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 1. SONIC WAVE\nAudio & DJ Module", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        if st.button("🧬 2. QUANTUM SCAN\nLogic & Timeline", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
    with col2:
        if st.button("🛰️ 3. RADAR & CHAT\nTactical Module", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        if st.button("🔢 4. DAILY CODE\nSecurity Key", use_container_width=True):
            st.session_state.page = "8"; st.rerun()

    st.divider()
    if st.button("🎨 ปรับแต่งสีระบบ (Interface)", use_container_width=True):
        st.session_state.page = "10"; st.rerun()
    
    st.markdown("<p style='text-align:center; opacity:0.5; font-size:12px;'>อยู่นิ่งๆ ไม่เจ็บตัว | System v.3.0</p>", unsafe_allow_html=True)

# --- หน้า 1: SONIC WAVE (DJ Deck) ---
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎵 SONIC WAVE STATION</h2>", unsafe_allow_html=True)
    # ใส่โค้ด HTML DJ Mixer เดิมของคุณตรงนี้ได้เลย

# --- หน้า 2: RADAR & CHAT ---
elif st.session_state.page == "2":
    st.markdown("<h2 class='neon-text'>🛰️ TACTICAL RADAR</h2>", unsafe_allow_html=True)
    # ใส่โค้ดแผนที่และแชตเดิมตรงนี้

# --- หน้า 3: รวม QUANTUM SCAN (3-in-1) ---
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text'>🧬 QUANTUM ANALYZER</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["💎 สแกนส่วนตัว", "🤝 ตรวจค่า Gap", "📅 Timeline 180 วัน"])
    
    with tab1:
        d_input = st.date_input("เลือกวันเกิด", value=date(1990,1,1), key="q_solo")
        res = get_detailed_logic(d_input)
        st.metric("YOUR CODE", res['res'])
        st.info(f"วัน{res['day_name']} | {res['phase']}")
    
    with tab2:
        c_a, c_b = st.columns(2)
        da = c_a.date_input("Agent 1", value=date(1990,1,1), key="qa")
        db = c_b.date_input("Agent 2", value=date(1991,1,1), key="qb")
        gap = abs(get_detailed_logic(da)['res'] - get_detailed_logic(db)['res'])
        st.subheader(f"Gap: {gap:.4f}")
        if gap < 0.5: st.success("💎 พิกัดเพชร")
        elif 3.8 <= gap <= 4.2: st.warning("🌀 พิกัดธรรม")

    with tab3:
        target_dob = st.date_input("วันเกิดเพื่อเช็คอนาคต", value=date(1990,1,1), key="q_timeline")
        code = get_detailed_logic(target_dob)['res']
        future = []
        for i in range(180):
            target_date = date.today() + timedelta(days=i)
            d_logic = get_detailed_logic(target_date)
            g = abs(d_logic['res'] - code)
            if g < 0.5 or (3.8 <= g <= 4.2) or g > 10.0:
                future.append({"วันที่": target_date.strftime('%d/%m/%Y'), "พิกัด": "เพชร" if g < 0.5 else "ธรรม" if g < 4.2 else "กระจก"})
        st.table(pd.DataFrame(future))

# --- หน้า 8: DAILY CODE ---
elif st.session_state.page == "8":
    st.markdown("<h2 class='neon-text'>🔢 SECURITY KEY</h2>", unsafe_allow_html=True)
    raw = f"{date.today()}_{st.session_state.user}_SYNAPSE"
    h = hashlib.sha256(raw.encode()).hexdigest()
    st.code(f"AGENT PIN: {str(int(h[:4], 16))[-4:].zfill(4)}", language="")

# --- หน้า 10: INTERFACE ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 INTERFACE SETUP</h2>", unsafe_allow_html=True)
    st.session_state.main_color = st.color_picker("Main Neon Color", st.session_state.main_color)
    st.session_state.sub_color = st.color_picker("Sub Neon Color", st.session_state.sub_color)
    if st.button("SAVE & APPLY"): st.rerun()

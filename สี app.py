# =========================================================
# 🛡️ SYNAPSE COMMAND CENTER - FULL POWER v4.2
# =========================================================

import streamlit as st
import base64
import math
from datetime import datetime, date, timedelta

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")
primary_neon = "#1F51FF" 

# ฟังก์ชันแปลงรูปโลโก้
def get_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

logo_data = get_base64("logo1.png")

# --- 2. CUSTOM CSS (หนา 2px + โยกสะบัด + ปรับขนาดปุ่ม) ---
st.markdown(f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    /* โลโก้เต้น */
    .logo-container {{
        display: flex; justify-content: center;
        animation: logo-dance 3s ease-in-out infinite;
        margin-bottom: 10px;
    }}
    @keyframes logo-dance {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-5px); }}
    }}

    /* สโลแกนนีออนโยกสะบัด */
    .neon-wrapper {{
        text-align: center;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        background: linear-gradient(to right, #FF3131, #FFF01F, #00F3FF, #FF44CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbow-glow 3s linear infinite, slogan-shake 2s ease-in-out infinite;
    }}
    @keyframes slogan-shake {{
        0%, 100% {{ transform: scale(1) rotate(0); }}
        50% {{ transform: scale(1.05) rotate(1deg); }}
    }}
    @keyframes rainbow-glow {{
        0% {{ filter: hue-rotate(0deg) drop-shadow(0 0 10px {primary_neon}); }}
        100% {{ filter: hue-rotate(360deg) drop-shadow(0 0 10px {primary_neon}); }}
    }}

    /* ปุ่ม UNIT ปรับให้เล็กลงและหนาตามสั่ง */
    button[kind="secondary"] {{
        background-color: transparent !important;
        color: {primary_neon} !important;
        border: 2px solid {primary_neon} !important;
        border-radius: 10px !important;
        height: 55px !important;
        font-weight: bold !important;
        font-size: 13px !important;
        box-shadow: 0 0 10px {primary_neon} !important;
        transition: 0.3s;
    }}
    button[kind="secondary"]:hover {{
        background-color: {primary_neon} !important;
        color: #000 !important;
        box-shadow: 0 0 20px {primary_neon} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
if logo_data:
    st.markdown(f'''<div class="logo-container"><img src="data:image/png;base64,{logo_data}" style="width:120px;"></div>''', unsafe_allow_html=True)

st.markdown(f'''<div class="neon-wrapper"><div style="font-size:28px; letter-spacing:4px;">SYNAPSE</div><div style="font-size:24px; letter-spacing:6px;">อยู่นิ่งๆไม่เจ็บตัว</div></div>''', unsafe_allow_html=True)

# --- 4. NAVIGATION HUB LOGIC ---
if 'page' not in st.session_state: 
    st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    st.write("##")
    num_cols = 4 
    cols = st.columns(num_cols) 
    
    unit_names = {
        1: "🎵 01: DJ STATION", 2: "🛰️ 02: TACTICAL RADAR", 3: "🔮 03: TRUTH LOGIC",
        4: "⚡ 04: SENSOR SCAN", 5: "🎨 05: UI DESIGNER", 6: "💬 06: COMMS CENTER",
        7: "🛠️ 07: DIY MASTER", 8: "🧬 08: SYNAPSE CORE", 9: "📹 09: MEDIA STUDIO",
        10: "💾 10: FIREBASE DB", 11: "🏴 11: COMMAND POST"
    }

    for i in range(1, 12):
        with cols[(i-1) % num_cols]: 
            if st.button(unit_names[i], key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i)
                st.rerun()

# --- 5. UNIT PAGES ---
else:
    # แถบปุ่มกลับ (Back Button)
    if st.button("⬅️ BACK TO HUB"):
        st.session_state.page = "HOME"
        st.rerun()
    
    st.divider()
    page = st.session_state.page

    if page == "1":
        st.markdown("<h2 class='neon-wrapper'>🎵 UNIT 01: DJ STATION</h2>", unsafe_allow_html=True)
        st.info("🎧 ระบบมิกซ์เพลงออนไลน์...")

    elif page == "2":
        st.markdown("<h2 class='neon-wrapper'>🛰️ UNIT 02: TACTICAL RADAR</h2>", unsafe_allow_html=True)
        st.info("📡 สแกนพิกัดเรียลไทม์...")

    elif page == "3":
        st.markdown("<h2 class='neon-wrapper'>🔮 UNIT 03: TRUTH LOGIC</h2>", unsafe_allow_html=True)
        st.info("🧬 ถอดรหัสค่าความจริง...")

    elif page == "4":
        st.markdown("<h2 class='neon-wrapper'>⚡ UNIT 04: SENSOR SCAN</h2>", unsafe_allow_html=True)
        st.info("📶 ตรวจรับสัญญาณเซนเซอร์...")

    elif page == "5":
        st.markdown("<h2 class='neon-wrapper'>🎨 UNIT 05: UI DESIGNER</h2>", unsafe_allow_html=True)
        st.info("🌈 ปรับแต่งสี Interface...")

    elif page == "6":
        st.markdown("<h2 class='neon-wrapper'>💬 UNIT 06: COMMS CENTER</h2>", unsafe_allow_html=True)
        st.info("🛰️ ช่องทางสื่อสารลับ...")

    elif page == "7":
        st.markdown("<h2 class='neon-wrapper'>🛠️ UNIT 07: DIY MASTER</h2>", unsafe_allow_html=True)
        st.info("🔧 บันทึกงานซ่อมบำรุง...")

    elif page == "8":
        st.markdown("<h2 class='neon-wrapper'>🧬 UNIT 08: SYNAPSE CORE</h2>", unsafe_allow_html=True)
        st.info("🧠 ระบบ AI ประมวลผล...")

    elif page == "9":
        st.markdown("<h2 class='neon-wrapper'>📹 UNIT 09: MEDIA STUDIO</h2>", unsafe_allow_html=True)
        st.info("🎬 จัดการสื่อวิดีโอ...")

    elif page == "10":
        st.markdown("<h2 class='neon-wrapper'>💾 UNIT 10: FIREBASE DB</h2>", unsafe_allow_html=True)
        st.info("📂 จัดการฐานข้อมูล Cloud...")

    elif page == "11":
        st.markdown("<h2 class='neon-wrapper'>🏴 11: COMMAND POST</h2>", unsafe_allow_html=True)
        st.info("🏁 สรุปสถานะภารกิจ...")

# --- 6. FOOTER ---
st.write("---")
st.caption(f"SYNAPSE OS v4.2 | AGENT STATUS: ONLINE | {datetime.now().strftime('%H:%M:%S')}")

import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date
import math
import random
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & STYLE (อยู่นิ่งๆ ไม่เจ็บตัว)
# ==========================================
st.set_page_config(page_title="SYNAPSE OS v20.2", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(270deg, #AFEEEE, #FF7F50, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
            background-size: 1600% 1600%;
            animation: RainbowFlow 60s ease infinite;
        }}
        @keyframes RainbowFlow {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
        
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            border-radius: 20px !important;
            padding: 10px !important;
            border: 2px solid {theme} !important;
            box-shadow: 0 0 15px {theme}88;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important;
            background-color: {theme}44 !important;
            border: 1px solid {theme} !important;
            box-shadow: 0 0 15px {theme} !important;
        }}
        .logic-box {{ 
            background-color: #101a24; padding: 15px; border-left: 5px solid #00ff41; 
            border-radius: 10px; margin-bottom: 20px; color: #f0f0f0;
        }}
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
            border: 2px solid {theme} !important;
            border-radius: 15px !important;
            filter: drop-shadow(0 0 5px {theme});
        }}
        </style>
    """, unsafe_allow_html=True)

def show_logo(width=200, glow_color=None):
    """ฟังก์ชันกลางสำหรับโชว์ logo1.png พร้อมแสงนีออน"""
    theme = glow_color if glow_color else st.session_state.get('theme_color', "#1408BF")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists("logo1.png"):
            with open("logo1.png", "rb") as f:
                data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div style="text-align:center; filter: drop-shadow(0 0 15px {theme});">
                    <img src="data:image/png;base64,{data}" style="width:100%; max-width:{width}px; border-radius:15px;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 10px {theme};'>SYNAPSE</h1>", unsafe_allow_html=True)

# ==========================================
# 1. LOGIC ENGINES (สูตรคำนวณ)
# ==========================================
def get_detailed_logic(dt):
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        return {"res": round(math.sqrt((day_val**2) + (m_num**2)), 4), "phase": f"ขึ้น {m_num} ค่ำ", "type": "แรงผลักดัน"}
    else:
        m_num = int(pos - 14.765) + 1
        return {"res": round((day_val * 1.618) / (m_num if m_num != 0 else 1), 4), "phase": f"แรม {m_num} ค่ำ", "type": "สมดุลทองคำ"}

# ==========================================
# 2. ROOMS (ฟังก์ชันแต่ละหน้าจอ)
# ==========================================
def room_truth_scan():
    st.subheader("🛰️ สแกนพิกัดรหัสคู่ขนาน")
    c1, c2 = st.columns(2)
    dob1 = c1.date_input("วันเกิดบุคคลที่ 1", key="u1")
    dob2 = c2.date_input("วันเกิดบุคคลที่ 2", key="u2")
    if dob1 and dob2:
        d1, d2 = get_detailed_logic(dob1), get_detailed_logic(dob2)
        st.write(f"รหัส 1: {d1['res']} | รหัส 2: {d2['res']}")
        gap = abs(d1['res'] - d2['res'])
        st.info(f"GAP: {gap:.4f}")
        if 3.5 <= gap <= 4.5: st.error("⚠️ ระดับ: รหัสคู่ขนาน (ตรวจพบสัญญาณสะท้อน!)")

def room_reality_extractor():
    st.subheader("🧬 Reality Extractor")
    target_date = st.date_input("เลือกวันที่สแกน", value=date.today())
    if target_date:
        data = get_detailed_logic(target_date)
        st.markdown(f"""<div class="logic-box" style="text-align:center;">
            <h1>{data['res']}</h1><p>{data['phase']}</p>
        </div>""", unsafe_allow_html=True)

# ==========================================
# 3. MAIN SYSTEM
# ==========================================
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    # ... Firebase Init ตามปกติของท่าน ...

def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation()

    if not st.session_state.logged_in:
        # หน้า Login (โชว์โลโก้นำหน้า)
        show_logo(width=250)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            with st.form("login_form"):
                uid = st.text_input("AGENT ID")
                pw = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("UNLOCK SYSTEM", use_container_width=True):
                    # จำลองการ Login (ให้ท่านไปเชื่อม Firebase ตามเดิม)
                    st.session_state.user = uid
                    st.session_state.logged_in = True
                    st.rerun()
    else:
        # เมื่อ Login แล้ว โชว์โลโก้บนสุดเสมอ
        show_logo(width=180)
        
        with st.sidebar:
            st.write(f"👤 AGENT: **{st.session_state.user}**")
            if st.button("🚪 LOGOUT", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

        tabs = st.tabs(["🏠 CORE", "🛰️ SCANNER", "🧬 EXTRACTOR", "🎧 MUSIC", "⚙️ SETTINGS"])
        
        with tabs[0]: st.write("ยินดีต้อนรับสู่ระบบ SYNAPSE")
        with tabs[1]: room_truth_scan()
        with tabs[2]: room_reality_extractor()
        with tabs[3]: st.write("ระบบ Music Station กำลังโหลด...")
        with tabs[4]: 
            st.session_state.theme_color = st.color_picker("ปรับแต่งสีระบบ", st.session_state.theme_color)

if __name__ == "__main__":
    main()

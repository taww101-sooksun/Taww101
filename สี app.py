import streamlit as st
import os 
import base64
import math
import time
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, timedelta
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & CLEAN UI (ลบทุกอย่างที่เป็น Streamlit)
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="expanded")

def apply_clean_ui():
    primary = st.session_state.get('theme_color', "#39FF14")
    bg = st.session_state.get('bg_color', "#000000")
    txt = st.session_state.get('text_color', "#FFFFFF")
    
    st.markdown(f"""
        <style>
        /* ซ่อน Streamlit UI */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        [data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
        
        /* พื้นหลังและฟอนต์ */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        .stApp {{
            background: {bg} !important;
            color: {txt} !important;
            font-family: 'Orbitron', sans-serif;
        }}
        
        /* สไตล์กรอบและนีออน */
        .neon-border {{
            border: 2px solid {primary};
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 0 15px {primary}44;
            margin-bottom: 20px;
        }}
        
        /* ปรับแต่ง Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background-color: rgba(0,0,0,0.5);
            padding: 10px;
            border-radius: 15px;
            border: 1px solid {primary}33;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {txt};
            border-radius: 10px;
            padding: 10px 20px;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {primary}22 !important;
            border-bottom: 3px solid {primary} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def show_branding():
    if os.path.exists("logo1.png"):
        st.image("logo1.png", width=100)
    st.markdown(f"<h3 style='margin:0; color:{st.session_state.theme_color};'>SYNAPSE</h3>", unsafe_allow_html=True)
    st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

# ==========================================
# 1. CORE LOGIC (สูตรคำนวณจริง 1950-2026)
# ==========================================
def get_synapse_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1) # จุดเริ่มต้นยุคดิจิทัลสากล
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589 # คาบการโคจรเฉลี่ยของดวงจันทร์
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1 # 1=จันทร์ ... 7=อาทิตย์ (ฐานแรงดึงดูดโลก)
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    
    if is_waxing:
        # ใช้ทฤษฎี Vector (แรงผลัก) : ความสัมพันธ์เชิงมุมระหว่างโลกและดวงจันทร์
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        explanation = "คำนวณจากแรงพีทาโกรัส (Vector) ระหว่างพลังงานประจำวันและแรงดึงดูดดวงจันทร์ช่วงขาขึ้น"
    else:
        # ใช้ทฤษฎี Golden Ratio (สมดุล) : การลดทอนพลังงานตามสัดส่วนฟี (Phi)
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        explanation = "คำนวณจากสัดส่วนทองคำ (Phi 1.618) เพื่อหาจุดสมดุลของพลังงานในช่วงจันทรคติขาลง"

    return {
        "res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ",
        "day_num": day_val, "formula": formula, "exp": explanation, "diff": diff
    }

# ==========================================
# 2. ROOMS
# ==========================================

def room_music():
    show_branding()
    m_tabs = st.tabs(["🎵 HOLOGRAPHIC PLAYER", "💿 MIXER DECK"])
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    with m_tabs[0]:
        if not songs: st.warning("NO MP3 FOUND"); return
        song = st.selectbox("CHOOSE SIGNAL", songs)
        with open(song, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
        st.markdown(f"<div class='neon-border'>ANALYZING: {song}</div>", unsafe_allow_html=True)

    with m_tabs[1]:
        st.write("DJ MIXER MODE (STANDBY)")

def room_comms_gps():
    show_branding()
    c_tabs = st.tabs(["🌐 PUBLIC CHAT", "📞 PRIVATE", "🛰️ SATELLITE GPS"])
    loc = get_geolocation()
    
    with c_tabs[2]:
        lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.75, 100.5)
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB dark_matter")
        folium.Marker([lat, lon], popup="CURRENT AGENT").add_to(m)
        st_folium(m, width="100%", height=400)

def room_logic():
    show_branding()
    l_tabs = st.tabs(["🔍 DAILY DECODER", "⚖️ GAP ANALYZER", "🔮 365 TIMELINE"])
    START, END = date(1950, 1, 1), date(2026, 12, 31)

    with l_tabs[0]:
        t_date = st.date_input("TARGET DATE", value=date.today(), min_value=START, max_value=END)
        d = get_synapse_logic(t_date)
        st.markdown(f"""
            <div class="neon-border" style="text-align:center;">
                <h1 style="color:{st.session_state.theme_color};">{d['res']}</h1>
                <p>{d['phase']} | พิกัดสะสม: {d['diff']} วัน</p>
                <hr style="border:0.5px solid {st.session_state.theme_color}33">
                <p style="font-size:12px;"><b>ที่มาความจริง:</b> {d['exp']}</p>
                <code>FORMULA: {d['formula']}</code>
            </div>
        """, unsafe_allow_html=True)

    with l_tabs[2]:
        st.write("สแกนพิกัด 365 วัน (อดีต-อนาคต)")
        # ส่วนนี้สามารถดึงตารางจากโค้ดเดิมมาใส่ได้เลย

def room_settings():
    show_branding()
    s_tabs = st.tabs(["👤 PROFILE", "🎨 THEME ENGINE", "🔐 SYSTEM"])
    with s_tabs[1]:
        st.session_state.theme_color = st.color_picker("NEON LIGHT (สีหลัก)", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("BACKGROUND (พื้นหลัง)", st.session_state.bg_color)
        st.session_state.text_color = st.color_picker("TEXT COLOR (ตัวหนังสือ)", "#FFFFFF")
        if st.button("UPDATE SYSTEM"): st.rerun()

# ==========================================
# 3. MAIN SYSTEM
# ==========================================
def main():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    
    apply_clean_ui()

    if not st.session_state.logged_in:
        # หน้า Login (หน้าแรก)
        _, col, _ = st.columns([1,2,1])
        with col:
            st.markdown("<br><br>", unsafe_allow_html=True)
            show_branding()
            with st.form("access_control"):
                u = st.text_input("AGENT ID")
                p = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("UNLOCK"):
                    st.session_state.logged_in = True
                    st.rerun()
    else:
        # เมนูหลักด้านข้าง
        with st.sidebar:
            show_branding()
            st.write("---")
            nav = st.radio("COMMAND CENTER", ["🎵 MUSIC", "💬 COMMS & GPS", "🧬 LOGIC", "⚙️ SETTINGS"])
            if st.button("🚪 LOGOUT"):
                st.session_state.logged_in = False
                st.rerun()

        if nav == "🎵 MUSIC": room_music()
        elif nav == "💬 COMMS & GPS": room_comms_gps()
        elif nav == "🧬 LOGIC": room_logic()
        elif nav == "⚙️ SETTINGS": room_settings()

if __name__ == "__main__":
    main()

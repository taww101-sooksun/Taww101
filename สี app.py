import streamlit as st
import os 
import time
import base64
import math
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "AGENT-X"
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อขัดข้อง: {e}")

def apply_custom_background():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(270deg, #111, #222, {st.session_state.theme_color}11);
            background-size: 400% 400%;
            animation: Gradient 15s ease infinite;
        }}
        @keyframes Gradient {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 15px; padding: 5px;
            border: 1px solid {st.session_state.theme_color};
            box-shadow: 0 0 10px {st.session_state.theme_color}44;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. THE MODULES (Rooms)
# ==========================================

def room_logic():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        
        # ปีนักษัตร
        thai_year = dt.year + 543
        zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
        zodiac = zodiacs[thai_year % 12]
        
        # ธาตุประจำวัน
        elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
        element = elements.get(day_val)

        if pos <= 14.765:
            m_num = int(pos) + 1
            phase = f"ขึ้น {m_num} ค่ำ"
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            p_type = "แรงผลักดัน (Vector)"
        else:
            m_num = int(pos - 14.765) + 1
            phase = f"แรม {m_num} ค่ำ"
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            p_type = "สมดุลสัดส่วนทองคำ (Phi)"
            
        return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element, "formula": formula, "type": p_type, "day_num": day_val, "lunar_num": m_num, "diff": diff}

    st.subheader("🔍 วิเคราะห์พิกัดความจริง (อดีต-อนาคต)")
    target_date = st.date_input("เลือกวันที่ตรวจสอบ", value=date.today(), min_value=date(1950,1,1), max_value=date(2026,12,31))
    
    if target_date:
        d = decode_truth(target_date)
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:20px; background:rgba(0,0,0,0.3);">
                <small>รหัสพิกัดจักรวาล</small>
                <h1 style="color:{st.session_state.theme_color}; font-size:60px; margin:0;">{d['res']}</h1>
                <p style="color:#888;">{d['type']}</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📅 **ฐานวัน ({d['day_num']}):** แรงดึงดูดโลก")
            st.info(f"🌙 **จันทรคติ ({d['phase']}):** แรงดึงดูดดวงจันทร์")
        with col2:
            st.success(f"🐎 **ปีนักษัตร:** ปี{d['zodiac']}")
            st.success(f"💎 **ธาตุประจำวัน:** ธาตุ{d['element']}")

        st.markdown(f"""
            <div style="background:#111; padding:15px; border-left:5px solid {st.session_state.theme_color}; border-radius:10px; margin-top:10px;">
                <p style="font-size:14px; color:#aaa; margin:0;">
                    <b>สูตรการคำนวณ:</b> {d['formula']}<br>
                    คำนวณจากวันที่สะสมตั้งแต่ปี 1900 รวมทั้งสิ้น {d['diff']:,} วัน
                </p>
            </div>
        """, unsafe_allow_html=True)

        if target_date < date.today(): st.warning("⏪ ตรวจสอบรอยเท้าพลังงานใน **'อดีต'**")
        elif target_date > date.today(): st.error("🔮 ตรวจสอบพิกัดเป้าหมายใน **'อนาคต'**")
        else: st.success("🟢 พิกัดพลังงานใน **'ปัจจุบัน'**")

def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ")
        return
    
    current_song = music_files[st.session_state.song_index % len(music_files)]
    st.info(f"🎵 กำลังเล่น: {current_song}")
    
    with open(current_song, "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ BACK", use_container_width=True):
        st.session_state.song_index -= 1
        st.rerun()
    if col2.button("🔄 RELOAD", use_container_width=True): 
        st.rerun()
    if col3.button("⏭️ NEXT", use_container_width=True):
        st.session_state.song_index += 1
        st.rerun()

def room_settings():
    st.subheader("🎨 SYSTEM THEME")
    color_presets = {"🟢 CYBER": "#39FF14", "🔵 DEEP": "#1408BF", "🔴 ALERT": "#FF0000", "🟣 VIBE": "#800080"}
    selected = st.selectbox("เลือกโทนสีระบบ", list(color_presets.keys()))
    if st.button("APPLY THEME", use_container_width=True):
        st.session_state.theme_color = color_presets[selected]
        st.rerun()
    
    st.write("---")
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# 2. MAIN SYSTEM
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation()

    if not st.session_state.logged_in:
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE OS</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("LOGIN", use_container_width=True):
                # ตรงนี้คุณสามารถใส่โค้ดเช็ค Firebase จริงได้
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
    else:
        st.sidebar.write(f"👤 AGENT: {st.session_state.user}")
        st.sidebar.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")
        
        tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "🎧 MUSIC", "🧬 LOGIC", "⚙️ SETTINGS"])
        with tabs[3]: room_music()
        with tabs[4]: room_logic()
        with tabs[5]: room_settings()

if __name__ == "__main__":
    main()

import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import math
import time
import folium
import firebase_admin
from firebase_admin import credentials, db
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from datetime import datetime, date

# --- [ 1. FIREBASE CONNECTION (ปลอดภัยผ่าน Secrets) ] ---
if not firebase_admin._apps:
    try:
        # ดึงข้อมูลจาก Secrets ที่คุณตั้งค่าไว้ใน Streamlit Cloud
        fb_creds = dict(st.secrets["firebase_credentials"])
        # แก้ไขเรื่องขึ้นบรรทัดใหม่ใน Private Key
        if "\\n" in fb_creds["private_key"]:
            fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://sooksun1-default-rtdb.firebaseio.com/"
        })
    except Exception as e:
        st.error(f"⚠️ Firebase Connection Error: {e}")

# --- [ 2. INITIAL SETUP ] ---
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00ff41"
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'current_page' not in st.session_state: st.session_state.current_page = "MAIN MENU"

st.set_page_config(page_title="SYNAPSE X", layout="wide")

# CSS Style
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header, footer, .stDeployButton {{visibility: hidden; display: none !important;}}
    [data-testid="stSidebar"] {{display: none;}}
    .stApp {{ background-color: #000; color: #ffffff; font-family: 'Orbitron', sans-serif; }}
    .neon-title {{ color: {st.session_state.theme_color}; text-shadow: 0 0 15px {st.session_state.theme_color}; text-align: center; margin-bottom: 25px; }}
    div.stButton > button {{ background-color: #111; border: 2px solid {st.session_state.theme_color}; color: {st.session_state.theme_color}; border-radius: 15px; padding: 15px; font-weight: bold; }}
    div.stButton > button:hover {{ background-color: {st.session_state.theme_color}; color: black; box-shadow: 0 0 20px {st.session_state.theme_color}; }}
    </style>
    """, unsafe_allow_html=True)

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- [ 3. INTERFACE LOGIC ] ---

if st.session_state.current_page == "MAIN MENU":
    st.markdown("<h1 class='neon-title'>SYNAPSE X</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 SETTINGS", use_container_width=True): go_to("SETTINGS")
        if st.button("🛰️ GPS & CHAT", use_container_width=True): go_to("GPS")
    with col2:
        if st.button("🎧 MUSIC", use_container_width=True): go_to("MUSIC")
        if st.button("🧬 DECODER", use_container_width=True): go_to("DECODER")
    if st.button("🎙️ SENSOR LAB", use_container_width=True): go_to("SENSOR")
    st.divider()
    st.caption(f"AGENT: {st.session_state.user_name} | 'อยู่นิ่งๆ ไม่เจ็บตัว'")

else:
    if st.button("⬅️ BACK TO MENU"): go_to("MAIN MENU")
    st.write("---")

    # --- PAGE: SETTINGS ---
    if st.session_state.current_page == "SETTINGS":
        st.markdown(f"<h2 class='neon-title'>SETTINGS</h2>", unsafe_allow_html=True)
        st.session_state.user_name = st.text_input("AGENT NAME", value=st.session_state.user_name)
        st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
        if st.button("SAVE"): st.rerun()

    # --- PAGE: GPS & CHAT (ระบบแชตจริง) ---
    elif st.session_state.current_page == "GPS":
        st.markdown(f"<h2 class='neon-title'>🛰️ COMMAND CENTER</h2>", unsafe_allow_html=True)
        
        loc = get_geolocation()
        my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)

        t1, t2, t3 = st.tabs(["📡 RADAR VIEW", "🌐 PUBLIC CHAT", "🔐 SECURE LINE"])

        with t1: # RADAR
            m = folium.Map(location=[my_lat, my_lon], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
            folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red')).add_to(m)
            st_folium(m, width="100%", height=400, key="radar_map")
            if st.button("📡 BROADCAST POSITION"):
                db.reference(f'users/{st.session_state.user_name}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
                st.success("ตำแหน่งอัปเดตแล้ว!")

        with t2: # PUBLIC CHAT (แชตจริง)
            with st.form("media_chat", clear_on_submit=True):
                msg = st.text_input("พิมพ์ข้อความ...")
                up_file = st.file_uploader("📸 ส่งรูป/วิดีโอ", type=['jpg','png','mp4'])
                if st.form_submit_button("📢 ส่ง"):
                    f_b64, f_type = None, None
                    if up_file:
                        f_b64 = base64.b64encode(up_file.getvalue()).decode()
                        f_type = up_file.type
                    if msg or f_b64:
                        db.reference('public_chat').push({
                            'u': st.session_state.user_name, 'm': msg, 'f': f_b64, 'ft': f_type, 'ts': time.time()
                        })
                        st.rerun()

            # แสดงผลข้อความ (Real-time ดึงจาก Firebase)
            st.write("---")
            data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
            if data:
                for k, v in reversed(list(data.items())):
                    st.markdown(f"**{v.get('u')}**: {v.get('m','')}")
                    if v.get('f'):
                        raw_f = base64.b64decode(v.get('f'))
                        if "image" in v.get('ft'): st.image(raw_f)
                        elif "video" in v.get('ft'): st.video(raw_f)

        with t3: # SECURE LINE (แชตลับ)
            all_agents = db.reference('users').get()
            friends = [u for u in all_agents.keys() if u != st.session_state.user_name] if all_agents else []
            target = st.selectbox("🎯 เลือกเป้าหมาย:", ["-- Select --"] + friends)
            
            if target != "-- Select --":
                room_id = "_".join(sorted([st.session_state.user_name, target]))
                with st.form("priv_form", clear_on_submit=True):
                    p_msg = st.text_input("ข้อความลับ...")
                    if st.form_submit_button("🚀 ส่งลับ"):
                        db.reference(f'private/{room_id}').push({
                            'u': st.session_state.user_name, 'm': p_msg, 'ts': time.time()
                        })
                        st.rerun()
                # แสดงแชตลับ
                p_data = db.reference(f'private/{room_id}').limit_to_last(5).get()
                if p_data:
                    for pk, pv in list(p_data.items()):
                        st.caption(f"{pv.get('u')}: {pv.get('m')}")

    # --- หน้าอื่นๆ (MUSIC, DECODER, SENSOR) ---
    elif st.session_state.current_page == "MUSIC":
        # ... (ใส่โค้ด Music ของคุณตามเดิม) ...
        st.write("DJ STATION ACTIVE")
    
    elif st.session_state.current_page == "DECODER":
        st.markdown("<h2 class='neon-title'>COSMIC DECODER</h2>", unsafe_allow_html=True)
        st.write("รหัสฐานวัน:", round(date.today().isoweekday() * 1.618, 4))
        
    elif st.session_state.current_page == "SENSOR":
        st.info("Scanning Vibrations...")

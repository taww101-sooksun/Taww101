import streamlit as st
import os 
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib

# ==========================================
# 1. CORE SYSTEM & AUTHENTICATION
# ==========================================
def init_system():
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'auth_status' not in st.session_state: st.session_status = False
    if 'user' not in st.session_state: st.session_state.user = None

    if not firebase_admin._apps:
        try:
            # ตรวจสอบว่ามี secrets ครบไหม
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def apply_theme():
    themes = {
        "Matrix":  {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF", "chat_user": "#39FF14", "chat_friend": "#333"},
        "Ocean":   {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC", "chat_user": "#00A8E8", "chat_friend": "#005F73"},
        "Ember":   {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF", "chat_user": "#FF4D4D", "chat_friend": "#990000"},
        "Rainbow": {"bg": "#FFFFFF", "main": "#FF69B4", "text": "#000000", "chat_user": "#FFB6C1", "chat_friend": "#E0FFFF"}
    }
    t = themes.get(st.session_state.theme_set, themes["Matrix"])
    bg_style = f"background-color: {t['bg']} !important;"
    if st.session_state.theme_set == "Rainbow":
        bg_style = "background: linear-gradient(135deg, #FF99CC, #99CCFF, #99FFCC) !important;"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} color: {t['text']} !important; }}
        .stButton>button {{ border: 2px solid {t['main']} !important; color: {t['text']} !important; background: {t['main']} !important; border-radius: 12px; font-weight: bold; width: 100%; }}
        h1, h2, h3, p, span, label, .stMarkdown, .stMetric {{ color: {t['text']} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 2. GPS RADAR (Hybrid Satellite Mode)
# ==========================================
def room_gps(theme):
    st.subheader("🛰️ ระบบเรดาร์ระบุตำแหน่ง (Hybrid Mode)")
    
    loc = get_geolocation()
    if loc:
        try:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            
            # อัปเดตลง Firebase
            db.reference(f'locations/{st.session_state.user}').update({
                'lat': lat, 'lon': lon, 'ts': time.time(),
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            col1, col2 = st.columns(2)
            col1.metric("LATITUDE", f"{lat:.6f}")
            col2.metric("LONGITUDE", f"{lon:.6f}")

            # แผนที่แบบ Hybrid (ดาวเทียม + ถนนภาษาไทย)
            google_hybrid = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
            m = folium.Map(
                location=[lat, lon], 
                zoom_start=18, 
                tiles=google_hybrid, 
                attr='Google'
            )

            folium.Marker(
                [lat, lon], 
                popup=f"USER: {st.session_state.user}",
                tooltip="ตำแหน่งของคุณ",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)

            # แสดงผลแผนที่
            st_folium(m, width=700, height=500)

        except Exception as e:
            st.error(f"❌ GPS Error: {e}")
    else:
        st.info("⌛ กำลังรอสัญญาณจากดาวเทียม... (กรุณากด Allow Location ในเบราว์เซอร์)")

# ==========================================
# 3. COMMUNICATION & MUSIC (ส่วนที่เหลือคงเดิม)
# ==========================================
# [ใส่ฟังก์ชัน room_comms และ room_music ตามที่คุณเขียนมาได้เลย]

def main():
    init_system()
    if not st.session_state.get('auth_status', False):
        st.title("🛡️ SYNAPSE LOGIN")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ENTER"):
            acc = db.reference(f'accounts/{u}').get()
            if acc and acc.get('pw') == hash_pw(p):
                st.session_state.auth_status, st.session_state.user = True, u
                st.rerun()
            else: st.error("❌ Access Denied")
        return

    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.session_state.theme_set = st.radio("🎨 Theme:", ["Matrix", "Ocean", "Ember", "Rainbow"])
        if st.button("🚪 LOGOUT"): 
            st.session_state.auth_status = False
            st.rerun()
    
    t = apply_theme()
    tabs = st.tabs(["🛰️ เรดาร์", "💬 สื่อสาร", "🎧 เพลง"])
    
    with tabs[0]: room_gps(t)
    with tabs[1]: st.info("ระบบสื่อสารกำลังออนไลน์...") # เรียกฟังก์ชัน room_comms
    with tabs[2]: st.info("เครื่องเล่นเพลงพร้อมใช้งาน...") # เรียกฟังก์ชัน room_music

if __name__ == "__main__":
    main()

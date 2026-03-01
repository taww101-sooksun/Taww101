import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
import os
import time
import pandas as pd
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME (แก้ Error ตัวหนังสือยึกยือ)
# ==========================================
st.set_page_config(page_title="SYNAPSE GLOBAL", layout="wide")
st_autorefresh(interval=10000, key="global_refresh")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    .neon-header { 
        font-size: 35px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #ff00de;
        border: 2px solid #00f2fe; padding: 10px; background: rgba(0,0,0,0.8);
        border-radius: 10px; margin-bottom: 20px; letter-spacing: 10px;
    }
    .login-box {
        border: 2px solid #ff00de; padding: 30px; border-radius: 15px;
        background: rgba(0,0,0,0.9); text-align: center; max-width: 500px; margin: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE CONNECTION
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

# ==========================================
# 3. 🛡️ หน้าด่านลงชื่อเข้าใช้ (LOGIN GATE)
# ==========================================
if 'logged_in' not in st.session_state:
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-header">SYNAPSE GATEWAY</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        u_id = st.text_input("ระบุชื่อรหัส AGENT ของคุณ:", placeholder="เช่น Ta101, Neo...")
        u_color = st.color_picker("เลือกสีหมุดประจำตัว (สำหรับแสดงทั่วโลก):", "#00f2fe")
        
        if st.button("🔓 INITIALIZE CONNECTION", use_container_width=True):
            if u_id:
                st.session_state.logged_in = True
                st.session_state.user_id = u_id
                st.session_state.user_color = u_color
                st.rerun()
            else:
                st.warning("⚠️ กรุณาระบุชื่อก่อนเข้าสู่โครงข่าย")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # หยุดหน้าอื่นไว้จนกว่าจะ Login

# ==========================================
# 4. หน้าจอหลัก (COMMAND CENTER) เมื่อ Login แล้ว
# ==========================================
user_id = st.session_state.user_id
user_color = st.session_state.user_color

# ส่วนหัว (World Clock)
st.markdown(f'<div class="neon-header">COMMAND CENTER: {user_id}</div>', unsafe_allow_html=True)

# ดึงพิกัดจริงส่งเข้า Firebase ทันที
loc = get_geolocation()
if loc:
    db.reference(f'users/{user_id}').update({
        'lat': loc['coords']['latitude'], 
        'lon': loc['coords']['longitude'],
        'color': user_color,
        'ts': time.time()
    })

# ระบบเพลงและโลโก้ใน Sidebar
with st.sidebar:
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg")
    audio_file = "ยักษ์ในตัวฉัน.mp3"
    if os.path.exists(audio_file): st.audio(audio_file, format="audio/mp3", loop=True)
    st.markdown(f"AGENT: <b style='color:{user_color};'>{user_id}</b>", unsafe_allow_html=True)

# 🚀 TABS ใช้งานจริง
tabs = st.tabs(["🛰️ เรดาร์โลก", "💬 แชตแยก", "📊 ข้อมูล", "🧹 ระบบ"])

with tabs[0]: # RADAR (พิกัดตรง + แยกสีตามที่คนเลือก)
    users = db.reference('users').get()
    center = [13.75, 100.5]
    if users and user_id in users:
        center = [users[user_id].get('lat'), users[user_id].get('lon')]

    m = folium.Map(location=center, zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    if users:
        for u, data in users.items():
            if isinstance(data, dict) and 'lat' in data:
                # ใช้สีที่ Agent คนนั้นเลือกไว้มาปักหมุด
                p_color = data.get('color', '#ff0000') 
                folium.CircleMarker(
                    location=[data['lat'], data['lon']], radius=10,
                    popup=u, color=p_color, fill=True, fill_color=p_color
                ).add_to(m)
    st_folium(m, width="100%", height=500)

with tabs[1]: # แชต
    st.subheader("🗨️ GLOBAL COMMS")
    msg = st.chat_input("TRANSMIT MESSAGE...")
    if msg: db.reference('global_chat').push({'user': user_id, 'msg': msg, 'ts': time.time()})
    
    chat_data = db.reference('global_chat').get()
    if chat_data:
        for c in list(chat_data.values())[-5:]:
            st.write(f"📌 **{c.get('user')}**: {c.get('msg')}")

with tabs[3]: # ล้างระบบ
    if st.button("🔥 WIPE DATABASE"):
        db.reference('/').delete()
        st.rerun()

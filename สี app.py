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
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh
from geopy.distance import geodesic

# ==========================================
# 1. CORE CONFIG & REFRESH
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

# สไตล์ Neon (ห้ามเอาออกตามสั่ง)
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    .neon-header { 
        font-size: 40px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
        border: 10px double #ff1744; padding: 20px; background: rgba(0,0,0,0.85);
        border-radius: 20px; margin-bottom: 30px;
    }
    .terminal-container {
        border: 1px solid rgba(0, 242, 254, 0.5); padding: 20px; border-radius: 10px;
        background: rgba(0, 5, 15, 0.9); border-left: 8px solid #00f2fe;
    }
    .clock-box { background: rgba(0, 242, 254, 0.1); border: 1px solid #00f2fe; padding: 10px; border-radius: 10px; text-align: center; }
    .bubble-me { background: rgba(0, 242, 254, 0.15); border: 2px solid #00f2fe; padding: 12px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; text-align: right; }
    .bubble-others { background: rgba(255, 23, 68, 0.15); border: 2px solid #ff1744; padding: 12px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; text-align: left; }
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
    except Exception as e:
        st.error(f"FIREBASE CONNECTION ERROR: {e}")

# ==========================================
# 3. HEADER & WORLD CLOCK
# ==========================================
st.markdown('<div class="neon-header">SYNAPSE COMMAND</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><small>{city}</small><br><b style='color:#ff1744;'>{now}</b></div>", unsafe_allow_html=True)

# ==========================================
# 4. TABS DEFINITION (ป้องกัน NameError)
# ==========================================
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 10-UNITS", "🔐 SECURITY", "📺 MEDIA", "🧹 SYSTEM"])

# --- TAB 1: CORE ---
with tabs[0]:
    st.session_state.my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Agent_01'))
    if st.button("🚀 INITIATE QUANTUM LINK"):
        loc = get_geolocation()
        if loc:
            db.reference(f'users/{st.session_state.my_name}').update({
                'lat': loc['coords']['latitude'], 
                'lon': loc['coords']['longitude'],
                'status': 'ACTIVE',
                'last_sync': time.time()
            })
            st.success("LINK ESTABLISHED.")

# ดึงข้อมูลจากฐานข้อมูลมาใช้ใน Tab ต่างๆ (ของจริง)
all_users = db.reference('users').get()

# --- TAB 2: RADAR ---
with tabs[1]:
    m = folium.Map(location=[13.75, 100.5], zoom_start=4, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    if all_users:
        for name, info in all_users.items():
            if isinstance(info, dict) and 'lat' in info:
                folium.Marker([info['lat'], info['lon']], tooltip=name).add_to(m)
    st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS (แก้ปัญหา KeyError) ---
with tabs[2]:
    current_user = st.session_state.get('my_name', 'Unknown_Agent')
    msg = st.chat_input("ส่งข้อความถึงกองบัญชาการ...")
    if msg:
        db.reference('global_chat').push({'name': current_user, 'msg': msg, 'ts': time.time()})
    
    chats = db.reference('global_chat').get()
    if chats:
        for c in sorted(chats.values(), key=lambda x: x.get('ts', 0))[-10:]:
            sender = c.get('name', 'Anonymous')
            style = "bubble-me" if sender == current_user else "bubble-others"
            st.markdown(f"<div class='{style}'><small>{sender}</small><br>{c.get('msg', '')}</div>", unsafe_allow_html=True)

# --- TAB 4: 10-UNITS ---
with tabs[3]:
    if all_users:
        st.dataframe(pd.DataFrame.from_dict(all_users, orient='index'), use_container_width=True)
    else: st.info("NO DATA IN DATABASE")

# --- TAB 5: SECURITY ---
with tabs[4]:
    st.warning("GEOFENCE ACTIVE: รัศมี 50KM จากศูนย์บัญชาการ")
    if all_users and st.session_state.get('my_name') in all_users:
        me = all_users[st.session_state.my_name]
        if 'lat' in me:
            d = geodesic((13.75, 100.5), (me['lat'], me['lon'])).km
            st.metric("ระยะห่างจากฐาน (KM)", f"{d:.2f}")

# --- TAB 6 & 7: MEDIA & SYSTEM ---
with tabs[5]: st.video("https://www.youtube.com/watch?v=f0h8PjdZzrw")
with tabs[6]:
    if st.button("🧹 WIPE DATABASE"):
        db.reference('/').delete()
        st.success("CLEARED.")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a") # เพลงเดิม
    st.write(f"USER: {st.session_state.get('my_name', 'N/A')}")

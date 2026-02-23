import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import os

# --- 1. INITIALIZE FIREBASE ---
st.set_page_config(page_title="SYNAPSE RADAR", layout="wide")

if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"Firebase Connection Error: {e}")

# --- 2. SECURITY GATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 ACCESS CONTROL</h2>", unsafe_allow_html=True)
    with st.form("Login"):
        u_id = st.text_input("Enter ID")
        u_pw = st.text_input("Password", type="password")
        if st.form_submit_button("UNLOCK"):
            if u_pw == "synapse2026" and u_id: 
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #1e1e1e, #2d3436, #000000); background-size: 400% 400%; animation: RainbowFlow 30s ease infinite; color: white; }
    .stMetric { background-color: rgba(255, 255, 255, 0.1) !important; border-radius: 10px; border: 1px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 SYNAPSE RADAR SYSTEM")
st.write(f"Logged in as: **{my_id}** | สโลแกน: *อยู่นิ่งๆ ไม่เจ็บตัว*")

# ดึงข้อมูลผู้ใช้ทั้งหมดจาก Firebase
all_users = db.reference('/users').get() or {}
friend_options = [u for u in all_users.keys() if u != my_id]

# --- 4. CHAT SYSTEM (เน้นแชท ไม่เน้นโทร) ---
with st.sidebar:
    st.header("💬 MESSENGER")
    chat_target = st.selectbox("เลือกเพื่อน", ["-- Select --"] + friend_options)
    if chat_target != "-- Select --":
        ids = sorted([my_id, chat_target])
        chat_id = f"chat_{ids[0]}_{ids[1]}"
        
        msgs = db.reference(f'/messages/{chat_id}').order_by_child('timestamp').limit_to_last(10).get()
        if msgs:
            for m_id, m_data in msgs.items():
                sender = "ME" if m_data['sender'] == my_id else m_data['sender']
                st.write(f"**{sender}:** {m_data['text']}")
        
        with st.form("send_msg", clear_on_submit=True):
            m_text = st.text_input("Message...")
            if st.form_submit_button("SEND"):
                db.reference(f'/messages/{chat_id}').push({
                    'sender': my_id, 'text': m_text, 'timestamp': datetime.now().isoformat()
                })
                st.rerun()

# --- 5. GPS & TACTICAL MAP ---
location = get_geolocation()
if location:
    coords = location.get('coords', {})
    lat, lon = coords.get('latitude'), coords.get('longitude')
    
    if lat and lon:
        # อัปเดตตำแหน่งตัวเองขึ้น Cloud
        db.reference(f'/users/{my_id}/location').update({
            'lat': lat, 'lon': lon, 'last_update': datetime.now().strftime('%H:%M:%S')
        })

        # สร้างแผนที่ Hybrid
        m = folium.Map(location=[lat, lon], zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')

        # วนลูปปักหมุดทุกคนในระบบ
        for user_id, user_data in all_users.items():
            if 'location' in user_data:
                u_lat = user_data['location'].get('lat')
                u_lon = user_data['location'].get('lon')
                u_time = user_data['location'].get('last_update', 'N/A')
                
                if u_lat and u_lon:
                    # ตั้งค่าสีและไอคอน: แดง=เรา, น้ำเงิน=เพื่อน
                    is_me = (user_id == my_id)
                    marker_color = 'red' if is_me else 'blue'
                    icon_type = 'star' if is_me else 'user'
                    label_name = f"YOU ({user_id})" if is_me else user_id

                    # ปักหมุด
                    folium.Marker(
                        [u_lat, u_lon],
                        popup=f"ID: {user_id}<br>Time: {u_time}",
                        tooltip=label_name,
                        icon=folium.Icon(color=marker_color, icon=icon_type, prefix='fa')
                    ).add_to(m)

                    # เพิ่มข้อความชื่อลอยบนแผนที่ (จะได้เห็นชัดๆ ว่ามุดไหนของใคร)
                    folium.map.Marker(
                        [u_lat, u_lon],
                        icon=folium.features.DivIcon(
                            icon_size=(150,36),
                            icon_anchor=(0,0),
                            html=f'<div style="font-size: 12pt; color: {marker_color}; font-weight: bold; text-shadow: 2px 2px black;">{label_name}</div>',
                        )
                    ).add_to(m)

        # แสดงผลแผนที่
        st_folium(m, use_container_width=True, height=600)
    else:
        st.warning("🛰️ กำลังจับสัญญาณดาวเทียม...")
else:
    st.info("💡 โปรดเปิด GPS เพื่อใช้งานระบบแผนที่")

st.caption("SYNAPSE V2.3 | REAL-TIME FRIEND TRACKER | NO LIES")

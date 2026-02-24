import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pandas as pd
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="SYNAPSE - Music Therapy", layout="wide")

# 2. เชื่อมต่อ Firebase
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
    except Exception as e:
        st.error(f"Firebase Connection Error: {e}")

# --- ส่วนหัวและโลโก้ ---
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.write("🌐")
with col2:
    st.title("SYNAPSE - Music Therapy")

# ดึงพิกัด GPS (ทำงานเบื้องหลัง)
location = get_geolocation()

# 3. สร้าง 3 Tab
tab1, tab2, tab3 = st.tabs(["🚀 สำหรับเพื่อน", "📊 Dashboard", "💬 ห้องสนทนา"])

with tab1:
    st.header("เริ่มการเดินทางของคุณ")
    user_id = st.text_input("ระบุชื่อหรือรหัสของคุณ:", placeholder="เช่น Ta101", key="user_input")
    
    if st.button("Start Journey", key="main_start_btn"):
        if user_id:
            if location and 'coords' in location:
                try:
                    lat = location['coords']['latitude']
                    lon = location['coords']['longitude']
                    now = datetime.datetime.now()
                    
                    # เลือกเพลงตามเวลา
                    song_path = "test_morning.mp3" if 6 <= now.hour < 12 else "test_evening.mp3"
                    
                    if firebase_admin._apps:
                        db.reference(f'users/{user_id}').set({
                            'last_seen': str(now),
                            'lat': lat,
                            'lon': lon,
                            'status': "Online"
                        })
                        st.success(f"เชื่อมต่อสำเร็จ! พิกัดปัจจุบันของคุณ: {lat}, {lon}")
                        if os.path.exists(song_path):
                            st.audio(song_path)
                        else:
                            st.info("กำลังรอไฟล์เพลง...")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการส่งข้อมูล: {e}")
            else:
                st.warning("⚠️ กรุณากด 'Allow' เพื่อเปิด GPS หรือรอสัญญาณสักครู่")
        else:
            st.warning("กรุณาใส่ชื่อก่อนนะครับเพื่อน")

with tab2:
    st.header("📊 แผนที่ติดตามตำแหน่ง")
    if firebase_admin._apps:
        try:
            users_ref = db.reference('users').get()
            if users_ref:
                map

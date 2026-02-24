import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pandas as pd
import os
from streamlit_js_eval import get_geolocation  # ตัวดึง GPS จริง

# 1. เชื่อมต่อ Firebase (ใช้กุญแจจาก Secrets)
if not firebase_admin._apps:
    try:
        fb_conf = st.secrets["firebase"]
        creds = credentials.Certificate(dict(fb_conf))
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"การเชื่อมต่อ Firebase มีปัญหา: {e}")

st.title("🌐 SYNAPSE - Music Therapy")

# --- ส่วนดึงพิกัด GPS จริง ---
# ตัวนี้จะเด้งถาม "Allow location access?" บนหน้าจอมือถือ/คอม
location = get_geolocation()

tab1, tab2 = st.tabs(["🚀 สำหรับเพื่อน", "📊 Dashboard ของเรา"])

with tab1:
    st.header("เริ่มการเดินทางของคุณ")
    user_id = st.text_input("ระบุชื่อหรือรหัสของคุณ:", placeholder="เช่น A001")
    
    if st.button("Start Journey"):
        if user_id:
            # --- ส่วนที่วางต่อจากบรรทัดที่ 34 ---

tab1, tab2 = st.tabs(["🚀 สำหรับเพื่อน", "📊 Dashboard ของเรา"])

with tab1:
    st.header("เริ่มการเดินทางของคุณ")
    user_id = st.text_input("ระบุชื่อหรือรหัสของคุณ:", placeholder="เช่น Ta101")
    
    if st.button("Start Journey"):
        if user_id:
            # 1. เช็กก่อนว่ามีข้อมูลพิกัดส่งมาจาก Browser หรือยัง
            if location and 'coords' in location:
                try:
                    lat = location['coords']['latitude']
                    lon = location['coords']['longitude']
                    
                    now = datetime.datetime.now()
                    current_hour = now.hour
                    
                    # 2. ตรรกะเลือกเพลง (ไฟล์ต้องอยู่ข้าง app.py ใน GitHub)
                    if 6 <= current_hour < 12:
                        song_path = "test_morning.mp3"
                        status = "เช้าอันสดใส"
                    else:
                        song_path = "test_evening.mp3"
                        status = "เย็นที่ผ่อนคลาย"

                    # 3. ส่ง "พิกัดจริง" เข้า Firebase
                    ref = db.reference(f'users/{user_id}')
                    ref.set({
                        'last_seen': str(now),
                        'lat': lat,
                        'lon': lon,
                        'status': status
                    })

                    st.success(f"เชื่อมต่อสำเร็จ! พิกัดของคุณคือ: {lat}, {lon}")
                    
                    # 4. เล่นเพลง
                    if os.path.exists(song_path):
                        st.audio(song_path)
                    else:
                        st.error(f"ไม่พบไฟล์ {song_path} ใน GitHub ของคุณ")
                
                except Exception as e:
                    st.error("เกิดข้อผิดพลาดในการประมวลผลพิกัด")
            else:
                # ถ้า GPS ยังไม่มา หรือยังไม่ได้กด Allow
                st.warning("⚠️ รอสักครู่ครับเพื่อน! ระบบกำลังดึง GPS กรุณากด 'Allow' ที่หน้าจอ หรือรอให้สัญญาณมาถึงก่อนนะครับ")
        else:
            st.warning("กรุณาใส่ชื่อก่อนนะครับเพื่อน")

with tab2:
    st.header("📊 สถานะและการติดตามพิกัด")
    users_ref = db.reference('users').get()
    
    if users_ref:
        map_data = []
        for uid, info in users_ref.items():
            if isinstance(info, dict) and 'lat' in info and 'lon' in info:
                map_data.append({
                    'User': uid,
                    'latitude': float(info['lat']),
                    'longitude': float(info['lon']),
                    'Status': info.get('status', 'N/A')
                })
        
        if map_data:
            df = pd.DataFrame(map_data)
            st.map(df) # แผนที่จะขึ้นตรงนี้!
            st.dataframe(df) # แสดงตารางตรวจสอบพิกัด
        else:
            st.info("มีรายชื่อในระบบ แต่ยังไม่มีข้อมูลพิกัด (Lat/Lon)")
    else:
        st.write("ยังไม่มีใครเชื่อมต่อเข้ามาครับ")


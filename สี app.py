import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pandas as pd
import os

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

# --- สร้าง Tabs (จุดนี้แหละที่สำคัญ ห้ามลบนะครับ) ---
tab1, tab2 = st.tabs(["🚀 สำหรับเพื่อน", "📊 Dashboard ของเรา"])

with tab1:
    st.header("เริ่มการเดินทางของคุณ")
    user_id = st.text_input("ระบุชื่อหรือรหัสของคุณ:", placeholder="เช่น A001")
    
    if st.button("Start Journey"):
        if user_id:
            now = datetime.datetime.now()
            current_hour = now.hour
            
            # ตรรกะเลือกเพลง (ตามที่คุณบอกว่าไฟล์อยู่ข้างนอกและเป็นตัวเล็กหมด)
            if 6 <= current_hour < 12:
                song_path = "test_morning.mp3"
                status = "เช้าอันสดใส"
            else:
                song_path = "test_evening.mp3"
                status = "เย็นที่ผ่อนคลาย"

            # ส่งค่าขึ้น Firebase (จำลองพิกัดกรุงเทพฯ ไปก่อนเพื่อให้แผนที่ขึ้น)
            ref = db.reference(f'users/{user_id}')
            ref.set({
                'last_seen': str(now),
                'status': status,
                'lat': 13.7563, # พิกัดทดสอบ
                'lon': 100.5018, # พิกัดทดสอบ
                'song': song_path
            })

            st.success(f"เชื่อมต่อสำเร็จ! ขณะนี้เป็นเวลา {now.strftime('%H:%M')}")
            
            # การเล่นเพลง
            if os.path.exists(song_path):
                st.audio(song_path)
            else:
                st.error(f"หาไฟล์ {song_path} ไม่เจอ ลองเช็คชื่อไฟล์ใน GitHub อีกทีนะ")
        else:
            st.warning("กรุณาใส่ชื่อก่อนนะครับ")

with tab2:
    st.header("📊 สถานะและการติดตามพิกัด")
    users_ref = db.reference('users').get()
    
    if users_ref:
        map_data = []
        for uid, info in users_ref.items():
            if isinstance(info, dict) and 'lat' in info and 'lon' in info:
                map_data.append({
                    'User': uid,
                    'latitude': info['lat'],
                    'longitude': info['lon'],
                    'Status': info.get('status', 'N/A')
                })
        
        if map_data:
            df = pd.DataFrame(map_data)
            st.map(df) # แผนที่จะขึ้นตรงนี้!
            st.table(df) # ตารางสรุปข้อมูล
        else:
            st.info("มีผู้ใช้งานแต่ยังไม่มีพิกัดส่งมา")
    else:
        st.write("ยังไม่มีใครเชื่อมต่อเข้ามาครับ")

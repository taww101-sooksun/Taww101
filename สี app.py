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
st.set_page_config(page_title="SYNAPSE", layout="wide")

# 2. เชื่อมต่อ Firebase
if not firebase_admin._apps:
    try:
        fb_conf = st.secrets["firebase"]
        creds = credentials.Certificate(dict(fb_conf))
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"Firebase Error: {e}")

st.title("🌐 SYNAPSE - Music Therapy")

# 3. ดึงพิกัด GPS จริงจาก Browser
location = get_geolocation()

tab1, tab2 = st.tabs(["🚀 สำหรับเพื่อน", "📊 Dashboard ของเรา"])

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
                    
                    # เลือกเพลงตามเวลา (ไฟล์อยู่ที่หน้าแรกของ GitHub)
                    song_path = "test_morning.mp3" if 6 <= now.hour < 12 else "test_evening.mp3"
                    status = "เช้าอันสดใส" if 6 <= now.hour < 12 else "เย็นที่ผ่อนคลาย"

                    # ส่งข้อมูลไป Firebase
                    ref = db.reference(f'users/{user_id}')
                    ref.set({
                        'last_seen': str(now),
                        'lat': lat,
                        'lon': lon,
                        'status': status
                    })

                    st.success(f"เชื่อมต่อสำเร็จ! พิกัดปัจจุบัน: {lat}, {lon}")
                    
                    if os.path.exists(song_path):
                        st.audio(song_path)
                    else:
                        st.error(f"ไม่พบไฟล์ {song_path} ใน GitHub (เช็คตัวเล็กตัวใหญ่ด้วยนะ)")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
            else:
                st.warning("⚠️ กรุณากด 'Allow' เพื่อเปิด GPS หรือรอสัญญาณสักครู่ครับ")
        else:
            st.warning("กรุณาใส่ชื่อก่อนนะครับ")

    
    if users_ref:
        map_points = []
        for uid, info in users_ref.items():
            if isinstance(info, dict) and 'lat' in info and 'lon' in info:
                map_points.append({
                    'lat': float(info['lat']),
                    'lon': float(info['lon']),
                    'name': uid
                })
        
        if map_points:
            # สร้างแผนที่ Folium (Zoom เห็นถนนชัดเจน)
            center_lat = map_points[0]['lat']
            center_lon = map_points[0]['lon']
            m = folium.Map(location=[center_lat, center_lon], zoom_start=15) # zoom 15 จะเห็นถนนชัดมาก
            
            for point in map_points:
                folium.Marker(
                    [point['lat'], point['lon']], 
                    popup=point['name'],
                    tooltip=point['name']
                ).add_to(m)
            
            # แสดงแผนที่
            st_folium(m, width=None, height=500)
            st.write("รายชื่อผู้ใช้ปัจจุบัน:")
            st.dataframe(pd.DataFrame(map_points))
        else:
            st.info("ยังไม่มีข้อมูลพิกัดในระบบ")
    else:
        st.write("ยังไม่มีใครออนไลน์ครับ")

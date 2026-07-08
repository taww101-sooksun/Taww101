import streamlit as st
import pandas as pd
import math
import random
import folium
from streamlit_folium import st_folium

# --- 1. ตั้งค่าหน้าตาของแอป ---
st.set_page_config(page_title="Radar Tracker", page_icon="✈️", layout="centered")

st.title("📡 ระบบจำลองค้นหาอากาศยานและโดรน (รัศมี 2 กม.)")
st.write("แอปพลิเคชันนี้คำนวณระยะทางจริงด้วยสูตร Haversine และแสดงผลบนแผนที่อย่างปลอดภัย")

# --- 2. ฟังก์ชันคำนวณระยะทางตามหลักภูมิศาสตร์จริง ---
def haversine(lat1, lon1, lat2, lon2):
    # แปลงองศาเป็นเรเดียน
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # รัศมีโลก (กิโลเมตร)
    return c * r

# --- 3. ฟังก์ชันจำลองข้อมูลโดรน/เครื่องบินรอบตัว ---
def generate_mock_data(center_lat, center_lon):
    targets = []
    names = ["DJI-Mavic3", "FPV-Drone-X", "THA-923", "NokAir-402", "Survey-Drone"]
    types = ["Drone", "Drone", "Airplane", "Airplane", "Drone"]
    
    for i in range(5):
        # สุ่มให้อยู่ใกล้บ้าง ไกลบ้าง (บวกลบพิกัดสุ่ม)
        mock_lat = center_lat + random.uniform(-0.03, 0.03)
        mock_lon = center_lon + random.uniform(-0.03, 0.03)
        distance = haversine(center_lat, center_lon, mock_lat, mock_lon)
        
        targets.append({
            "ID": names[i],
            "Type": types[i],
            "Latitude": mock_lat,
            "Longitude": mock_lon,
            "Distance_KM": round(distance, 2),
            "Altitude_FT": random.randint(100, 1500) if types[i] == "Drone" else random.randint(10000, 30000)
        })
    return pd.DataFrame(targets)

# --- 4. จัดการ State และพิกัดศูนย์กลาง (ตัวคุณ) ---
# สมมติพิกัดเริ่มต้น (เปลี่ยนเป็นจุดที่นายอยู่ได้เลย)
MY_LAT = 13.6900
MY_LON = 100.7500
RADIUS_LIMIT = 2.0  # รัศมี 2 กิโลเมตร

if 'aircraft_df' not in st.session_state:
    # รันครั้งแรก ให้สร้างข้อมูลจำลองไว้ก่อน
    st.session_state.aircraft_df = generate_mock_data(MY_LAT, MY_LON)

# --- 5. ส่วนควบคุมการทำงาน (UI) ---
col1, col2 = st.columns([3, 1])

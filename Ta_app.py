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
with col1:
    st.info(f"📍 พิกัดของคุณ: {MY_LAT}, {MY_LON} | ค้นหาในรัศมี: {RADIUS_LIMIT} กม.")
with col2:
    # ปุ่มกดอัปเดตข้อมูลใหม่ (ปลอดภัย ไม่ทำหน้าเว็บพัง)
    if st.button("🔄 กดสแกนพิกัดใหม่", use_container_width=True):
        st.session_state.aircraft_df = generate_mock_data(MY_LAT, MY_LON)
        st.rerun()

# กรองข้อมูลเอาเฉพาะลำที่อยู่ในระยะ 2 กม.
all_df = st.session_state.aircraft_df
nearby_df = all_df[all_df['Distance_KM'] <= RADIUS_LIMIT]

# --- 6. ส่วนการแสดงผลแผนที่ (จุดที่เคยบั๊ก บล็อกพื้นที่ไว้ตรงนี้) ---
st.subheader("🗺️ แผนที่แสดงผลการตรวจจับ")

map_placeholder = st.empty()

with map_placeholder.container():
    # สร้างแผนที่ Folium ตั้งต้นที่พิกัดของเรา
    m = folium.Map(location=[MY_LAT, MY_LON], zoom_start=14, control_scale=True)
    
    # 🔵 ปักหมุดตัวเราเอง (จุดศูนย์กลาง)
    folium.Marker(
        [MY_LAT, MY_LON], 
        popup="ตำแหน่งของคุณ", 
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)
    
    # วาดวงกลมรัศมี 2 กิโลเมตรรอบตัว
    folium.Circle(
        location=[MY_LAT, MY_LON],
        radius=RADIUS_LIMIT * 1000, # แปลงเป็นเมตร
        color="red",
        fill=True,
        fill_opacity=0.1
    ).add_to(m)
    
    # 🔴 ปักหมุดอากาศยานที่ตรวจเจอในรัศมี 2 กม.
    for idx, row in nearby_df.iterrows():
        icon_type = "plane" if row['Type'] == "Airplane" else "cloud"
        color_type = "orange" if row['Type'] == "Airplane" else "red"
        
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=f"ID: {row['ID']}<br>ระยะ: {row['Distance_KM']} กม.<br>ความสูง: {row['Altitude_FT']} ฟุต",
            icon=folium.Icon(color=color_type, icon=icon_type)
        ).add_to(m)
    
    # แสดงผลแผนที่ใน Streamlit (ใส่ key ล็อกไว้ ป้องกันตัวลบ Node เอ๋อ)
    st_folium(m, key="safe_radar_map", width=700, height=450, returned_objects=[])

# --- 7. ตารางสรุปข้อมูลด้านล่าง ---
st.subheader("📊 รายการอากาศยานรอบตัว")

tab1, tab2 = st.tabs([f"🎯 ในรัศมี 2 กม. ({len(nearby_df)} ลำ)", f"🌐 ทั้งหมดที่ตรวจจับได้ ({len(all_df)} ลำ)"])

with tab1:
    if not nearby_df.empty:
        st.dataframe(nearby_df[['ID', 'Type', 'Distance_KM', 'Altitude_FT']], use_container_width=True)
    else:
        st.success("🟢 เคลียร์! ไม่มีโดรนหรือเครื่องบินแปลกปลอมเข้ามาในระยะ 2 กิโลเมตร")

with tab2:
    st.dataframe(all_df[['ID', 'Type', 'Distance_KM', 'Altitude_FT']], use_container_width=True)

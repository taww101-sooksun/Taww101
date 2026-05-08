import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64
import json

# --- 1. ตั้งค่าหน้าจอและซ่อน UI ที่ไม่จำเป็น ---
st.set_page_config(page_title="SYNAPSE RADAR", layout="wide")

# CSS สำหรับซ่อนเมนูและทำโลโก้นีออนเต้น
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0e1117; }
    
    @keyframes neon-glow {
        0% { filter: drop-shadow(0 0 5px #00FF00) drop-shadow(0 0 10px #00FF00); }
        50% { filter: drop-shadow(0 0 15px #00FF00) drop-shadow(0 0 25px #00FF00); }
        100% { filter: drop-shadow(0 0 5px #00FF00) drop-shadow(0 0 10px #00FF00); }
    }

    .neon-logo {
        width: 100%;
        max-width: 200px;
        display: block;
        margin: 0 auto;
        animation: neon-glow 2s infinite ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชันช่วย (Helper Functions) ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) * R

# --- 3. เชื่อมต่อ FIREBASE (ดึงจาก st.secrets) ---
if not firebase_admin._apps:
    try:
        firebase_info = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(firebase_info)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase_url"]
        })
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ Firebase ไม่ได้: {e}")

# --- 4. แสดงโลโก้ใน SIDEBAR ---
with st.sidebar:
    logo_data = get_base64_image("logo1.png")
    if logo_data:
        st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="neon-logo">', unsafe_allow_html=True)
    else:
        st.write("🛰️ [ ไม่พบไฟล์ logo1.png ]")
    
    st.markdown("<h2 style='text-align: center; color: #00FF00;'>SYNAPSE</h2>", unsafe_allow_html=True)
    st.session_state.user = st.text_input("รหัส AGENT", value="Bas_Admin")
    st.markdown("---")
    st.caption("สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว")

# --- 5. ฟังก์ชันหลัก ROOM RADAR ---
def room_radar():
    st.subheader("🛰️ ระบบเรดาร์ตรวจจับสัญญาณ AGENT")
    
    # ดึงพิกัดปัจจุบัน
    loc = get_geolocation()
    if loc and 'coords' in loc:
        my_lat = loc['coords']['latitude']
        my_lon = loc['coords']['longitude']
    else:
        my_lat, my_lon = 13.7367, 100.5231 # พิกัดสำรอง (กทม.)
        st.info("📡 กำลังค้นหาพิกัดจริงจากดาวเทียม...")

    # สร้างแผนที่ Google Maps Hybrid (สว่างและเห็นชื่อสถานที่ชัดเจน)
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=15, 
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
        attr='Google Maps Hybrid'
    )
    
    # วงแหวนเรดาร์สีนีออน
    radar_color = "#00FFFF"
    for radius in [1000, 3000]:
        folium.Circle(
            radius=radius,
            location=[my_lat, my_lon],
            color=radar_color,
            fill=True,
            fill_opacity=0.05,
            weight=1,
            dash_array='5, 5'
        ).add_to(m)

    # หมุดของตัวเอง
    folium.Marker(
        [my_lat, my_lon], 
        tooltip="ตำแหน่งของคุณ",
        icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
    ).add_to(m)

    # ดึงพิกัด AGENT อื่นๆ จาก Firebase
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user:
                    u_lat, u_lon = data.get('lat'), data.get('lon')
                    if u_lat and u_lon:
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        folium.Marker(
                            [u_lat, u_lon], 
                            popup=f"AGENT: {uid}<br>ห่างจากคุณ: {dist:.2f} กม.",
                            icon=folium.Icon(color='green', icon='user', prefix='fa')
                        ).add_to(m)
                        # เส้นเชื่อมสัญญาณ
                        folium.PolyLine([[my_lat, my_lon], [u_lat, u_lon]], color="#00FF00", weight=1, opacity=0.3).add_to(m)
    except Exception as e:
        st.error(f"เรดาร์ขัดข้อง: {e}")

    # แสดงผลแผนที่
    st_folium(m, width="100%", height=500)

    # ปุ่มอัปเดตพิกัดเข้า Firebase
    if st.button("🛰️ กระจายสัญญาณพิกัดสด (LIVE UPDATE)", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.success("อัปเดตพิกัดเข้าฐานข้อมูลแล้ว!")

# รันระบบ
if __name__ == "__main__":
    room_radar()

import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64

# --- 1. ตั้งค่าหน้าจอ (ต้องอยู่บรรทัดแรกสุดของโค้ด) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

# --- 2. CSS สำหรับซ่อน UI และทำโลโก้นีออนเต้น (ใส่ไว้ตรงนี้จะคุมทั้งแอป) ---
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
        max-width: 180px;
        display: block;
        margin: 0 auto;
        animation: neon-glow 2s infinite ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ฟังก์ชันดึงภาพโลโก้ ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# --- 4. แสดงโลโก้ใน SIDEBAR (ส่วนนี้จะแสดงทุกหน้า) ---
with st.sidebar:
    logo_data = get_base64_image("logo1.png")
    if logo_data:
        st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="neon-logo">', unsafe_allow_html=True)
    else:
        st.write("🛰️ [ LOGO ]")
    
    st.markdown("<h2 style='text-align: center; color: #00FF00;'>SYNAPSE</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # เมนูเลือกหน้า (ถ้าเพื่อนมีหลายหน้า)
    menu = st.radio("เมนูหลัก", ["เรดาร์ตรวจจับ", "ตั้งค่าระบบ"])
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว")

# --- 5. เชื่อมต่อ FIREBASE ---
if not firebase_admin._apps:
    try:
        firebase_info = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(firebase_info)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase_url"]
        })
    except:
        pass

# --- 6. ฟังก์ชันคำนวณระยะทาง ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) * R

# --- 7. หน้าจอหลัก (เปลี่ยนตามเมนูที่เลือก) ---
if menu == "เรดาร์ตรวจจับ":
    st.subheader("🛰️ ระบบเรดาร์ตรวจจับ AGENT")
    
    loc = get_geolocation()
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    else:
        my_lat, my_lon = 13.7367, 100.5231
        st.info("📡 กำลังรอพิกัดจริง...")

    # แผนที่ Google Maps Hybrid สว่างชัดเจน
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, 
                   tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google')
    
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')).add_to(m)

    # แสดงผลแผนที่
    st_folium(m, width="100%", height=500)

elif menu == "ตั้งค่าระบบ":
    st.subheader("⚙️ การตั้งค่าอุปกรณ์")
    st.write("จัดการข้อมูล AGENT และการเชื่อมต่อดาวเทียม")

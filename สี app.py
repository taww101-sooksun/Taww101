import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64

# --- 1. ตั้งค่าพื้นฐาน (ต้องอยู่บนสุด) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

# CSS สำหรับซ่อน UI และสร้างเอฟเฟกต์นีออนเต้นให้โลโก้
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

# --- 2. ฟังก์ชันจัดการรูปภาพโลโก้ ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# --- 3. แสดงโลโก้ถาวรใน Sidebar (จะปรากฏทุกหน้า) ---
with st.sidebar:
    logo_data = get_base64_image("logo1.png")
    if logo_data:
        st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="neon-logo">', unsafe_allow_html=True)
    else:
        st.warning("⚠️ ไม่พบไฟล์ logo1.png")
    
    st.markdown("<h2 style='text-align: center; color: #00FF00;'>SYNAPSE</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("เมนูระบบ", ["📡 เรดาร์ตรวจจับ", "⚙️ ตั้งค่า AGENT"])
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Command Center")

# --- 4. เชื่อมต่อ Firebase (ดึงจาก Secrets) ---
if not firebase_admin._apps:
    try:
        firebase_info = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(firebase_info)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_url"]})
    except:
        pass

# --- 5. ฟังก์ชันคำนวณพิกัด ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) * R

# --- 6. ส่วนการทำงานหลัก ---
if menu == "📡 เรดาร์ตรวจจับ":
    st.subheader("🛰️ ระบบเรดาร์ตรวจจับ AGENT")
    
    # ดึงตำแหน่ง (ถ้าตำแหน่งไม่ตรง ให้เช็คสิทธิ์ GPS ใน Chrome)
    loc = get_geolocation()
    
    if loc and 'coords' in loc:
        my_lat = loc['coords']['latitude']
        my_lon = loc['coords']['longitude']
        st.success(f"📍 ล็อกพิกัดสำเร็จ: {my_lat:.5f}, {my_lon:.5f}")
    else:
        # พิกัดบ้านนาโพธิ์ (อ้างอิงจากรูป 1000015090.jpg)
        my_lat, my_lon = 15.6558, 104.2185 
        st.info("📡 กำลังรอสัญญาณดาวเทียม... (แสดงพิกัดฐานทัพชั่วคราว)")

    # ใช้ Google Maps Hybrid เพื่อความแม่นยำของสถานที่
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=17, 
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
        attr='Google Maps'
    )
    
    # หมุดปัจจุบัน
    folium.Marker(
        [my_lat, my_lon], 
        tooltip="ตำแหน่งของคุณ",
        icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
    ).add_to(m)

    st_folium(m, width="100%", height=500)

    if st.button("🛰️ อัปเดตและกระจายสัญญาณสด", use_container_width=True):
        db.reference(f'users/Bas_Admin').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.toast("ส่งพิกัดเข้าดาวเทียมแล้ว!")

elif menu == "⚙️ ตั้งค่า AGENT":
    st.subheader("⚙️ การตั้งค่าระบบ")
    st.write("จัดการรหัสสัญญาณและสีธีมนีออน")

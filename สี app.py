import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0e1117; }
    
    @keyframes neon-glow {
        0% { filter: drop-shadow(0 0 5px #00FF00) drop-shadow(0 0 10px #00FF00); }
        50% { filter: drop-shadow(0 0 15px #00FF00) drop-shadow(0 0 25px #00FF00); }
        100% { filter: drop-shadow(0 0 5px #00FF00) drop-shadow(0 0 10px #00FF00); }
    }
    .neon-logo-main {
        width: 150px;
        display: block;
        margin: 0 auto 20px auto;
        animation: neon-glow 2s infinite ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

# --- 2. แสดงโลโก้ที่ "หน้าหลัก" (เพื่อให้เห็นทันที) ---
logo_data = get_base64_image("logo1.png")
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="neon-logo-main">', unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>SYNAPSE</h1>", unsafe_allow_html=True)

# --- 3. การดึงพิกัดแบบแม่นยำสูง (High Accuracy) ---
# เพิ่มความพยายามในการดึงพิกัดให้แม่นที่สุด
loc = get_geolocation() 

if loc and 'coords' in loc:
    my_lat = loc['coords']['latitude']
    my_lon = loc['coords']['longitude']
    accuracy = loc['coords'].get('accuracy', 'N/A')
    st.success(f"📍 ล็อกพิกัดแม่นยำสำเร็จ: {my_lat:.6f}, {my_lon:.6f} (รัศมีคลาดเคลื่อน: {accuracy} เมตร)")
else:
    # พิกัดฐานทัพที่คุณอยู่ (นาโพธิ์) อ้างอิงจากรูปภาพ
    my_lat, my_lon = 15.65872, 103.57858
    st.warning("📡 กำลังปรับจูนสัญญาณ GPS... กรุณารอสักครู่หรือเดินไปที่โล่งแจ้ง")

# --- 4. แผนที่ Google Hybrid ---
m = folium.Map(
    location=[my_lat, my_lon], 
    zoom_start=18, # ซูมเข้าไปให้เห็นหลังคาบ้านชัดๆ
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
    attr='Google Maps'
)

folium.Marker(
    [my_lat, my_lon], 
    icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
).add_to(m)

st_folium(m, width="100%", height=500)

if st.button("🛰️ บันทึกและส่งพิกัดปัจจุบัน", use_container_width=True):
    try:
        db.reference(f'users/Bas_Admin').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.toast("ส่งพิกัดเข้าดาวเทียมแล้ว!")
    except: st.error("Firebase Connection Error")

import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import json

# --- 1. เชื่อมต่อ Firebase (ดึงจาก st.secrets) ---
if not firebase_admin._apps:
    # ดึงข้อมูล JSON จาก Secrets ของ Streamlit
    # สมมติว่าคุณเก็บไว้ในชื่อ "firebase_service_account"
    firebase_info = dict(st.secrets["firebase_service_account"])
    
    cred = credentials.Certificate(firebase_info)
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["firebase_url"] # เก็บ URL แยกไว้ใน Secrets ด้วย
    })

# --- 2. ฟังก์ชันคำนวณระยะทาง ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) * R

# --- 3. ตั้งค่า UI และซ่อน Branding ---
st.set_page_config(page_title="SYNAPSE RADAR", layout="wide")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;} .stApp {background-color: #0e1117;}</style>", unsafe_allow_html=True)

# กำหนดตัวตนผู้ใช้ (จากข้อมูลส่วนตัวของคุณ)
if 'user' not in st.session_state:
    st.session_state.user = "Bas_Admin" # หรือ "Ta" ตามที่คุณสะดวก
st.session_state.theme_color = "#00FF00"

# --- 4. ฟังก์ชัน ROOM RADAR (ตัวที่คุณส่งมา) ---
def room_radar():
    st.subheader("🛰️ ระบบเรดาร์ตรวจจับสัญญาณ AGENT")
    
    loc = get_geolocation()
    if loc and 'coords' in loc:
        my_lat = loc['coords']['latitude']
        my_lon = loc['coords']['longitude']
        st.session_state.my_pos = (my_lat, my_lon)
    else:
        my_lat, my_lon = 13.7367, 100.5231
        st.info("📡 กำลังรอพิกัดจริงจากดาวเทียม...")

    m = folium.Map(location=[my_lat, my_lon], zoom_start=14, tiles="CartoDB dark_matter")
    
    folium.Marker([my_lat, my_lon], tooltip="คุณ (ORIGIN)",
                  icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')).add_to(m)

    for radius in [1000, 3000, 5000]:
        folium.Circle(radius=radius, location=[my_lat, my_lon], color=st.session_state.theme_color,
                      fill=False, dash_array='10, 10', opacity=0.3).add_to(m)

    # ดึงข้อมูล AGENT อื่นๆ จาก Firebase Realtime Database
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user:
                    u_lat, u_lon = data.get('lat'), data.get('lon')
                    if u_lat and u_lon:
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        folium.Marker([u_lat, u_lon], popup=f"AGENT: {uid}<br>ระยะ: {dist:.2f} กม.",
                                      icon=folium.Icon(color='green', icon='signal', prefix='fa')).add_to(m)
                        folium.PolyLine(locations=[[my_lat, my_lon], [u_lat, u_lon]], 
                                        color=st.session_state.theme_color, weight=1, opacity=0.4, dash_array='5, 5').add_to(m)
    except Exception as e:
        st.error(f"📡 เรดาร์ขัดข้อง: {e}")

    st_folium(m, width="100%", height=500)

    if st.button("🛰️ กระจายสัญญาณพิกัดสด (LIVE UPDATE)", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.success(f"อัปเดตพิกัดเข้าฐานข้อมูลเรียบร้อย!")

# รันระบบ
room_radar()
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE COMMAND CENTER")

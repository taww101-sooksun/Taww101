import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import json
import streamlit as st

# --- 1. CSS สำหรับสร้างขอบนีออนเต้น (Neon Glow Animation) ---
st.markdown("""
    <style>
    /* สร้างการเคลื่อนไหวของแสงนีออน */
    @keyframes neon-glow {
        0% { filter: drop-shadow(0 0 5px #00FF00) drop-shadow(0 0 10px #00FF00); }
        50% { filter: drop-shadow(0 0 15px #00FF00) drop-shadow(0 0 25px #00FF00); }
        100% { filter: drop-shadow(0 0 5px #00FF00) drop-shadow(0 0 10px #00FF00); }
    }

    /* สไตล์สำหรับโลโก้ */
    .neon-logo {
        width: 100%;
        max-width: 250px;
        display: block;
        margin-left: auto;
        margin-right: auto;
        animation: neon-glow 2s infinite ease-in-out; /* สั่งให้เต้นตลอดเวลา */
        border-radius: 15px; /* ปรับขอบให้โค้งมนถ้าต้องการ */
    }

    /* ซ่อนส่วนประกอบ Streamlit ตามที่เพื่อนเคยขอ */
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ส่วนการดึงโลโก้มาแสดงใน Sidebar ---
with st.sidebar:
    try:
        # ใช้ HTML แทน st.image เพื่อให้ใส่ Class CSS ได้
        import base64
        
        def get_base64_image(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()

        # แปลงไฟล์ภาพเป็น base64 เพื่อให้ CSS จัดการได้ง่ายขึ้น
        logo_base64 = get_base64_image("logo1.png")
        st.markdown(
            f'<img src="data:image/png;base64,{logo_base64}" class="neon-logo">',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error("ไม่พบไฟล์ logo1.png ในระบบ")
    
    st.markdown("<br><h3 style='text-align: center; color: #00FF00;'>SYNAPSE COMMAND</h3>", unsafe_allow_html=True)
    st.markdown("---")

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

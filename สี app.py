import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time

# --- 1. SETTING & STYLE (Rainbow Background) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide", page_icon="🛰️")

# ใส่ CSS สำหรับพื้นหลังสีรุ้งวิ่งตามที่คุณต้องการ
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: rainbow 15s ease infinite;
    }}
    @keyframes rainbow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}
    /* ทำให้เนื้อหาด้านบนดูง่ายขึ้น */
    .stTabs, .stMarkdown, .stTextInput, .stButton {{
        background: rgba(0, 0, 0, 0.7);
        padding: 15px;
        border-radius: 15px;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        # ใช้ค่าจาก secrets หรือถ้ามีไฟล์ google-services.json ก็เปลี่ยนเป็น credentials.Certificate("google-services.json")
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"กรุณาตั้งค่า Firebase ใน Secrets: {e}")

# --- 3. HEADER & LOGO ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo3.jpg", width=120)
    except:
        st.subheader("🛰️ LOGO")
with col2:
    st.title("🛰️ SYNAPSE COMMAND CENTER")
    st.write("### *'อยู่นิ่งๆ ไม่เจ็บตัว'* | BY Ta101")

# --- 4. MUSIC PLAYER ---
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

# --- 5. CORE SYSTEM ---
loc = get_geolocation()
tabs = st.tabs(["🚀 CORE & CONTROL", "🛰️ RADAR MAP", "📞 TELE-CALL"])

with tabs[0]:
    my_id = st.text_input("ระบุชื่อรหัสของคุณ (ID):", value="Ta101")
    
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"📍 ตรวจพบตำแหน่งปัจจุบัน: {lat}, {lon}")
        
        if st.button("🛰️ LOGIN & UPDATE POSITION"):
            db.reference(f'users/{my_id}').update({
                'lat': lat, 
                'lon': lon, 
                'status': 'online',
                'last_update': time.time()
            })
            st.toast(f"สวัสดี {my_id}, พิกัดอัปเดตแล้ว!", icon="✅")
            st.balloons()
    else:
        st.warning("🚨 กรุณากด 'อนุญาต' (Allow) ให้เข้าถึงพิกัด GPS บนเบราว์เซอร์")

with tabs[1]:
    all_users = db.reference('users').get()
    
    # กำหนดจุดศูนย์กลางแผนที่
    v_lat, v_lon = (13.75, 100.5)
    if all_users and my_id in all_users:
        v_lat = all_users[my_id].get('lat', 13.75)
        v_lon = all_users[my_id].get('lon', 100.5)

    m = folium.Map(location=[v_lat, v_lon], zoom_start=16, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for name, info in all_users.items():
            if 'lat' in info and 'lon' in info:
                # 💡 หมุดเปลี่ยนสีตามสถานะจริง
                current_time = time.time()
                last_active = info.get('last_update', 0)
                
                if name == my_id:
                    icon_color = 'green'  # ตัวเราสีเขียว
                elif (current_time - last_active) < 300: # ออนไลน์ไม่เกิน 5 นาที
                    icon_color = 'blue'   # เพื่อนออนไลน์สีฟ้า
                else:
                    icon_color = 'red'    # ออฟไลน์สีแดง
                
                folium.Marker(
                    [info['lat'], info['lon']], 
                    tooltip=f"{name} ({'Online' if icon_color != 'red' else 'Offline'})",
                    icon=folium.Icon(color=icon_color, icon='star')
                ).add_to(m)
        
    st_folium(m, width="100%", height=600)

with tabs[2]:
    st.subheader("📞 SYNAPSE QUICK-CALL")
    st.info("ใช้ Whereby แทน Jitsi เพื่อความเสถียรบนมือถือที่มากกว่า")

    room_id = st.text_input("ชื่อห้องสนทนา:", value=f"synapse-{my_id}")
    whereby_url = f"https://whereby.com/{room_id}" 
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write("ส่งลิงก์นี้ให้เพื่อน:")
        st.code(whereby_url)
    with col_c2:
        if st.button("🚀 เปิดผ่าน Google Meet (สำรอง)"):
            st.markdown(f'<a href="https://meet.google.com/new" target="_blank">สร้างห้องสำรองที่นี่</a>', unsafe_allow_html=True)

    # ฝังหน้าจอโทร
    st.markdown(f"""
        <iframe 
            src="{whereby_url}?embed&vpa=1&chat=1" 
            width="100%" 
            height="600" 
            allow="camera; microphone; fullscreen; display-capture">
        </iframe>
    """, unsafe_allow_html=True)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time

# --- 1. SETTING & STYLE (พื้นหลังสีรุ้งวิ่ง) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide", page_icon="🛰️")

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
    /* กล่องเนื้อหาให้อ่านง่ายขึ้น */
    .stTabs, .stMarkdown, .stTextInput, .stButton {{
        background: rgba(0, 0, 0, 0.8);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(0, 255, 0, 0.4);
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"⚠️ กรุณาตั้งค่า Firebase Secrets: {e}")

# --- 3. HEADER & LOGO ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo3.jpg", width=400)
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
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "📞 TELE-CALL"])

with tabs[0]:
    my_id = st.text_input("ระบุชื่อรหัสของคุณ (ID):", value="Ta101")
    
    # ✅ แก้ไขจุด KeyError: เช็คค่า loc ก่อนดึงพิกัด
    if loc is not None and 'coords' in loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"📍 ตรวจพบตำแหน่งปัจจุบัน: {lat}, {lon}")
        
        if st.button("🛰️ บันทึกตำแหน่งเข้าดาวเทียม"):
            db.reference(f'users/{my_id}').update({
                'lat': lat, 
                'lon': lon, 
                'last_update': time.time()
            })
            st.toast(f"บันทึกพิกัด {my_id} สำเร็จ!", icon="✅")
            st.balloons()
    else:
        st.warning("🛰️ กำลังรอสัญญาณ GPS... กรุณากด 'Allow' (อนุญาต) บนเบราว์เซอร์")
        if st.button("🔄 รีเฟรชสัญญาณพิกัด"):
            st.rerun()

with tabs[1]:
    all_users = db.reference('users').get()
    
    # กำหนดจุดศูนย์กลางแผนที่ (ถ้าไม่มีพิกัดเราให้ไปกรุงเทพฯ ก่อน)
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
                # 🔵 ตัวคุณ = สีเขียว | ออนไลน์ (ไม่เกิน 5 นาที) = สีฟ้า | ออฟไลน์ = สีแดง
                is_online = (time.time() - info.get('last_update', 0)) < 300
                icon_color = 'green' if name == my_id else ('blue' if is_online else 'red')
                
                folium.Marker(
                    [info['lat'], info['lon']], 
                    tooltip=f"{name} ({'Online' if is_online else 'Offline'})",
                    icon=folium.Icon(color=icon_color, icon='star')
                ).add_to(m)
        
    st_folium(m, width="100%", height=600)

with tabs[2]:
    st.subheader("📞 SYNAPSE DIRECT CALL")
    # ลิงก์ห้องที่คุณสมัครไว้
    whereby_url = "https://ta-sooksun.whereby.com/ta0b9934f8-ae2a-4e0f-b513-58a0616fd29a"
    
    # ฝัง Iframe ห้องคุย
    st.markdown(f"""
        <iframe 
            src="{whereby_url}?embed&vpa=1&chat=1" 
            allow="camera; microphone; fullscreen; speaker; display-capture; compute-pressure" 
            style="height: 700px; width: 100%; border: 3px solid #00ff00; border-radius: 15px;">
        </iframe>
    """, unsafe_allow_html=True)

import streamlit as st
import os 
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib
import pytz  # ต้องใช้สำหรับตั้งค่าโซนเวลาประเทศไทย

# ==========================================
# 1. ระบบจัดการเวลา (Thailand Timezone)
# ==========================================
def get_thai_time():
    # บังคับให้เป็นโซนเวลาเอเชีย/กรุงเทพฯ
    thai_tz = pytz.timezone('Asia/Bangkok')
    return datetime.now(thai_tz)

def init_system():
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 2. เรดาร์ระบุตำแหน่ง (แก้ปัญหาเวลาไม่ตรง)
# ==========================================
def room_gps():
    st.subheader("🛰️ เรดาร์ระบุตำแหน่ง")
    
    # ดึงเวลาไทยปัจจุบัน
    now = get_thai_time()
    current_time_str = now.strftime("%H:%M:%S")
    current_date_str = now.strftime("%d/%m/%Y")

    # แสดงผลเวลาไทยตัวใหญ่ๆ ให้ตรวจสอบได้
    st.markdown(f"### 🕒 Server Time (ไทย): `{current_time_str}`")
    st.caption(f"วันที่ปัจจุบัน: {current_date_str}")

    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        accuracy = loc['coords'].get('accuracy', 0)
        
        # บันทึกลง Firebase พร้อมเวลาที่ถูกต้อง
        db.reference(f'locations/{st.session_state.user}').update({
            'lat': lat, 'lon': lon, 
            'update_time': current_time_str,
            'timestamp': time.time()
        })

        col1, col2 = st.columns(2)
        col1.metric("Latitude", f"{lat:.6f}")
        col2.metric("Longitude", f"{lon:.6f}")
        st.write(f"🎯 ความแม่นยำ: {accuracy:.2f} เมตร")

        # แผนที่แบบที่คุณท่านต้องการ
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker(
            [lat, lon], 
            popup=f"พิกัด ณ เวลา {current_time_str}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        st_folium(m, width=700, height=400)
    else:
        st.warning("⌛ กำลังค้นหาตำแหน่ง... (กรุณาเปิด GPS และกด Allow)")

# ==========================================
# 3. ส่วนการสื่อสารและมัลติมีเดีย (คงเดิม)
# ==========================================
def room_comms():
    st.subheader("💬 สื่อสาร")
    # ... (โค้ดส่วนแชทและวิดีโอคอลเดิมของคุณท่าน) ...
    st.info("ระบบแชทและวิดีโอคอลพร้อมใช้งาน")

def room_music():
    st.subheader("🎧 เพลง")
    # ... (โค้ดส่วนเครื่องเล่นเพลงเดิมของคุณท่าน) ...
    st.info("ระบบมัลติมีเดียพร้อมใช้งาน")

# ==========================================
# 4. หน้าจอหลักและการรวมธีม
# ==========================================
def main():
    init_system()
    
    # ธีมและการตกแต่ง
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #FFFFFF; }
        .stMetric { background-color: #111111; padding: 10px; border-radius: 10px; border: 1px solid #333; }
        </style>
    """, unsafe_allow_html=True)

    if not st.session_state.auth_status:
        st.title("🛡️ SYNAPSE LOGIN")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ENTER"):
            acc = db.reference(f'accounts/{u}').get()
            if acc and acc.get('pw') == hash_pw(p):
                st.session_state.auth_status, st.session_state.user = True, u
                st.rerun()
        return

    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 User: **{st.session_state.user}**")
        if st.button("🚪 LOGOUT"): st.session_state.auth_status = False; st.rerun()

    menu = {"🛰️ เรดาร์": room_gps, "💬 สื่อสาร": room_comms, "🎧 เพลง": room_music}
    tabs = st.tabs(list(menu.keys()))
    for i, func in enumerate(menu.values()):
        with tabs[i]: func()

if __name__ == "__main__":
    main()

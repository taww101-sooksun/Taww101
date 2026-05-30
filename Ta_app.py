import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import time
import json

# 1. ตั้งค่าหน้าจอและระบบสีพื้นหลัง (Theme Selector)
st.set_page_config(page_title="SYNAPSE CLEAR", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 

with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    picked_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    st.session_state.theme_color = picked_color
    st.write(f"สีปัจจุบัน: {picked_color}")
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# ใช้ CSS ปรับแต่งตามสีนีออนที่เลือก
st.markdown(f"""
    <style>
    .stApp {{ 
        background: #000 !important; 
        color: {st.session_state.theme_color} !important; 
    }}
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background-color: transparent !important;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. เชื่อมต่อ FIREBASE
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Firebase ได้: {e}")

st.title("🛰️ SYNAPSE COMMAND CENTER")

# 3. บังคับเล่นเพลง (ยักษ์ในตัวฉัน)
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR"])

with tabs[0]:
    my_id = st.text_input("ระบุชื่อรหัสของคุณ:", value="Ta101")
    
    st.markdown("### 📍 ระบบดึงพิกัดดาวเทียม (Real-Time)")
    st.write("กดปุ่มด้านล่างเพื่อสั่งให้มือถือค้นหาตำแหน่งพิกัดที่แท้จริงของคุณ")

    # ใช้ระบบ HTML5 / JavaScript ฝั่งหน้าบ้านดึงพิกัด (หมดปัญหาค้าง, หมดปัญหา None)
    # มันจะยิงข้อมูลกลับมาฝั่ง Streamlit ผ่านฟังก์ชัน st.components
    js_gps_html = f"""
    <div style="text-align: center;">
        <button onclick="getLocation()" style="
            background-color: transparent; 
            color: {st.session_state.theme_color}; 
            border: 2px solid {st.session_state.theme_color}; 
            padding: 15px 32px; 
            font-size: 16px; 
            cursor: pointer; 
            border-radius: 8px;
            font-weight: bold;
            width: 100%;
            box-shadow: 0 0 10px {st.session_state.theme_color};
        ">📡 กดปุ่มนี้เพื่อแชร์พิกัดปัจจุบันจริง</button>
        <p id="status" style="margin-top: 10px; color: #fff; font-size: 14px;">สถานะ: รอการกดปุ่ม...</p>
    </div>

    <script>
    function getLocation() {{
        const status = document.getElementById('status');
        if (!navigator.geolocation) {{
            status.innerHTML = '❌ เบราว์เซอร์ของคุณไม่รองรับระบบ GPS';
            return;
        }}
        
        status.innerHTML = '⚡ กำลังค้นหาสัญญาณดาวเทียม...';
        
        navigator.geolocation.getCurrentPosition(
            (position) => {{
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                status.innerHTML = '✅ เจอพิกัดแล้ว! กำลังส่งเข้าดาวเทียมหลัก...';
                
                // ส่งพิกัดกลับไปให้ Python ทันทีผ่าน URL query parameters เพื่อความชัวร์
                const currentUrl = new URL(window.parent.location.href);
                currentUrl.searchParams.set('lat

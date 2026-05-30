import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import time
import os

# บังคับระบบไม่ให้วิ่งไปหา Google Metadata Server (แก้บั๊ก Connection timed out)
os.environ["g_metadata_server"] = "none"
os.environ["GOOGLE_CLOUD_DISABLE_GRPC"] = "true"

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

# 2. เชื่อมต่อ FIREBASE (แบบกำหนดตัวเลือกปิดดักจับ Metadata)
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        
        # เชื่อมต่อฐานข้อมูลโดยตรง
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Firebase ได้: {e}")

st.title("🛰️ SYNAPSE COMMAND CENTER")

# 3. บังคับเล่นเพลง
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR"])

with tabs[0]:
    my_id = st.text_input("ระบุชื่อรหัสของคุณ:", value="Ta101")
    
    st.markdown("### 📍 ระบบดึงพิกัดดาวเทียม (Real-Time)")
    st.write("กดปุ่มด้านล่างเพื่อสั่งให้มือถือค้นหาตำแหน่งพิกัดที่แท้จริงของคุณ")

    js_gps_html = """
    <div style="text-align: center;">
        <button onclick="getLocation()" style="
            background-color: transparent; 
            color: NEON_COLOR; 
            border: 2px solid NEON_COLOR; 
            padding: 15px 32px; 
            font-size: 16px; 
            cursor: pointer; 
            border-radius: 8px;
            font-weight: bold;
            width: 100%;
            box-shadow: 0 0 10px NEON_COLOR;
        ">📡 กดปุ่มนี้เพื่อแชร์พิกัดปัจจุบันจริง</button>
        <p id="status" style="margin-top: 10px; color: #fff; font-size: 14px;">สถานะ: รอการกดปุ่ม...</p>
    </div>

    <script>
    function getLocation() {
        const status = document.getElementById('status');
        if (!navigator.geolocation) {
            status.innerHTML = '❌ เบราว์เซอร์ของคุณไม่รองรับระบบ GPS';
            return;
        }
        
        status.innerHTML = '⚡ กำลังค้นหาสัญญาณดาวเทียม...';
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                status.innerHTML = '✅ เจอพิกัดแล้ว! กำลังส่งเข้าดาวเทียมหลัก...';
                
                const currentUrl = new URL(window.parent.location.href);
                currentUrl.searchParams.set('lat', lat);
                currentUrl.searchParams.set('lon', lon);
                window.parent.location.href = currentUrl.toString();
            },
            (error) => {
                if(error.code == 1) {
                    status.innerHTML = '❌ กรุณากด "อนุญาต" สิทธิ์ GPS บนมือถือของคุณด้วยครับ';
                } else {
                    status.innerHTML = '❌ สัญญาณดาวเทียมขัดข้อง ลองเปิด GPS ในเครื่องดูครับ';
                }
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }
    </script>
    """.replace("NEON_COLOR", st.session_state.theme_color)

    st.components.v1.html(js_gps_html, height=120)

    query_params = st.query_params
    
    if "lat" in query_params and "lon" in query_params:
        lat = float(query_params["lat"])
        lon = float(query_params["lon"])
        
        st.success(f"🎯 สัญญาณดาวเทียมล็อกเป้าสำเร็จ: {lat}, {lon}")
        
        try:
            db.reference(f'users/{my_id}').update({
                'lat': lat, 'lon': lon, 'last_update': time.time()
            })
            st.toast("🛰️ อัปเดตพิกัดลงฐานข้อมูลสำเร็จ!", icon="🚀")
        except Exception as e:
            st.error(f"ส่งพิกัดเข้าเซิร์ฟเวอร์ไม่สำเร็จ: {e}")
            
        if st.button("🔄 ล้างค่าพิกัดเก่าเพื่อจับสัญญาณใหม่"):
            st.query_params.clear()
            st.rerun()

with tabs[1]:
    all_users = None
    try:
        all_users = db.reference('users').get()
    except Exception as e:
        pass # ถ้าบั๊กดึงไม่ได้ ให้ปล่อยข้ามไปเงียบๆ ไม่ให้ตัวหนังสือสีแดงกวนใจ
    
    view_lat, view_lon = 13.75, 100.5 
    
    if all_users and my_id in all_users:
        if isinstance(all_users[my_id], dict):
            view_lat = all_users[my_id].get('lat', 13.75)
            view_lon = all_users[my_id].get('lon', 100.5)

    m = folium.Map(
        location=[view_lat, view_lon], 
        zoom_start=15, 
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
        attr="Google Satellite"
    )

    if all_users:
        for name, info in all_users.items():
            if isinstance(info, dict) and 'lat' in info and 'lon' in info:
                color = 'blue' if name == my_id else 'red'
                folium.Marker(
                    location=[info['lat'], info['lon']], 
                    tooltip=name,
                    icon=folium.Icon(color=color, icon='star')
                ).add_to(m)
                
    st_folium(m, width="100%", height=500)

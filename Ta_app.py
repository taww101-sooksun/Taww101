import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time

# 1. ⚡ ตั้งค่าหน้าจอและระบบสีพื้นหลัง (Theme Selector)
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

# วิธีแก้ SyntaxError: ต้องใช้ปีกกาซ้อน 2 ชั้น {{ }} เมื่อต้องการเขียน CSS ใน f-string ของ Python
st.markdown(f"""
    <style>
    .stApp {{ 
        background: #000 !important; 
        color: {st.session_state.theme_color} !important; 
    }}
    .chat-box {{ 
        border: 1px solid {st.session_state.theme_color}; 
        padding: 10px; 
        border-radius: 10px; 
        margin-bottom: 5px;
        background: rgba(255,255,255,0.05);
    }}
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background-color: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. 🛰️ เชื่อมต่อ FIREBASE (ดึงค่าความปลอดภัยจาก Secrets)
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

# 3. 🎵 บังคับเล่นเพลง (ยักษ์ในตัวฉัน)
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

# 4. 🚀 ระบบดึงพิกัดจริงจากเบราว์เซอร์ผู้ใช้งาน
loc = get_geolocation()

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR"])

with tabs[0]:
    my_id = st.text_input("ระบุชื่อรหัสของคุณ:", value="Ta101")
    if loc and 'coords' in loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"📍 ตรวจพบตำแหน่งจริงของคุณ: {lat}, {lon}")
        
        if st.button("🛰️ บันทึกพิกัดจริงลงระบบ"):
            try:
                db.reference(f'users/{my_id}').update({
                    'lat': lat, 'lon': lon, 'last_update': time.time()
                })
                st.balloons()
                st.success("บันทึกพิกัดเข้า Firebase เรียบร้อยแล้วเพื่อน!")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดขณะส่งข้อมูล: {e}")
    else:
        st.warning("🚨 ระบบกำลังรอตำแหน่ง... กรุณากด 'อนุญาต' (Allow) การเข้าถึงตำแหน่งบนเบราว์เซอร์ด้วยนะ")

with tabs[1]:
    all_users = None
    try:
        all_users = db.reference('users').get()
    except Exception as e:
        st.error(f"ดึงข้อมูลจากด่านดาวเทียมไม่สำเร็จ: {e}")
    
    # ดึงพิกัดของเรามาตั้งค่าจุดกึ่งกลางแผนที่ ถ้าหาไม่เจอให้ไปจุดตั้งต้น (กรุงเทพฯ)
    view_lat, view_lon = 13.75, 100.5 
    if all_users and my_id in all_users:
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
                # 🔵 ตัวคุณสีน้ำเงิน | 🔴 คนอื่นสีแดง
                color = 'blue' if name == my_id else 'red'
                folium.Marker(
                    [info['lat'], info['lon']], 
                    tooltip=name,
                    icon=folium.Icon(color=color, icon='star')
                ).add_to(m)
                
        st_folium(m, width="100%", height=500)

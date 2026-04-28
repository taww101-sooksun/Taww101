import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time

# --- 1. SET UP & THEME (รวมไว้จุดเดียว) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 

with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    picked_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    st.session_state.theme_color = picked_color
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# ฉีด CSS ปรับแต่ง UI
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background-color: transparent !important;
        width: 100%;
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
        st.error(f"Firebase Error: {e}")

st.title("🛰️ SYNAPSE COMMAND CENTER")

# --- 3. MUSIC SYSTEM ---
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

# --- 4. GEOLOCATION & TABS ---
loc = get_geolocation()
if loc:
    accuracy = loc['coords'].get('accuracy', 'N/A')
    st.write(f"ความคลาดเคลื่อน: {accuracy} เมตร")
    
    if accuracy > 100:
        st.warning("⚠️ สัญญาณ GPS ไม่แม่นยำ (อาจเคลื่อนได้เป็นกิโล) ลองออกไปที่โล่งครับ")


with tabs[0]:
    my_id = st.text_input("ระบุชื่อรหัสของคุณ:", value="Ta101")
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"📍 พิกัดปัจจุบัน: {lat}, {lon}")
        
        if st.button("🛰️ อัปเดตพิกัดลงฐานข้อมูล"):
            db.reference(f'users/{my_id}').update({
                'lat': lat, 
                'lon': lon, 
                'last_update': time.time()
            })
            st.toast("บันทึกพิกัดแล้ว!", icon="✅")
    else:
        st.info("⌛ กำลังรอสัญญาณ GPS... (กรุณากด Allow Location บนเบราว์เซอร์)")

with tabs[1]:
    all_users = db.reference('users').get()
    
    if loc: # เช็กก่อนว่ามีพิกัดเราจริงๆ ไหม
        my_lat = loc['coords']['latitude']
        my_lon = loc['coords']['longitude']
        
        st.write(f"ตำแหน่งของคุณตอนนี้: {my_lat}, {my_lon}")

        m = folium.Map(location=[my_lat, my_lon], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                       attr="Google Satellite")

        # วาด Marker คนอื่นๆ
        if all_users:
            for name, info in all_users.items():
                if isinstance(info, dict) and 'lat' in info and 'lon' in info:
                    color = 'blue' if name == my_id else 'red'
                    folium.Marker([info['lat'], info['lon']], tooltip=name).add_to(m)
        
        st_folium(m, width="100%", height=500)
    else:
        st.warning("⚠️ แผนที่ยังไม่พร้อม เพราะระบบยังหาพิกัด GPS ของคุณไม่เจอครับ")

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
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR"])

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
    try:
        all_users = db.reference('users').get()
        
        # จุดศูนย์กลางแผนที่ (ถ้าไม่มีพิกัดเรา ให้ใช้กรุงเทพฯ)
        view_lat, view_lon = 13.75, 100.5
        if all_users and my_id in all_users:
            view_lat = all_users[my_id].get('lat', 13.75)
            view_lon = all_users[my_id].get('lon', 100.5)

        m = folium.Map(location=[view_lat, view_lon], zoom_start=16, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                       attr="Google Satellite")

        if all_users:
            for name, info in all_users.items():
                if isinstance(info, dict) and 'lat' in info and 'lon' in info:
                    color = 'blue' if name == my_id else 'red'
                    folium.Marker(
                        [info['lat'], info['lon']], 
                        popup=name,
                        tooltip=name,
                        icon=folium.Icon(color=color, icon='info-sign')
                    ).add_to(m)
        
        st_folium(m, width="100%", height=500, key="synapse_map")
    except Exception as e:
        st.error(f"Map Error: {e}")

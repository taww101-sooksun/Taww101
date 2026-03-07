import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time

# 1. ⚡ ล้างหน้าจอให้คมชัด
st.set_page_config(page_title="SYNAPSE CLEAR", layout="wide")

# 2. 🛰️ เชื่อมต่อ FIREBASE
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

st.title("🛰️ SYNAPSE COMMAND CENTER")

# 3. 🎵 บังคับเล่นเพลง (ยักษ์ในตัวฉัน)
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

# 4. 🚀 ระบบดึงพิกัดจริง (แก้จากอนุสาวรีย์ฯ เป็นตัวคุณ)
loc = get_geolocation()

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR"])

with tabs[0]:
    my_id = st.text_input("ระบุชื่อรหัสของคุณ:", value="Ta101")
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"📍 ตรวจพบตำแหน่งจริง: {lat}, {lon}")
        
        if st.button("🛰️ บันทึกพิกัดจริง"):
            db.reference(f'users/{my_id}').update({
                'lat': lat, 'lon': lon, 'last_update': time.time()
            })
            st.balloons()
    else:
        st.warning("🚨 กรุณากด 'อนุญาต' (Allow) การเข้าถึงตำแหน่งบนเบราว์เซอร์")

with tabs[1]:
    all_users = db.reference('users').get()
    
    # 💡 หัวใจสำคัญ: ถ้ามีพิกัดเรา ให้เปิดแผนที่ตรงที่เราอยู่เลย!
    view_lat, view_lon = 13.75, 100.5 # ค่าพื้นฐาน
    if all_users and my_id in all_users:
        view_lat = all_users[my_id].get('lat', 13.75)
        view_lon = all_users[my_id].get('lon', 100.5)

    m = folium.Map(location=[view_lat, view_lon], zoom_start=17, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for name, info in all_users.items():
            if 'lat' in info and 'lon' in info:
                # 🔵 ตัวคุณ | 🔴 คนอื่น
                color = 'blue' if name == my_id else 'red'
                folium.Marker([info['lat'], info['lon']], tooltip=name,
                              icon=folium.Icon(color=color, icon='star')).add_to(m)
        st_folium(m, width="100%", height=500)

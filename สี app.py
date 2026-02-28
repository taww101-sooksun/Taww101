import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import time
import pandas as pd

# 1. ตั้งค่าหน้าจอและล้างความมัว (Cache)
st.set_page_config(page_title="SYNAPSE QUANTUM", layout="wide")
if 'init' not in st.session_state:
    st.cache_data.clear()
    st.session_state.init = True

# 2. 🎵 ระบบเพลง (ยักษ์ในตัวฉัน) - วางไว้บนสุดให้กดง่าย
st.markdown("### 🎵 BATTLE RHYTHM")
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)

# 3. 🛰️ เชื่อมต่อ FIREBASE (ความจริงจาก Key ของคุณ)
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

# 4. จัดการ TAB ให้เป็นระเบียบ (แก้ NameError)
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "📊 DATA"])

# --- TAB 1: CORE (เน้นดึงพิกัดจริงจากเบราว์เซอร์) ---
with tabs[0]:
    st.subheader("🚀 เชื่อมต่อพิกัดจริง")
    my_name = st.text_input("ระบุชื่อรหัสของคุณ (ต้องตรงกับใน Firebase):", value="Agent_01")
    
    # ใช้ตัวดึงพิกัดที่มีความแม่นยำสูงขึ้น
    location = get_geolocation()
    
    if location:
        lat = location['coords']['latitude']
        lon = location['coords']['longitude']
        st.success(f"จับสัญญาณได้แล้ว: {lat}, {lon}")
        
        if st.button("🛰️ อัปเดตพิกัดจริงลงแผนที่"):
            db.reference(f'users/{my_name}').update({
                'lat': lat,
                'lon': lon,
                'last_update': time.time()
            })
            st.info("ส่งข้อมูลพิกัดจริงเข้าระบบแล้ว!")
    else:
        st.warning("⚠️ กรุณากด 'Allow' หรือ 'อนุญาต' ให้เข้าถึงตำแหน่งในเบราว์เซอร์ด้วยครับ")

# --- TAB 2: RADAR (แสดงผลแบบ Real-time) ---
with tabs[1]:
    st.subheader("🛰️ ระบบเรดาร์ตรวจจับพิกัดจริง")
    all_users = db.reference('users').get()
    
    # ถ้ามีพิกัดจริงของเรา ให้แผนที่ไปโผล่ตรงนั้นเลย ไม่ไปอนุสาวรีย์ฯ แล้ว
    current_lat, current_lon = 13.75, 100.5 # ค่าสำรอง
    if all_users and my_name in all_users:
        current_lat = all_users[my_name].get('lat', 13.75)
        current_lon = all_users[my_name].get('lon', 100.5)

    m = folium.Map(location=[current_lat, current_lon], zoom_start=16, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google")

    if all_users:
        for name, info in all_users.items():
            if 'lat' in info and 'lon' in info:
                # แยกสี: ตัวเราสีน้ำเงิน คนอื่นสีแดง
                is_me = (name == my_name)
                folium.Marker(
                    [info['lat'], info['lon']],
                    tooltip=f"{'ตัวคุณ' if is_me else name}",
                    icon=folium.Icon(color='blue' if is_me else 'red', icon='star' if is_me else 'user', prefix='fa')
                ).add_to(m)
        st_folium(m, width="100%", height=500)


# --- TAB 3: ข้อมูลดิบ (แบไต๋ความจริง) ---
with tabs[2]:
    st.subheader("📊 ตารางข้อมูลจาก Firebase")
    if all_users:
        st.dataframe(pd.DataFrame.from_dict(all_users, orient='index'))

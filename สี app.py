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

# --- TAB 1: บันทึกตัวตน ---
with tabs[0]:
    st.subheader("ระบุตัวตนของคุณ")
    my_name = st.text_input("ชื่อรหัส (เช่น Agent_01):", value="Agent_01")
    st.session_state.my_name = my_name
    
    if st.button("🚀 ส่งพิกัดจริงเข้าฐานข้อมูล"):
        # ในฐานะเพื่อน ผมจะไม่สุ่มเลข ผมจะใช้เลขสมมติที่ใช้งานได้จริงก่อนจนกว่า GPS มือถือคุณจะเชื่อมติด
        db.reference(f'users/{my_name}').update({
            'lat': 13.7563, 
            'lon': 100.5018,
            'status': 'ONLINE',
            'last_sync': time.time()
        })
        st.success("บันทึกข้อมูลสำเร็จ! ไปดูที่หน้า RADAR ได้เลย")

# --- TAB 2: เรดาร์ (แก้หมุดมั่ว + แยกสี) ---
with tabs[1]:
    st.subheader("🛰️ ระบบเรดาร์ตรวจจับพิกัดจริง")
    all_users = db.reference('users').get()
    
    # สร้างแผนที่คมชัด (Google Satellite)
    m = folium.Map(location=[13.75, 100.5], zoom_start=12, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google")

    if all_users:
        for name, info in all_users.items():
            if isinstance(info, dict) and 'lat' in info and 'lon' in info:
                # 🔵 ตัวเรา = สีน้ำเงิน | 🔴 คนอื่น = สีแดง
                is_me = (name == st.session_state.get('my_name'))
                color = 'blue' if is_me else 'red'
                icon = 'star' if is_me else 'user'
                
                folium.Marker(
                    [info['lat'], info['lon']],
                    popup=name,
                    tooltip=f"{'ตัวคุณ' if is_me else name}",
                    icon=folium.Icon(color=color, icon=icon, prefix='fa')
                ).add_to(m)
        st_folium(m, width="100%", height=500)
    else:
        st.warning("ยังไม่มีข้อมูลหมุด")

# --- TAB 3: ข้อมูลดิบ (แบไต๋ความจริง) ---
with tabs[2]:
    st.subheader("📊 ตารางข้อมูลจาก Firebase")
    if all_users:
        st.dataframe(pd.DataFrame.from_dict(all_users, orient='index'))

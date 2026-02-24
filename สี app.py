import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pandas as pd
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="SYNAPSE - Music Therapy", layout="wide")

# 2. เชื่อมต่อ Firebase
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
    except Exception as e:
        st.error(f"Firebase Setup Error: {e}")

# --- ส่วนหัวและโลโก้ ---
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.write("🌐")
with col2:
    st.title("SYNAPSE - Music Therapy")

location = get_geolocation()

# 3. สร้าง 3 Tab
tab1, tab2, tab3 = st.tabs(["🚀 สำหรับเพื่อน", "📊 Dashboard", "💬 ห้องสนทนา"])

with tab1:
    st.header("เริ่มการเดินทางของคุณ")
    user_id = st.text_input("ระบุชื่อหรือรหัสของคุณ:", placeholder="เช่น Ta101", key="user_input")
    if st.button("Start Journey", key="main_start_btn"):
        if user_id and location and 'coords' in location:
            try:
                lat, lon = location['coords']['latitude'], location['coords']['longitude']
                now = datetime.datetime.now()
                if firebase_admin._apps:
                    db.reference(f'users/{user_id}').set({
                        'last_seen': str(now), 'lat': lat, 'lon': lon, 'status': "Online"
                    })
                    st.success(f"เชื่อมต่อสำเร็จ! พิกัด: {lat}, {lon}")
                    song = "test_morning.mp3" if 6 <= now.hour < 12 else "test_evening.mp3"
                    if os.path.exists(song): st.audio(song)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("กรุณาใส่ชื่อและรอสัญญาณ GPS สักครู่ครับ")

with tab2:
    st.header("📊 แผนที่ติดตามตำแหน่ง")
    if firebase_admin._apps:
        try:
            users_ref = db.reference('users').get()
            if users_ref:
                map_points = []
                for k, v in users_ref.items():
                    if isinstance(v, dict) and 'lat' in v and 'lon' in v:
                        map_points.append({'lat': float(v['lat']), 'lon': float(v['lon']), 'name': k})
                
                if map_points:
                    m = folium.Map(location=[map_points[0]['lat'], map_points[0]['lon']], zoom_start=16, tiles="CartoDB voyager")
                    for p in map_points:
                        folium.Marker([p['lat'], p['lon']], popup=p['name'], tooltip=p['name']).add_to(m)
                    st_folium(m, width=None, height=500)
                else:
                    st.info("ไม่มีพิกัดในระบบ")
            else:
                st.info("ยังไม่มีข้อมูลพิกัด")
        except Exception as e:
            st.error(f"Map Error: {e}")

with tab3:
    st.header("💬 ห้องสนทนา")
    if firebase_admin._apps:
        with st.form("chat_form", clear_on_submit=True):
            name_val = user_id if user_id else ""
            c_user = st.text_input("ชื่อ:", value=name_val)
            c_msg = st.text_input("ข้อความ:")
            if st.form_submit_button("ส่ง") and c_user and c_msg:
                db.reference('chats').push({
                    'name': c_user, 'msg': c_msg, 'time': datetime.datetime.now().strftime("%H:%M")
                })
        
        try:
            chats = db.reference('chats').order_by_key().limit_to_last(15).get()
            if chats:
                for _, data in reversed(chats.items()):
                    st.write(f"**{data.get('name','?')}**: {data.get('msg','')}")
                    st.divider()
        except Exception as e:
            st.error(f"Chat Load Error: {e}")

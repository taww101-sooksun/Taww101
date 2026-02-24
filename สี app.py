import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# 1. เชื่อมต่อ Firebase
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
        st.error(f"Firebase Error: {e}")

# ฟังก์ชันคำนวณเวลาจากพิกัด Longitude (ความจริงทางภูมิศาสตร์)
def get_time_by_coords(lon):
    # คำนวณหา Offset จาก Longitude (15 องศา = 1 ชม.)
    offset = round(lon / 15)
    # ใช้เวลาสากล UTC แล้วบวกตามตำแหน่งจริงบนโลก
    actual_time = datetime.datetime.utcnow() + datetime.timedelta(hours=offset)
    return actual_time.strftime("%H:%M")

# --- ส่วนหัว ---
st.title("🌐 SYNAPSE - True Location Time")
location = get_geolocation()

tab1, tab2, tab3 = st.tabs(["🚀 เช็คอิน", "📊 แผนที่", "💬 แชท"])

with tab1:
    user_id = st.text_input("ชื่อของคุณ:", key="user_input")
    if st.button("Start Journey"):
        if user_id and location and 'coords' in location:
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
            # ดึงเวลาจากพิกัด ไม่ได้ดึงจากนาฬิกาเครื่อง!
            true_time = get_time_by_coords(lon)
            
            db.reference(f'users/{user_id}').set({
                'last_seen': true_time, 'lat': lat, 'lon': lon
            })
            st.success(f"บันทึกสำเร็จ! เวลาจริง ณ พิกัดนี้คือ: {true_time}")

with tab2:
    if firebase_admin._apps:
        users = db.reference('users').get()
        if users:
            map_points = [[v['lat'], v['lon']] for k, v in users.items() if 'lat' in v]
            m = folium.Map(location=map_points[0], zoom_start=15, 
                           tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google")
            for k, v in users.items():
                folium.Marker([v['lat'], v['lon']], popup=f"{k} ({v['last_seen']})").add_to(m)
            st_folium(m, width=700, height=500)

with tab3:
    with st.form("chat"):
        msg = st.text_input("ข้อความ:")
        if st.form_submit_button("ส่ง") and msg and user_id:
            # ใช้พิกัดปัจจุบันคำนวณเวลาแชท
            chat_time = get_time_by_coords(location['coords']['longitude']) if location else "--:--"
            db.reference('chats').push({'name': user_id, 'msg': msg, 'time': chat_time})
    
    chats = db.reference('chats').order_by_key().limit_to_last(10).get()
    if chats:
        for _, d in reversed(chats.items()):
            st.write(f"**{d.get('name')}** ({d.get('time')}): {d.get('msg')}")

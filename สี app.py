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
    offset = round(lon / 15)
    actual_time = datetime.datetime.utcnow() + datetime.timedelta(hours=offset)
    return actual_time.strftime("%H:%M")

# --- ส่วนหัวและโลโก้ ---
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=300)

tab1, tab2, tab3 = st.tabs(["🚀 เช็คอิน", "📊 แผนที่", "💬 แชท"])

with tab1:
    user_id = st.text_input("ชื่อของคุณ:", key="user_input")
    if st.button("Start Journey"):
        if user_id and location and 'coords' in location:
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
            true_time = get_time_by_coords(lon)
            
            if firebase_admin._apps:
                db.reference(f'users/{user_id}').set({
                    'last_seen': true_time, 'lat': lat, 'lon': lon
                })
                st.success(f"บันทึกสำเร็จ! เวลาจริง ณ พิกัดนี้คือ: {true_time}")
        else:
            st.warning("กรุณาใส่ชื่อและรอสัญญาณ GPS สักครู่")

with tab2:
    st.header("📊 แผนที่")
    if firebase_admin._apps:
        try:
            users = db.reference('users').get()
            if users:
                map_points = []
                # วนลูปเช็คข้อมูลก่อนวาดแผนที่ เพื่อป้องกัน KeyError
                valid_users = []
                for k, v in users.items():
                    if isinstance(v, dict) and 'lat' in v and 'lon' in v:
                        valid_users.append({'name': k, 'lat': v['lat'], 'lon': v['lon'], 'time': v.get('last_seen', '--:--')})
                
                if valid_users:
                    # สร้างแผนที่โดยยึดตำแหน่งคนแรกที่ข้อมูลครบ
                    m = folium.Map(location=[valid_users[0]['lat'], valid_users[0]['lon']], 
                                   zoom_start=15, 
                                   tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", 
                                   attr="Google")
                    
                    for u in valid_users:
                        folium.Marker([u['lat'], u['lon']], 
                                      popup=f"{u['name']} ({u['time']})",
                                      tooltip=u['name']).add_to(m)
                    
                    st_folium(m, width=700, height=500)
                else:
                    st.info("ยังไม่มีข้อมูลพิกัดที่สมบูรณ์ในระบบ")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการโหลดแผนที่: {e}")

with tab3:
    st.header("💬 แชท")
    with st.form("chat", clear_on_submit=True):
        msg = st.text_input("ข้อความ:")
        if st.form_submit_button("ส่ง") and msg and user_id:
            chat_time = "--:--"
            if location and 'coords' in location:
                chat_time = get_time_by_coords(location['coords']['longitude'])
            
            db.reference('chats').push({'name': user_id, 'msg': msg, 'time': chat_time})
    
    chats = db.reference('chats').order_by_key().limit_to_last(15).get()
    if chats:
        for _, d in reversed(chats.items()):
            name = d.get('name', 'Anonymous')
            m_text = d.get('msg', '')
            t_text = d.get('time', '--:--')
            if m_text:
                st.write(f"**{name}** ({t_text}): {m_text}")
                st.divider()

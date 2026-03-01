import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import pandas as pd
from streamlit_js_eval import get_geolocation

# 1. 🔑 ระบบตรวจสอบสิทธิ์ (Simple Auth)
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False

# 2. 🛡️ หน้า Login (Gateway)
if not st.session_state.auth_status:
    st.markdown('<div class="neon-header">SYNAPSE GATEWAY</div>', unsafe_allow_html=True)
    with st.container():
        st.info("🌐 ระบบเชื่อมต่อโครงข่ายทั่วโลก (Global Network)")
        user_input = st.text_input("กรุณาระบุรหัส AGENT ของคุณ:", placeholder="ตัวอย่าง: Ta101, Neo_01...")
        agent_color = st.color_picker("เลือกสีหมุดประจำตัวของคุณ:", "#00f2fe")
        
        if st.button("🔓 INITIATE LINK (เข้าสู่ระบบ)"):
            if user_input:
                st.session_state.user_id = user_input
                st.session_state.my_color = agent_color
                st.session_state.auth_status = True
                st.rerun()
            else:
                st.error("กรุณาระบุชื่อรหัสก่อนเข้าเครื่อง")
    st.stop() # หยุดการทำงานหน้าอื่นจนกว่าจะ Login

# ==========================================
# 3. เมื่อ Login ผ่านแล้ว (หน้าหลัก)
# ==========================================
user_id = st.session_state.user_id
my_color = st.session_state.my_color

# ส่วนหัวโปรแกรม (ใช้โค้ดเดิมที่เพื่อนมี)
st.sidebar.success(f"ONLINE: {user_id}")
st.sidebar.markdown(f"🎨 สีประจำตัว: <span style='color:{my_color};'>●</span>", unsafe_allow_html=True)

# 4. 🛰️ ส่งพิกัดอัตโนมัติ (ความจริงคือต้องรู้ว่าเขาอยู่ที่ไหน)
loc = get_geolocation()
if loc:
    db.reference(f'users/{user_id}').update({
        'lat': loc['coords']['latitude'], 
        'lon': loc['coords']['longitude'],
        'color': my_color,
        'last_sync': time.time(),
        'status': 'ACTIVE'
    })

# 5. 🗺️ แผนที่เรดาร์ (ดึงสีจากฐานข้อมูลมาโชว์)
# ใน Tab Radar ให้แก้ส่วนปักหมุดเป็นแบบนี้:
# folium.Marker(
#     location=[data['lat'], data['lon']], 
#     popup=u,
#     icon=folium.Icon(color='white', icon_color=data.get('color', '#red'), icon='user')
# ).add_to(m)

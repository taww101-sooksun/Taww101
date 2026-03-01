import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
from streamlit_folium import st_folium
import folium
from streamlit_js_eval import get_geolocation

# 1. 🖼️ ส่วนแสดงผล LOGO และสไตล์ (แก้ให้ดึง logo3.jpg)
st.set_page_config(page_title="COMMAND CENTER", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #00f2fe; }
    .neon-box { border: 2px solid #ff1744; border-radius: 10px; padding: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ดึงโลโก้ (เพื่อนต้องมีไฟล์ logo3.jpg ในโฟลเดอร์เดียวกับโค้ด หรือใช้ URL)
try:
    st.image("logo3.jpg", width=150) # ถ้าเป็นไฟล์ในเครื่อง
except:
    st.image("https://img.icons8.com/nolan/128/security-configuration.png", width=100) # สำรองถ้าหาไฟล์ไม่เจอ

st.title("SYNAPSE COMMAND")

# 2. 🎵 ระบบเพลง (ยักษ์ในตัวฉัน.mp3)
# ใช้ Link Google Drive เดิมที่เพื่อนเคยใช้ ซึ่งเสถียรที่สุด
music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.audio(music_url, format="audio/mpeg", loop=True)
st.caption("🎵 กำลังเล่น: ยักษ์ในตัวฉัน.mp3")

# 3. 📱 แยก TAB: โทรคอล / แชต / เรดาร์ / ข้อมูล
tabs = st.tabs(["🚀 CORE & CALL", "💬 CHAT", "🛰️ RADAR", "📊 10-UNITS"])

with tabs[0]: # 📞 โทรคอล
    st.subheader("UNIT: Ta101")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📞 CALL COMMAND", use_container_width=True):
            st.write("📞 กำลังต่อสายไปยังกองบัญชาการ...")
    with col2:
        if st.button("🚨 EMERGENCY", use_container_width=True):
            st.error("ส่งสัญญาณขอความช่วยเหลือแล้ว!")

with tabs[1]: # 💬 แชตแยก
    st.subheader("🗨️ PRIVATE COMMS")
    chat_msg = st.chat_input("ส่งข้อความถึง Agent คนอื่น...")
    if chat_msg:
        st.info(f"ส่งแล้ว: {chat_msg}")

with tabs[2]: # 🛰️ เรดาร์ (พิกัดตรง)
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
        folium.Marker([lat, lon], tooltip="Ta101", icon=folium.Icon(color='blue', icon='star')).add_to(m)
        st_folium(m, width="100%", height=400)
    else:
        st.warning("กรุณาเปิด GPS เพื่อระบุพิกัดที่ถูกต้อง")

with tabs[3]: # 📊 10-UNITS
    st.write("ตารางสถานะ Unit ทั้งหมด 1.1 - 1.10")
    # ดึงข้อมูลจาก Firebase มาโชว์ตรงนี้...

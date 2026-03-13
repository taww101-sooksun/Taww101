import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import datetime

# --- SETTING ---
st.set_page_config(page_title="SYNAPSE CORE", layout="wide")

# CSS แบบเรียบง่ายที่ใช้งานได้จริง ไม่บั๊ก
st.markdown("""
    <style>
    .main { background-color: #00050a; color: #00f2fe; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #00f2fe; color: black; font-weight: bold; }
    .status-box { border: 1px solid #00f2fe; padding: 10px; border-radius: 10px; background: rgba(0, 242, 254, 0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ SYNAPSE COMMAND CENTER")

# --- 1. ระบบเวลา (ทำได้จริง) ---
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**CURRENT TIME (BKK):** {datetime.datetime.now().strftime('%H:%M:%S')}")

# --- 2. ระบบ GPS (ต้องกดยอมรับใน Browser ถึงจะขึ้น) ---
with st.expander("📍 GPS LOCATOR", expanded=True):
    loc = get_geolocation()
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"พบพิกัดของคุณ: {lat}, {lon}")
    else:
        st.info("กรุณากด 'Allow' เพื่อแชร์พิกัด GPS ของคุณ")
        lat, lon = 13.7563, 100.5018  # ค่า Default (กรุงเทพ)

# --- 3. RADAR MAP (ใช้งานได้จริง) ---
st.subheader("🛰️ LIVE RADAR")
# สร้างแผนที่
m = folium.Map(location=[lat, lon], zoom_start=12)
# ปักหมุดตัวคุณเอง
folium.Marker(
    [lat, lon], 
    popup="YOUR POSITION", 
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(m)

# แสดงผลแผนที่
st_folium(m, width="100%", height=400)

# --- 4. SIMPLE CHAT (Local Session - ไม่ใช้ DB ให้วุ่นวาย) ---
st.subheader("💬 LOCAL COMMS")
if 'messages' not in st.session_state:
    st.session_state.messages = []

with st.form("chat_input"):
    user_msg = st.text_input("Enter Message:")
    submit = st.form_submit_button("SEND")
    
    if submit and user_msg:
        st.session_state.messages.append(user_msg)

for msg in st.session_state.messages[-5:]: # แสดง 5 ข้อความล่าสุด
    st.write(f"📌 {msg}")

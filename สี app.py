import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# --- 1. ตั้งค่าหน้าเว็บและดีไซน์ ---
st.set_page_config(page_title="SYNAPSE - Premium Control", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #0a2342 50%, #004e92 100%);
        color: #ffffff;
    }
    .status-box { 
        padding: 20px; border-radius: 15px; 
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(79, 172, 254, 0.3);
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%; border-radius: 30px;
        background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%);
        color: white; border: none; font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. เชื่อมต่อ Firebase ---
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
        st.error(f"Error: {e}")

# --- 3. ตรวจสอบพิกัด ---
location = get_geolocation()

# --- 4. ส่วนหัวและโลโก้ ---
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m: st.image("logo3.jpg", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE CONTROL</h1>", unsafe_allow_html=True)

# Dashboard สถานะ
st.markdown("<div class='status-box'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"🛰️ **GPS:** {'🟢 CONNECTED' if location else '🔴 SEARCHING...'}")
with c2: st.markdown("🎵 **MUSIC:** 🟢 ONLINE")
with c3: st.markdown(f"🔥 **DB:** {'🟢 SYNCED' if firebase_admin._apps else '🔴 ERROR'}")
st.markdown("</div>", unsafe_allow_html=True)

# --- 5. แท็บการใช้งาน ---
tab1, tab2, tab3 = st.tabs(["🚀 Experience", "📊 Global Map", "💬 Community"])

with tab1:
    user_display_name = st.text_input("👤 ระบุชื่อผู้ใช้:", placeholder="พิมพ์ชื่อของคุณที่นี่")
    if st.button("🚀 UPDATE MY STATUS"):
        if user_display_name and location:
            user_ref = db.reference(f'users/{user_display_name}')
            user_ref.set({
                'lat': location['coords']['latitude'],
                'lon': location['coords']['longitude'],
                'time': datetime.datetime.now().strftime("%H:%M")
            })
            st.success("บันทึกข้อมูลสำเร็จ!")
    st.markdown("---")
    playlist_id = "PL6S211

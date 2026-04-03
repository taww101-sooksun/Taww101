import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime

# ==========================================
# 0. CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

# --- ฟังก์ชันดึงเวลาตามพิกัดจริง ---
def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        if timezone_str:
            local_tz = pytz.timezone(timezone_str)
            return datetime.now(local_tz)
    except:
        pass
    return datetime.now(pytz.timezone('Asia/Bangkok'))

# ==========================================
# 1. CORE MODULES
# ==========================================

def room_core():
    st.subheader("🏠 CORE CONTROL")
    loc = get_geolocation()
    lat, lon = 13.7367, 100.5231 # Default กทม.
    if loc and 'coords' in loc:
        lat = loc['coords'].get('latitude', lat)
        lon = loc['coords'].get('longitude', lon)
    
    current_time = get_local_time(lat, lon)
    
    st.markdown(f"""
        <div style="text-align:center; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:15px; background:rgba(0,0,0,0.3);">
            <h1 style="font-size:5em; color:{st.session_state.theme_color}; margin:0;">
                {current_time.strftime('%H:%M:%S')}
            </h1>
            <p style="color:#888; font-family:monospace;">📍 LAT: {lat:.4f} | LON: {lon:.4f}</p>
            <p style="color:{st.session_state.theme_color};">SYSTEM ONLINE: Welcome AGENT {st.session_state.user}</p>
        </div>
    """, unsafe_allow_html=True)

def room_call():
    st.subheader("📞 SYNAPSE P2P CALL (Voice & Video)")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("เลือก AGENT ที่ต้องการโทรหา:", friends)
    
    if target:
        call_html = f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:1px solid {st.session_state.theme_color}; text-align:center;">
            <video id="remoteVideo" autoplay playsinline style="width:100%; height:300px; background:#000; border-radius:10px;"></video>
            <video id="localVideo" autoplay playsinline muted style="width:100px; position:absolute; bottom:30px; right:30px; border:2px solid {st.session_state.theme_color};"></video>
            <div style="margin-top:10px;">
                <button id="startCall" style="background:{st.session_state.theme_color}; color:black; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📞 เริ่มการโทร</button>
                <button onclick="location.reload()" style="background:#ff4444; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">❌ วางสาย</button>
            </div>
        </div>
        <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
        <script>
            const peer = new Peer('{st.session_state.user}');
            const localVideo = document.getElementById('localVideo');
            const remoteVideo = document.getElementById('remoteVideo');
            peer.on('call', call => {{
                navigator.mediaDevices.getUserMedia({{video: true, audio: true}}).then(stream => {{
                    localVideo.srcObject = stream;
                    call.answer(stream);
                    call.on('stream', remoteStream => {{ remoteVideo.srcObject = remoteStream; }});
                }});
            }});
            document.getElementById('startCall').onclick = () => {{
                navigator.mediaDevices.getUserMedia({{video: true, audio: true}}).then(stream => {{
                    localVideo.srcObject = stream;
                    const call = peer.call('{target}', stream);
                    call.on('stream', remoteStream => {{ remoteVideo.srcObject = remoteStream; }});
                }});
            }};
        </script>
        """
        components.html(call_html, height=450)

# (ฟังก์ชัน room_radar, room_music, room_secure_chat, room_login ใช้ตัวเดิมที่ต๊ะมีได้เลย)

# ==========================================
# 3. MAIN INTERFACE
# ==========================================
def main():
    init_system()
    
    with st.sidebar:
        if os.path.exists("logo1.jpg"):
            st.image("logo1.jpg", use_container_width=True)
        else:
            st.markdown(f"<h2 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE OS</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.session_state.logged_in:
            st.write(f"👤 AGENT: **{st.session_state.user}**")
            st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")
            if st.button("🚪 LOGOUT", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

    if not st.session_state.logged_in:
        room_login()
        return

    # เพิ่ม Tab "📞 CALL" เข้าไปตรงนี้ครับ
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", "🎧 MUSIC", "⚙️ SETTINGS"])
    
    with tabs[0]: room_core() # เรียกใช้ฟังก์ชันที่แก้เวลาแล้ว
    with tabs[1]: room_radar()
    with tabs[2]: room_secure_chat()
    with tabs[3]: room_call()   # ห้องโทรใหม่
    with tabs[4]: room_music()
    with tabs[5]: 
        st.session_state.theme_color = st.color_picker("ปรับสีธีมระบบ (Neon)", st.session_state.theme_color)

if __name__ == "__main__":
    main()
